"""Tests for batch formatting."""
from datetime import date
from decimal import Decimal

from lib.ncpdp.adapter import NcpdpClaimInput, build_transmission_dict
from lib.ncpdp.batch import BATCH_ROW_PREFIX, format_batch
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
