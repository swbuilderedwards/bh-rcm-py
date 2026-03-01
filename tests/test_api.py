"""Tests for the NCPDP API endpoints."""
import pathlib

from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)

SAMPLE_CLAIM = {
    "bin_number": "610511",
    "caremark_id": "TEST123456",
    "rx_group": "RX0583",
    "person_code": "01",
    "relationship_code": "1",
    "date_of_birth": "1990-05-15",
    "first_name": "Jane",
    "last_name": "Doe",
    "gender": "F",
    "service_date": "2024-03-01",
    "reference_number": 8001234,
    "upc": "60008003304",
    "ingredient_cost": "400.00",
    "dispensing_fee": "0.15",
    "usual_and_customary_charge": "400.15",
    "gross_amount_due": "400.15",
}

BATCH_RESPONSE_PATH = pathlib.Path("tests/ncpdp/data/batch_response.ncpdp")


class TestEncodeEndpoint:
    def test_encode_single_claim(self):
        resp = client.post("/api/claims/ncpdp/encode", json=SAMPLE_CLAIM)
        assert resp.status_code == 200
        data = resp.json()
        assert "encoded" in data
        assert data["encoded"].startswith("610511")

    def test_encode_rejects_invalid_input(self):
        resp = client.post("/api/claims/ncpdp/encode", json={"bin_number": "610511"})
        assert resp.status_code == 422


class TestBatchEndpoint:
    def test_batch_single_claim(self):
        resp = client.post("/api/claims/ncpdp/batch", json=[SAMPLE_CLAIM])
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/plain; charset=utf-8"
        assert resp.text.startswith("\x02G1")

    def test_batch_multiple_claims(self):
        resp = client.post("/api/claims/ncpdp/batch", json=[SAMPLE_CLAIM, SAMPLE_CLAIM, SAMPLE_CLAIM])
        assert resp.status_code == 200
        lines = resp.text.strip().split("\n")
        assert len(lines) == 3

    def test_batch_empty_list(self):
        resp = client.post("/api/claims/ncpdp/batch", json=[])
        assert resp.status_code == 200
        assert resp.text == "\n"


class TestParseResponseEndpoint:
    def test_parse_response_file(self):
        with open(BATCH_RESPONSE_PATH, "rb") as f:
            resp = client.post("/api/claims/ncpdp/parse-response", files={"file": ("batch_response.ncpdp", f)})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["transmissions"]) == 2

    def test_parse_response_structure(self):
        with open(BATCH_RESPONSE_PATH, "rb") as f:
            resp = client.post("/api/claims/ncpdp/parse-response", files={"file": ("batch_response.ncpdp", f)})
        tx = resp.json()["transmissions"][0]
        assert "header" in tx
        assert "segments" in tx
        assert "transactions" in tx

    def test_parse_response_invalid_file(self):
        resp = client.post(
            "/api/claims/ncpdp/parse-response",
            files={"file": ("bad.txt", b"this is not a valid ncpdp file")},
        )
        assert resp.status_code == 400


class TestStubAdjudicateEndpoint:
    def _get_batch_text(self):
        resp = client.post("/api/claims/ncpdp/batch", json=[SAMPLE_CLAIM])
        assert resp.status_code == 200
        return resp.text

    def test_adjudicate_returns_plain_text(self):
        batch_text = self._get_batch_text()
        resp = client.post(
            "/api/claims/ncpdp/stub-adjudicate",
            content=batch_text.encode("utf-8"),
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/plain; charset=utf-8"

    def test_adjudicate_response_is_parseable(self):
        batch_text = self._get_batch_text()
        resp = client.post(
            "/api/claims/ncpdp/stub-adjudicate",
            content=batch_text.encode("utf-8"),
        )
        # The response should be parseable by parse-response-text
        parse_resp = client.post(
            "/api/claims/ncpdp/parse-response-text",
            content=resp.text.encode("utf-8"),
        )
        assert parse_resp.status_code == 200
        data = parse_resp.json()
        assert len(data["transmissions"]) == 1

    def test_full_pipeline_roundtrip(self):
        """encode → adjudicate → parse roundtrip via API."""
        # Step 1: Encode batch
        batch_resp = client.post("/api/claims/ncpdp/batch", json=[SAMPLE_CLAIM, SAMPLE_CLAIM])
        assert batch_resp.status_code == 200

        # Step 2: Adjudicate
        adj_resp = client.post(
            "/api/claims/ncpdp/stub-adjudicate",
            content=batch_resp.text.encode("utf-8"),
        )
        assert adj_resp.status_code == 200

        # Step 3: Parse response
        parse_resp = client.post(
            "/api/claims/ncpdp/parse-response-text",
            content=adj_resp.text.encode("utf-8"),
        )
        assert parse_resp.status_code == 200
        data = parse_resp.json()
        assert len(data["transmissions"]) == 2


class TestParseResponseTextEndpoint:
    def test_parse_response_text(self):
        with open(BATCH_RESPONSE_PATH, "rb") as f:
            content = f.read()
        resp = client.post(
            "/api/claims/ncpdp/parse-response-text",
            content=content,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["transmissions"]) == 2

    def test_parse_response_text_structure(self):
        with open(BATCH_RESPONSE_PATH, "rb") as f:
            content = f.read()
        resp = client.post(
            "/api/claims/ncpdp/parse-response-text",
            content=content,
        )
        tx = resp.json()["transmissions"][0]
        assert "header" in tx
        assert "segments" in tx
        assert "transactions" in tx

    def test_parse_response_text_invalid(self):
        resp = client.post(
            "/api/claims/ncpdp/parse-response-text",
            content=b"this is not valid ncpdp",
        )
        assert resp.status_code == 400
