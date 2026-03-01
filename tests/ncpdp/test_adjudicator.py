"""Tests for the CVS PBM Stub adjudicator."""
import io

from lib.ncpdp import batch, encoders
from lib.ncpdp.adapter import NcpdpClaimInput, build_transmission_dict
from lib.ncpdp.adjudicator import adjudicate_batch, adjudicate_transmission

SAMPLE_CLAIM = NcpdpClaimInput(
    bin_number="610511",
    caremark_id="TEST123456",
    rx_group="RX0583",
    person_code="01",
    relationship_code="1",
    date_of_birth="1990-05-15",
    first_name="Jane",
    last_name="Doe",
    gender="F",
    service_date="2024-03-01",
    reference_number=8001234,
    upc="60008003304",
    ingredient_cost="400.00",
    dispensing_fee="0.15",
    usual_and_customary_charge="400.15",
    gross_amount_due="400.15",
)


def _make_request_td():
    return build_transmission_dict(SAMPLE_CLAIM)


class TestAdjudicateTransmission:
    def test_returns_response_header(self):
        td = _make_request_td()
        result = adjudicate_transmission(td)
        header = result["header"]
        assert header["transaction_code"] == "B1"
        assert header["header_response_status"] == "A"
        assert header["service_provider_id"] == "1316418981"

    def test_echoes_date_of_service(self):
        td = _make_request_td()
        result = adjudicate_transmission(td)
        assert result["header"]["date_of_service"] == td["header"]["date_of_service"]

    def test_has_response_status_segment(self):
        td = _make_request_td()
        result = adjudicate_transmission(td)
        seg21 = [s for s in result["segments"] if s["segment_identification"] == "21"]
        assert len(seg21) == 1
        assert seg21[0]["transaction_response_status"] in ("P", "R")

    def test_has_claim_segment_with_ref_number(self):
        td = _make_request_td()
        result = adjudicate_transmission(td)
        seg22 = [s for s in result["segments"] if s["segment_identification"] == "22"]
        assert len(seg22) == 1
        assert seg22[0]["prescription_service_reference_number"] == 8001234

    def test_rejected_has_reject_code(self):
        td = _make_request_td()
        # Run enough times to get a rejection
        for _ in range(100):
            result = adjudicate_transmission(td)
            seg21 = [s for s in result["segments"] if s["segment_identification"] == "21"][0]
            if seg21["transaction_response_status"] == "R":
                assert "reject_code" in seg21
                assert seg21["reject_count"] == "1"
                return
        raise AssertionError("Expected at least one rejection in 100 tries")

    def test_paid_has_pricing_segment(self):
        td = _make_request_td()
        for _ in range(100):
            result = adjudicate_transmission(td)
            seg21 = [s for s in result["segments"] if s["segment_identification"] == "21"][0]
            if seg21["transaction_response_status"] == "P":
                seg23 = [s for s in result["segments"] if s["segment_identification"] == "23"]
                assert len(seg23) == 1
                return
        raise AssertionError("Expected at least one paid in 100 tries")

    def test_response_can_be_formatted(self):
        """The response dict can be passed to Transmission.format() without error."""
        td = _make_request_td()
        result = adjudicate_transmission(td)
        encoded = encoders.Transmission.format(result, enforce_types=False)
        assert encoded.startswith("D0")


class TestAdjudicateBatch:
    def test_roundtrip_single_claim(self):
        """Encode → adjudicate → parse roundtrip."""
        td = build_transmission_dict(SAMPLE_CLAIM)
        batch_text = batch.format_batch([td])
        response_text = adjudicate_batch(batch_text)

        # Parse the response
        filestream = io.BytesIO(response_text.encode("utf-8"))
        responses = list(batch.parse_from(filestream))
        assert len(responses) == 1

    def test_roundtrip_multiple_claims(self):
        tds = [build_transmission_dict(SAMPLE_CLAIM) for _ in range(3)]
        batch_text = batch.format_batch(tds)
        response_text = adjudicate_batch(batch_text)

        filestream = io.BytesIO(response_text.encode("utf-8"))
        responses = list(batch.parse_from(filestream))
        assert len(responses) == 3

    def test_responses_have_correct_structure(self):
        td = build_transmission_dict(SAMPLE_CLAIM)
        batch_text = batch.format_batch([td])
        response_text = adjudicate_batch(batch_text)

        filestream = io.BytesIO(response_text.encode("utf-8"))
        responses = list(batch.parse_from(filestream))
        resp = responses[0]

        assert "header" in resp
        assert resp["header"]["transaction_code"] == "B1"
        assert resp["header"]["header_response_status"] == "A"

    def test_ref_number_preserved_through_roundtrip(self):
        td = build_transmission_dict(SAMPLE_CLAIM)
        batch_text = batch.format_batch([td])
        response_text = adjudicate_batch(batch_text)

        filestream = io.BytesIO(response_text.encode("utf-8"))
        responses = list(batch.parse_from(filestream))

        # Find segment 22 in first transaction's segments or top-level segments
        all_segments = responses[0].get("segments", [])
        for tx in responses[0].get("transactions", []):
            all_segments.extend(tx.get("segments", []))

        seg22 = [s for s in all_segments if s.get("segment_identification") == "22"]
        assert len(seg22) == 1
        assert seg22[0]["prescription_service_reference_number"] == 8001234
