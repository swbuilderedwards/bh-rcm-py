"""Tests for the NCPDP encoders module."""
from decimal import Decimal

import pytest

from lib.ncpdp import encoders


class TestDollar:
    @pytest.mark.parametrize(
        "argument,expected",
        [(0, "0{"), (-2.5, "25}"), (99.95, "999E"), (400.00, "4000{"), (Decimal("-13.37"), "133P"), (Decimal("0"), "0{"), (Decimal("-0"), "0{")],
    )
    def test_dollar_format(self, argument, expected):
        assert encoders.Dollar.format(argument) == expected

    @pytest.mark.parametrize(
        "argument,exception", [(None, TypeError), ("", TypeError), ("bob", TypeError), ([2], TypeError), (float("+Inf"), OverflowError)],
    )
    def test_dollar_format_failures(self, argument, exception):
        with pytest.raises(exception):
            encoders.Dollar.format(argument)

    @pytest.mark.parametrize(
        "argument,expected",
        [
            ("0{", Decimal("0")),
            ("25}", Decimal("-2.5")),
            ("999E", Decimal("99.95")),
            ("4000{", Decimal("400.00")),
            # TODO(danver): Can they possibly send the empty string?
        ],
    )
    def test_dollar_parse(self, argument, expected):
        assert encoders.Dollar.parse(argument) == expected

    @pytest.mark.parametrize(
        "argument,exception", [("bob", ValueError), ("2.2", ValueError), ("", ValueError)],
    )
    def test_dollar_parse_failures(self, argument, exception):
        with pytest.raises(exception):
            encoders.Dollar.parse(argument)


class TestNumeric:
    @pytest.mark.parametrize("argument,expected", [(0, "0"), (2, "2"), (1234, "1234"), (400, "400")])
    def test_numeric_format(self, argument, expected):
        assert encoders.Numeric.format(argument) == expected

    @pytest.mark.parametrize(
        "argument,exception", [(None, TypeError), ("", TypeError), ("bob", TypeError), ([2], TypeError), (float("+Inf"), TypeError)],
    )
    def test_numeric_format_failures(self, argument, exception):
        with pytest.raises(exception):
            encoders.Numeric.format(argument)

    @pytest.mark.parametrize(
        "argument,expected",
        [
            ("", 0),
            ("0", 0),
            ("20", 20),
            ("00100", 100),
            ("400", 400),
            # Undefinded behaviour. These should never occur in the input. Their
            # output is not guaranteed.
            # 2.0
            # -2
        ],
    )
    def test_numeric_parse(self, argument, expected):
        assert encoders.Numeric.parse(argument) == expected

    @pytest.mark.parametrize("argument,exception", [("bob", ValueError), ("2.2", ValueError)])
    def test_numeric_parse_failures(self, argument, exception):
        with pytest.raises(exception):
            encoders.Numeric.parse(argument)


class TestAlphanumeric:
    @pytest.mark.parametrize(
        "argument,expected",
        [("", ""), ("0", "0"), ("0 ", "0"), (" ", ""), ("abcd", "ABCD"), ("~\"'0a2 B ", "~\"'0A2 B"), (" leading space_", " LEADING SPACE_")],
    )
    def test_alphanumeric_format(self, argument, expected):
        assert encoders.Alphanumeric.format(argument) == expected

    @pytest.mark.parametrize(
        "argument,exception",
        [
            (None, TypeError),
            (2, TypeError),
            (float("+Inf"), TypeError),
            ([2], TypeError),
            ("\xa5", ValueError),
            ("\xa0NonBreakingSpaces\xa0", ValueError),
        ],
    )
    def test_alphanumeric_format_failures(self, argument, exception):
        with pytest.raises(exception):
            encoders.Alphanumeric.format(argument)

    @pytest.mark.parametrize(
        "argument,expected", [("", ""), ("ABCD", "ABCD"), ("2@#23!A", "2@#23!A"), ("A   ", "A")],
    )
    def test_alphanumeric_parse(self, argument, expected):
        assert encoders.Alphanumeric.parse(argument) == expected

    @pytest.mark.parametrize("argument,exception", [(0, TypeError), (None, TypeError), ([], TypeError)])
    def test_alphanumeric_parse_failures(self, argument, exception):
        with pytest.raises(exception):
            encoders.Alphanumeric.parse(argument)


