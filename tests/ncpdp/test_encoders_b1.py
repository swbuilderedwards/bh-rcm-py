"""Additional tests for the NCPDP encoders module: the B1 transaction."""
from decimal import Decimal

from lib.ncpdp import encoders


SPECIMEN_B1_TRANSMISSION_REQUEST_DICT = {
    "header": {
        "bin_number": 610066,
        "transaction_code": "B1",
        "processor_control_number": "1234567890",
        "transaction_count": "1",
        "service_provider_id_qualifier": "01",
        "service_provider_id": "4563663111",
        "date_of_service": 20070915,
        "software_vendor_certification_id": "98765",
    },
    "segments": [
        {
            "segment_identification": "01",
            "date_of_birth": 19620615,
            "patient_gender_code": 1,
            "patient_first_name": "Joseph",
            "patient_last_name": "Smith",
            "patient_street_address": "123 Main Street",
            "patient_city_address": "My town",
            "patient_state_province_address": "CO",
            "patient_zip_postal_zone": "34567",
            "patient_phone_number": 2014658923,
            "patient_e_mail_address": "jsmith@ncpdp.org",
        },
        {"segment_identification": "04", "cardholder_id": "987654321"},
    ],
    "transactions": [
        {
            "segments": [
                {
                    "segment_identification": "07",
                    "prescription_service_reference_number_qualifier": "1",
                    "prescription_service_reference_number": 1234567,
                    "product_service_id_qualifier": "03",
                    "product_service_id": "00006094268",
                    "quantity_dispensed": 30000,
                    "fill_number": 0,
                    "days_supply": 30,
                    "compound_code": 1,
                    "daw_product_selection_code": "0",
                    "date_prescription_written": 20070915,
                    "number_of_refills_authorized": 5,
                    "prescription_origin_code": 1,
                    "submission_clarification_code_count": 1,
                    "submission_clarification_code": 4,
                    "other_coverage_code": "1",
                    "special_packaging_indicator": 1,
                    "unit_of_measure": "EA",
                },
                {"segment_identification": "02", "provider_id_qualifier": "05", "provider_id": 3935933111},
                {
                    "segment_identification": "03",
                    "prescriber_id_qualifier": "08",
                    "prescriber_id": "00G2345",
                    "prescriber_last_name": "JONES",
                    "prescriber_telephone_number": 2013639572,
                    "primary_care_provider_id_qualifier": "01",
                    "primary_care_provider_id": "1234566",
                    "primary_care_provider_last_name": "WRIGHT",
                },
                {
                    "segment_identification": "11",
                    "ingredient_cost_submitted": 55.70,
                    "dispensing_fee_submitted": 10.00,
                    "other_amount_claimed_submitted_count": 1,
                    "other_amount_claimed_submitted_qualifier": "01",
                    "other_amount_claimed_submitted": 15.00,
                    "usual_and_customary_charge": 86.70,
                    "gross_amount_due": 80.70,
                    "basis_of_cost_determination": "03",
                },
            ]
        }
    ],
}

# Roundtripping the dictionary above results in minor changes to the structure
# of this data.
SPECIMEN_B1_TRANSMISSION_REQUEST_ROUNDTRIPPED = {
    "header": {
        "bin_number": 610066,
        "transaction_code": "B1",
        "processor_control_number": "1234567890",
        "transaction_count": "1",
        "service_provider_id_qualifier": "01",
        "service_provider_id": "4563663111",
        "date_of_service": 20070915,
        "software_vendor_certification_id": "98765",
    },
    "segments": [
        {
            "segment_identification": "01",
            "date_of_birth": 19620615,
            "patient_gender_code": 1,
            "patient_first_name": "JOSEPH",
            "patient_last_name": "SMITH",
            "patient_street_address": "123 MAIN STREET",
            "patient_city_address": "MY TOWN",
            "patient_state_province_address": "CO",
            "patient_zip_postal_zone": "34567",
            "patient_phone_number": 2014658923,
            "patient_e_mail_address": "JSMITH@NCPDP.ORG",
        },
        {"segment_identification": "04", "cardholder_id": "987654321"},
    ],
    "transactions": [
        {
            "segments": [
                {
                    "segment_identification": "07",
                    "prescription_service_reference_number_qualifier": "1",
                    "prescription_service_reference_number": 1234567,
                    "product_service_id_qualifier": "03",
                    "product_service_id": "00006094268",
                    "quantity_dispensed": 30000,
                    "fill_number": 0,
                    "days_supply": 30,
                    "compound_code": 1,
                    "daw_product_selection_code": "0",
                    "date_prescription_written": 20070915,
                    "number_of_refills_authorized": 5,
                    "prescription_origin_code": 1,
                    "submission_clarification_code_count": 1,
                    "submission_clarification_code": 4,
                    "other_coverage_code": "1",
                    "special_packaging_indicator": 1,
                    "unit_of_measure": "EA",
                },
                {"segment_identification": "02", "provider_id_qualifier": "05", "provider_id": 3935933111},
                {
                    "segment_identification": "03",
                    "prescriber_id_qualifier": "08",
                    "prescriber_id": "00G2345",
                    "prescriber_last_name": "JONES",
                    "prescriber_telephone_number": 2013639572,
                    "primary_care_provider_id_qualifier": "01",
                    "primary_care_provider_id": "1234566",
                    "primary_care_provider_last_name": "WRIGHT",
                },
                {
                    "segment_identification": "11",
                    "ingredient_cost_submitted": Decimal("55.70"),
                    "dispensing_fee_submitted": Decimal("10.00"),
                    "other_amount_claimed_submitted_count": 1,
                    "other_amount_claimed_submitted_qualifier": "01",
                    "other_amount_claimed_submitted": Decimal("15.00"),
                    "usual_and_customary_charge": Decimal("86.70"),
                    "gross_amount_due": Decimal("80.70"),
                    "basis_of_cost_determination": "03",
                },
            ]
        }
    ],
}


