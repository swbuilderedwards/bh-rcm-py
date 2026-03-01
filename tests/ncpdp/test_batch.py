"""Tests for batch formatting."""
import io
from datetime import date
from decimal import Decimal

from lib.ncpdp.adapter import NcpdpClaimInput, build_transmission_dict
from lib.ncpdp.batch import BATCH_ROW_PREFIX, format_batch, format_response_batch, parse_from
from lib.ncpdp import encoders


def _sample_claim(**overrides):
    defaults = dict(
        bin_number="610511",
        caremark_id="TEST123456",
        rx_group="RX0583",
        person_code="01",
        relationship_code="1",
        date_of_birth=date(1990, 5, 15),
        first_name="Jane",
        last_name="Doe",
        gender="F",
        service_date=date(2024, 3, 1),
        reference_number=8001234,
        upc="60008003304",
        ingredient_cost=Decimal("400.00"),
        dispensing_fee=Decimal("0.15"),
        usual_and_customary_charge=Decimal("400.15"),
        gross_amount_due=Decimal("400.15"),
    )
    defaults.update(overrides)
    return NcpdpClaimInput(**defaults)


class TestFormatBatch:
    def test_prefix_format(self):
        td = build_transmission_dict(_sample_claim())
        result = format_batch([td])
        line = result.split("\n")[0]
        assert line.startswith("\x02G1")
        assert line[3:13] == " " * 10

    def test_single_transmission(self):
        td = build_transmission_dict(_sample_claim())
        result = format_batch([td])
        lines = result.strip().split("\n")
        assert len(lines) == 1

    def test_multiple_transmissions(self):
        tds = [build_transmission_dict(_sample_claim()) for _ in range(3)]
        result = format_batch(tds)
        lines = result.strip().split("\n")
        assert len(lines) == 3

    def test_trailing_newline(self):
        td = build_transmission_dict(_sample_claim())
        result = format_batch([td])
        assert result.endswith("\n")

    def test_roundtrip(self):
        """adapter -> format_batch -> strip prefix -> Transmission.parse"""
        td = build_transmission_dict(_sample_claim())
        batch_output = format_batch([td])
        line = batch_output.strip().split("\n")[0]
        # Strip the 13-char prefix (\x02G1 + 10 spaces)
        raw_transmission = line[len(BATCH_ROW_PREFIX):]
        parsed = encoders.Transmission.parse(raw_transmission)
        assert parsed["header"]["bin_number"] == 610511
        assert parsed["header"]["transaction_code"] == "B1"
        assert parsed["segments"][0]["cardholder_id"] == "TEST123456"


class TestFormatResponseBatch:
    def _sample_response_dict(self):
        return {
            "header": {
                "transaction_code": "B1",
                "transaction_count": "1",
                "header_response_status": "A",
                "service_provider_id_qualifier": "01",
                "service_provider_id": "1316418981",
                "date_of_service": 20240301,
            },
            "segments": [
                {
                    "segment_identification": "21",
                    "transaction_response_status": "P",
                },
                {
                    "segment_identification": "22",
                    "prescription_service_reference_number_qualifier": "1",
                    "prescription_service_reference_number": 8001234,
                },
            ],
            "transactions": [],
        }

    def test_starts_with_header(self):
        result = format_response_batch([self._sample_response_dict()])
        assert result.startswith("   R")

    def test_ends_with_trailer(self):
        result = format_response_batch([self._sample_response_dict()])
        lines = result.strip().split("\n")
        assert lines[-1] == "0000000000"

    def test_response_lines_start_with_d0(self):
        result = format_response_batch([self._sample_response_dict()])
        lines = result.strip().split("\n")
        # Line 0 is header, line -1 is trailer, middle lines are transmissions
        assert lines[1].startswith("D0")

    def test_roundtrip_through_parse_from(self):
        """format_response_batch → parse_from roundtrip."""
        rd = self._sample_response_dict()
        text = format_response_batch([rd])
        filestream = io.BytesIO(text.encode("utf-8"))
        results = list(parse_from(filestream))
        assert len(results) == 1
        assert results[0]["header"]["transaction_code"] == "B1"
        assert results[0]["header"]["header_response_status"] == "A"

    def test_multiple_responses_roundtrip(self):
        rds = [self._sample_response_dict() for _ in range(3)]
        text = format_response_batch(rds)
        filestream = io.BytesIO(text.encode("utf-8"))
        results = list(parse_from(filestream))
        assert len(results) == 3

    def test_ref_number_preserved(self):
        rd = self._sample_response_dict()
        text = format_response_batch([rd])
        filestream = io.BytesIO(text.encode("utf-8"))
        results = list(parse_from(filestream))
        all_segs = results[0].get("segments", [])
        for tx in results[0].get("transactions", []):
            all_segs.extend(tx.get("segments", []))
        seg22 = [s for s in all_segs if s.get("segment_identification") == "22"]
        assert len(seg22) == 1
        assert seg22[0]["prescription_service_reference_number"] == 8001234