class TestEnsureWidth:
    @pytest.mark.parametrize(
        "arguments,expected",
        [
            (("", " ", 5, True), "     "),
            (("", " ", 5, False), "     "),
            ((" ", " ", 5, False), "     "),
            (("abcd", " ", 5, True), "abcd "),
            (("abcd", " ", 5, False), " abcd"),
            (("0234", "0", 5, False), "00234"),
            (("0123456789", "0", None, False), "0123456789"),
        ],
    )
    def test_ensure_width(self, arguments, expected):
        assert encoders.ensure_width(*arguments) == expected

    @pytest.mark.parametrize(
        "arguments,exception", [(("1234567", " ", 0, False), ValueError), (("1234567", "", 7, False), ValueError)],
    )
    def test_ensure_width_raises(self, arguments, exception):
        with pytest.raises(exception):
            encoders.ensure_width(*arguments)


class TestRequestHeader:

    SPECIMEN_B1_HEADER_OBJECT = encoders.RequestHeader(
        bin_number=4336,
        transaction_code="B1",
        processor_control_number="TIMKB1",
        transaction_count="1",
        service_provider_id_qualifier="01",
        service_provider_id="1881706737",
        date_of_service=20190311,
        software_vendor_certification_id="D022000018",
    )

    SPECIMEN_B1_HEADER_STRING = "004336D0B1TIMKB1    1011881706737     20190311D022000018"

    def test_header_format(self):
        header = self.SPECIMEN_B1_HEADER_OBJECT.format()

        assert len(header) == 56
        assert header == self.SPECIMEN_B1_HEADER_STRING

    def test_header_parse(self):
        assert encoders.RequestHeader.parse(self.SPECIMEN_B1_HEADER_STRING) == self.SPECIMEN_B1_HEADER_OBJECT


class TestResponseHeader:

    SPECIMEN_B1_HEADER_OBJECT = encoders.ResponseHeader(
        transaction_code="B1",
        header_response_status="A",
        transaction_count="1",
        service_provider_id_qualifier="01",
        service_provider_id="4563663111",
        date_of_service=20070915,
    )

    SPECIMEN_B1_HEADER_STRING = "D0B11A014563663111     20070915"

    def test_header_format(self):
        header = self.SPECIMEN_B1_HEADER_OBJECT.format()

        assert len(header) == 31
        assert header == self.SPECIMEN_B1_HEADER_STRING

    def test_header_parse(self):
        assert encoders.ResponseHeader.parse(self.SPECIMEN_B1_HEADER_STRING) == self.SPECIMEN_B1_HEADER_OBJECT


class TestPatientSegment:
    @pytest.fixture
    def instance(self):
        return encoders.PatientSegment(
            date_of_birth=20190120,
            patient_first_name="Bob",
            patient_gender_code=1,
            patient_last_name="D'Builder",
            patient_street_address="101 Spring Ln",
            patient_city_address="Bobsville",
            patient_state_province_address="IL",
            patient_zip_postal_zone="23451",
            patient_phone_number=5555555,
            patient_e_mail_address="abcd@gdef.com",
        )

    @pytest.fixture
    def formatted(self):
        return (
            """\x1e\x1cAM01\x1cC420190120\x1cC51\x1cCABOB\x1cCBD'BUILDER"""
            + """\x1cCM101 SPRING LN\x1cCNBOBSVILLE\x1cCOIL\x1cCP23451\x1cCQ5555555\x1cHNABCD@GDEF.COM"""
        )

    def test_format(self, instance, formatted):
        assert instance.format() == formatted

    def test_parse(self, instance, formatted):
        golden_instance = encoders.PatientSegment(
            date_of_birth=20190120,
            patient_gender_code=1,
            patient_first_name="BOB",
            patient_last_name="D'BUILDER",
            patient_street_address="101 SPRING LN",
            patient_city_address="BOBSVILLE",
            patient_state_province_address="IL",
            patient_zip_postal_zone="23451",
            patient_phone_number=5555555,
            patient_e_mail_address="ABCD@GDEF.COM",
            place_of_service=None,
        )
        assert encoders.PatientSegment.parse(formatted) == golden_instance