SPECIMEN_B1_TRANSMISSION_REQUEST_BODY = """610066D0B112345678901014563663111     2007091598765     \x1e\x1cAM01\x1cC419620615\x1cC51\x1cCAJOSEPH\x1cCBSMITH\x1cCM123 MAIN STREET\x1cCNMY TOWN\x1cCOCO\x1cCP34567\x1cCQ2014658923\x1cHNJSMITH@NCPDP.ORG\x1e\x1cAM04\x1cC2987654321\x1d\x1e\x1cAM07\x1cEM1\x1cD21234567\x1cE103\x1cD700006094268\x1cE730000\x1cD300\x1cD530\x1cD61\x1cD80\x1cDE20070915\x1cDF05\x1cNX1\x1cDK4\x1cDT1\x1c28EA\x1cDJ1\x1cC81\x1e\x1cAM02\x1cEY05\x1cE93935933111\x1e\x1cAM03\x1cEZ08\x1cDB00G2345\x1cDRJONES\x1cPM2013639572\x1c2E01\x1cDL1234566\x1c4EWRIGHT\x1e\x1cAM11\x1cD9557{\x1cDC100{\x1cDQ867{\x1cDU807{\x1cDN03\x1cH71\x1cH801\x1cH9150{"""  # noqa: E501


def test_b1_request_encoding():
    assert encoders.Transmission.format(SPECIMEN_B1_TRANSMISSION_REQUEST_DICT) == SPECIMEN_B1_TRANSMISSION_REQUEST_BODY


SPECIMEN_B1_TRANSMISSION_PAID_RESPONSE_BODY = """D0B11A014563663111     20070915\x1E\x1CAM20\x1CF4TRANSMISSION MESSAGE TEXT\x1D\x1E\x1CAM21\x1CANP\x1CF3123456789123456789\x1CUF1\x1CUH01\x1CFQTRANSACTION MESSAGE TEXT\x1C7F03\x1C8F6023570862\x1E\x1CAM22\x1CEM1\x1CD21234567\x1C9F1\x1CAP03\x1CAR17236056901\x1E\x1CAM23\x1CF5100{\x1CF6557{\x1CF7100{\x1CAV1\x1CJ21\x1CJ301\x1CJ4150{\x1CF9707{\x1CFM1\x1CFN20{\x1CFI80{\x1CAW20{\x1CEQ20{"""  # noqa: E501


SPECIMEN_B1_TRANSMISSION_PAID_RESPONSE_DICT = {
    "header": {
        "transaction_code": "B1",
        "transaction_count": "1",
        "header_response_status": "A",
        "service_provider_id_qualifier": "01",
        "service_provider_id": "4563663111",
        "date_of_service": 20070915,
    },
    "segments": [{"segment_identification": "20", "message": "TRANSMISSION MESSAGE TEXT"}],
    "transactions": [
        {
            "segments": [
                {
                    "segment_identification": "21",
                    "transaction_response_status": "P",
                    "authorization_number": 123456789123456789,
                    "additional_message_information_count": 1,
                    "additional_message_information_qualifier": "01",
                    "additional_message_information": "TRANSACTION MESSAGE TEXT",
                    "help_desk_phone_number_qualifier": "03",
                    "help_desk_phone_number": 6023570862,
                },
                {
                    "segment_identification": "22",
                    "prescription_service_reference_number_qualifier": "1",
                    "prescription_service_reference_number": 1234567,
                    "preferred_product_count": 1,
                    "preferred_product_id_qualifier": "03",
                    "preferred_product_id": "17236056901",
                },
                {
                    "segment_identification": "23",
                    "patient_pay_amount": Decimal("10"),
                    "ingredient_cost_paid": Decimal("55.7"),
                    "dispensing_fee_paid": Decimal("10"),
                    "tax_exempt_indicator": 1,
                    "other_amount_paid_count": 1,
                    "other_amount_paid_qualifier": "01",
                    "other_amount_paid": Decimal("15"),
                    "total_amount_paid": Decimal("70.7"),
                    "basis_of_reimbursement_determination": 1,
                    "amount_attributed_to_sales_tax": Decimal("2"),
                    "amount_of_copay": Decimal("8.00"),
                    "flat_sales_tax_amount_paid": Decimal("2"),
                    "patient_sales_tax_amount": Decimal("2"),
                },
            ]
        }
    ],
}


def test_b1_response_encoding():
    assert encoders.Transmission.format(SPECIMEN_B1_TRANSMISSION_PAID_RESPONSE_DICT) == SPECIMEN_B1_TRANSMISSION_PAID_RESPONSE_BODY


def test_b1_response_decoding():
    assert encoders.Transmission.parse(SPECIMEN_B1_TRANSMISSION_PAID_RESPONSE_BODY) == SPECIMEN_B1_TRANSMISSION_PAID_RESPONSE_DICT
