"""Tests for the NCPDP adapter layer."""
from datetime import date
from decimal import Decimal

import pytest

from lib.ncpdp.adapter import (
    BIG_HEALTH_PHARMACY_ID,
    BIG_HEALTH_NCPDP_CERTIFICATION_ID,
    NcpdpClaimInput,
    build_transmission_dict,
)
from lib.ncpdp import encoders


@pytest.fixture
def sample_input():
    return NcpdpClaimInput(
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


class TestNcpdpClaimInput:
    def test_valid_input(self, sample_input):
        assert sample_input.bin_number == "610511"
        assert sample_input.gender == "F"

    def test_defaults(self, sample_input):
        assert sample_input.days_supply == 365
        assert sample_input.quantity == 1

    def test_rejects_invalid_gender(self):
        with pytest.raises(Exception):
            NcpdpClaimInput(
                bin_number="610511",
                caremark_id="TEST123456",
                rx_group="RX0583",
                person_code="01",
                relationship_code="1",
                date_of_birth=date(1990, 5, 15),
                first_name="Jane",
                last_name="Doe",
                gender="Z",
                service_date=date(2024, 3, 1),
                reference_number=8001234,
                upc="60008003304",
                ingredient_cost=Decimal("400.00"),
                dispensing_fee=Decimal("0.15"),
                usual_and_customary_charge=Decimal("400.15"),
                gross_amount_due=Decimal("400.15"),
            )


class TestBuildTransmissionDict:
    def test_top_level_keys(self, sample_input):
        result = build_transmission_dict(sample_input)
        assert set(result.keys()) == {"header", "segments", "transactions"}

    def test_header(self, sample_input):
        result = build_transmission_dict(sample_input)
        header = result["header"]

        assert header["bin_number"] == 610511
        assert header["transaction_code"] == "B1"
        assert header["transaction_count"] == "1"
        assert header["processor_control_number"] == "RX0583"
        assert header["service_provider_id"] == BIG_HEALTH_PHARMACY_ID
        assert header["service_provider_id_qualifier"] == "01"
        assert header["software_vendor_certification_id"] == BIG_HEALTH_NCPDP_CERTIFICATION_ID
        assert header["date_of_service"] == 20240301

    def test_insurance_segment(self, sample_input):
        result = build_transmission_dict(sample_input)
        insurance = result["segments"][0]

        assert insurance["segment_identification"] == "04"
        assert insurance["cardholder_id"] == "TEST123456"
        assert insurance["group_id"] == "RX0583"
        assert insurance["person_code"] == "01"
        assert insurance["patient_relationship_code"] == 1

    def test_patient_segment(self, sample_input):
        result = build_transmission_dict(sample_input)
        patient = result["segments"][1]

        assert patient["segment_identification"] == "01"
        assert patient["date_of_birth"] == 19900515
        assert patient["patient_gender_code"] == 2  # F -> 2
        assert patient["patient_first_name"] == "Jane"
        assert patient["patient_last_name"] == "Doe"

    def test_claim_segment(self, sample_input):
        result = build_transmission_dict(sample_input)
        claim = result["transactions"][0]["segments"][0]

        assert claim["segment_identification"] == "07"
        assert claim["prescription_service_reference_number_qualifier"] == "1"
        assert claim["prescription_service_reference_number"] == 8001234
        assert claim["product_service_id_qualifier"] == "03"
        assert claim["product_service_id"] == "60008003304"
        assert claim["quantity_dispensed"] == 1000
        assert claim["fill_number"] == 0
        assert claim["days_supply"] == 365
        assert claim["compound_code"] == 1
        assert claim["daw_product_selection_code"] == "0"
        assert claim["date_prescription_written"] == 20240301
        assert claim["number_of_refills_authorized"] == 0
        assert claim["prescription_origin_code"] == 0
        assert claim["other_coverage_code"] == "0"

    def test_pricing_segment(self, sample_input):
        result = build_transmission_dict(sample_input)
        pricing = result["transactions"][0]["segments"][1]

        assert pricing["segment_identification"] == "11"
        assert pricing["ingredient_cost_submitted"] == Decimal("400.00")
        assert pricing["dispensing_fee_submitted"] == Decimal("0.15")
        assert pricing["usual_and_customary_charge"] == Decimal("400.15")
        assert pricing["gross_amount_due"] == Decimal("400.15")
        assert pricing["basis_of_cost_determination"] == "00"

    def test_gender_mapping(self):
        """All gender codes map to the correct NCPDP values."""
        base = dict(
            bin_number="610511",
            caremark_id="TEST",
            rx_group="RX",
            person_code="01",
            relationship_code="1",
            date_of_birth=date(1990, 1, 1),
            first_name="A",
            last_name="B",
            service_date=date(2024, 1, 1),
            reference_number=1,
            upc="123",
            ingredient_cost=Decimal("1"),
            dispensing_fee=Decimal("0"),
            usual_and_customary_charge=Decimal("1"),
            gross_amount_due=Decimal("1"),
        )
        for gender, expected_code in [("M", 1), ("F", 2), ("U", 3), ("X", 3)]:
            claim = NcpdpClaimInput(**{**base, "gender": gender})
            result = build_transmission_dict(claim)
            assert result["segments"][1]["patient_gender_code"] == expected_code

    def test_name_truncation(self):
        claim = NcpdpClaimInput(
            bin_number="610511",
            caremark_id="TEST",
            rx_group="RX",
            person_code="01",
            relationship_code="1",
            date_of_birth=date(1990, 1, 1),
            first_name="Bartholomew123456",  # 17 chars, should truncate to 12
            last_name="Wolfeschlegelstein",  # 18 chars, should truncate to 15
            gender="M",
            service_date=date(2024, 1, 1),
            reference_number=1,
            upc="123",
            ingredient_cost=Decimal("1"),
            dispensing_fee=Decimal("0"),
            usual_and_customary_charge=Decimal("1"),
            gross_amount_due=Decimal("1"),
        )
        result = build_transmission_dict(claim)
        assert len(result["segments"][1]["patient_first_name"]) == 12
        assert len(result["segments"][1]["patient_last_name"]) == 15

    def test_roundtrip_through_encoder(self, sample_input):
        """The transmission dict can be formatted by encoders.Transmission
        and parsed back without error.
        """
        tx_dict = build_transmission_dict(sample_input)
        encoded = encoders.Transmission.format(tx_dict)
        decoded = encoders.Transmission.parse(encoded)

        assert decoded["header"]["bin_number"] == 610511
        assert decoded["header"]["transaction_code"] == "B1"
        assert decoded["segments"][0]["cardholder_id"] == "TEST123456"
        assert decoded["transactions"][0]["segments"][0]["prescription_service_reference_number"] == 8001234