class TestInsuranceSegment:
    @pytest.fixture
    def instance(self):
        return encoders.InsuranceSegment(cardholder_id="987654321", group_id="1234", person_code="123", patient_relationship_code=1,)

    def test_format(self, instance):
        assert instance.format() == """\x1e\x1cAM04\x1cC2987654321\x1cC11234\x1cC3123\x1cC61"""

    def test_format_optional(self):
        assert encoders.InsuranceSegment("987654321").format() == """\x1e\x1cAM04\x1cC2987654321"""

    def test_parse_optional(self):
        assert encoders.InsuranceSegment.parse("""\x1e\x1cAM04\x1cC2987654321""") == encoders.InsuranceSegment("987654321")


class TestClaimSegment:
    @pytest.fixture
    def instance(self):
        return encoders.ClaimSegment(
            prescription_service_reference_number_qualifier="1",
            prescription_service_reference_number=800082,
            product_service_id_qualifier="01",
            product_service_id="upc-for-sleepio",
            fill_number=0,
            days_supply=365,
            quantity_dispensed=1,
            daw_product_selection_code="0",
            date_prescription_written=20190829,
            compound_code=1,
            prescription_origin_code=0,
            number_of_refills_authorized=0,
            other_coverage_code="0",
            level_of_service="00",
        )

    def test_format(self, instance):
        assert instance.format() == (
            """\x1e\x1cAM07\x1cEM1\x1cD2800082\x1cE101\x1cD7UPC-FOR-SLEEPIO\x1cE71"""
            + """\x1cD300\x1cD5365\x1cD61\x1cD80\x1cDE20190829\x1cDF00\x1cDI00\x1cDJ0\x1cC80"""
        )


class TestPricingSegment:
    @pytest.fixture
    def instance(self):
        return encoders.PricingSegment(400, 20, gross_amount_due=420)

    def test_format(self, instance):
        assert instance.format() == """\x1e\x1cAM11\x1cD94000{\x1cDC200{\x1cDU4200{"""

    def test_to_dict(self, instance):
        assert instance.to_dict() == {
            "dispensing_fee_submitted": 20,
            "gross_amount_due": 420,
            "ingredient_cost_submitted": 400,
            "segment_identification": "11",
        }


class TestPrescriberSegment:
    @pytest.fixture
    def instance(self):
        return encoders.PrescriberSegment(prescriber_id_qualifier="ab", prescriber_id="123456", primary_care_provider_id_qualifier="CA",)

    def test_format(self, instance):
        assert instance.format() == "\x1e\x1cAM03\x1cEZAB\x1cDB123456\x1c2ECA"


class TestResponseClaimSegment:
    def test_select_from_transmission_dict(self):
        assert encoders.ResponseClaimSegment.select_from_transmission_dict(
            {
                "header": {
                    "date_of_service": 20190920,
                    "header_response_status": "A",
                    "service_provider_id": "1316418981",
                    "service_provider_id_qualifier": "01",
                    "transaction_code": "B1",
                    "transaction_count": "1",
                },
                "segments": [{"group_id": "RX0583", "segment_identification": "25"}],
                "transactions": [
                    {
                        "segments": [
                            {
                                "additional_message_information": "NON-SPECIALTY DRUG",
                                "additional_message_information_count": 1,
                                "additional_message_information_qualifier": "01",
                                "authorization_number": 192632163817002999,
                                "segment_identification": "21",
                                "transaction_response_status": "P",
                            },
                            {
                                "prescription_service_reference_number": 323049609982,
                                "prescription_service_reference_number_qualifier": "1",
                                "segment_identification": "22",
                            },
                            {
                                "basis_of_reimbursement_determination": 3,
                                "dispensing_fee_paid": Decimal("0.00"),
                                "ingredient_cost_paid": Decimal("0.32"),
                                "patient_pay_amount": Decimal("0.00"),
                                "segment_identification": "23",
                                "total_amount_paid": Decimal("0.32"),
                            },
                        ]
                    }
                ],
            }
        ) == {
            "prescription_service_reference_number": 323049609982,
            "prescription_service_reference_number_qualifier": "1",
            "segment_identification": "22",
        }


class TestCompoundSegment:
    @pytest.fixture
    def instance(self):
        return encoders.CompoundSegment(
            compound_dispensing_unit_form_indicator=3,
            compound_dosage_form_description_code="11",
            compound_ingredient_component_count=3,
            ingredients=[
                {
                    "compound_product_id": "11845013901",
                    "compound_ingredient_quantity": 12,
                    "compound_ingredient_drug_cost": Decimal("1.2"),
                    "compound_ingredient_basis_of_cost_determination": "01",
                    "compound_product_id_qualifier": 3,
                },
                {
                    "compound_product_id_qualifier": 3,
                    "compound_product_id": "00603148049",
                    "compound_ingredient_quantity": 12,
                    "compound_ingredient_drug_cost": Decimal("8.4"),
                    "compound_ingredient_basis_of_cost_determination": "01",
                },
                {
                    "compound_product_id_qualifier": 3,
                    "compound_product_id": "60809031055",
                    "compound_ingredient_quantity": 24,
                    "compound_ingredient_drug_cost": Decimal("4.6"),
                    "compound_ingredient_basis_of_cost_determination": "01",
                },
            ],
            modifier_codes={"compound_ingredient_modifier_code_count": 1, "compound_ingredient_modifier_code": "A"},
        )

    def test_format(self, instance):
        assert (
            instance.format()
            == "\x1E\x1CAM10\x1CEF11\x1CEG3\x1CEC03\x1CRE03\x1CTE11845013901\x1CED12000\x1CEE12{\x1CUE01\x1CRE03\x1CTE00603148049\x1CED12000\x1CEE84{\x1CUE01\x1CRE03\x1CTE60809031055\x1CED24000\x1CEE46{\x1CUE01\x1C2G01\x1C2HA"  # noqa: E501
        )


class TestCOBOtherPaymentSegment:
    @pytest.fixture
    def instance(self):
        return encoders.COBOtherPaymentSegment(
            **{
                "segment_identification": "05",
                "coordination_of_benefits_other_payments_count": 1,
                "other_payments": [
                    {
                        "other_payer_patient_responsibility_amount_count": 1,
                        "other_payer_patient_responsibility_amounts": [
                            {
                                "other_payer_patient_responsibility_amount_qualifier": "12",
                                "other_payer_patient_responsibility_amount": Decimal("71.14"),
                            }
                        ],
                        "other_payer_coverage_type": "01",
                        "other_payer_date": "20191026",
                        "other_payer_id": "447225",
                        "other_payer_id_qualifier": "03",
                        "benefit_stages": {"benefit_stage_count": 1, "benefit_stage_amount": Decimal("76.50"), "benefit_stage_qualifier": "03"},
                    }
                ],
            }
        )

    def test_format(self, instance):
        assert (
            instance.format()
            == "\x1e\x1cAM05\x1c4C1\x1c5C01\x1c6C03\x1c7C447225\x1cE820191026\x1cNR1\x1cNP12\x1cNQ711D\x1cMU1\x1cMV03\x1cMW765{"
            # noqa: E501
        )


class TestResponseDURPPSSegment:
    def test_parse(self):
        golden_instance = encoders.ResponseDURPPSSegment(
            dur_pps_response_code_counter=1,
            reason_for_service_code="ID",
            clinical_significance_code=2,
            other_pharmacy_indicator=1,
            previous_date_of_fill="20210323",
            quantity_of_previous_fill="0000001000",
            database_indicator="4",
            other_prescriber_indicator="0",
            dur_free_text_message="SLEEPIO      MIS",
            dur_additional_text=None,
        )
        assert (
            golden_instance
            == encoders.ResponseDURPPSSegment.parse(
                "\x1e\x1cAM24\x1cJ61\x1cE4ID\x1cFS2\x1cFT1\x1cFU20210323\x1cFV0000001000\x1cFW4\x1cFX0\x1cFYSLEEPIO      MIS"
            )
            # noqa: E501
        )


class TestResponseCOBSegment:
    def test_parse(self):
        golden_instance = encoders.ResponseCOBSegment(
            segment_identification="28",
            other_payer_id_count=1,
            other_payer_coverage_type="",
            other_payer_id_qualifier=3,
            other_payer_processor_control_number="MEDJUMBO",
            other_payer_cardholder_id="XYZABCD",
            other_payer_group_id="RXAMCY",
            other_payer_help_desk_phone_number="0000000000",
        )

        assert golden_instance == encoders.ResponseCOBSegment.parse(
            "\x1cAM28\x1cNT1\x1c5C  \x1c6C03\x1c7C610502\x1cMHMEDJUMBO\x1cNUXYZABCD\x1cMJRXAMCY\x1cUB0000000000\x1cUX20210101\x1cUY20391231"
            # noqa: E501
        )
