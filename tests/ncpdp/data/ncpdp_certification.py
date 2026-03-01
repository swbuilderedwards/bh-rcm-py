"""Test data for NCPDP certification."""
import datetime
import random
import sys

from lib.ncpdp import batch

# Lock down the behavior of the random number generator, so that subsequent
# generations of this file are consistent.
random.seed(0)


def reference_number():
    """Reference numbers are intended to be somewhat random, and 7 digits long."""
    return random.randint(1000000, 9999999)


def run_claims(fstream):
    batch.for_certification_format_claim_dicts_to(fstream, get_all_claims())


def get_all_claims():

    CURRENT_DATE = int(datetime.date.today().strftime("%Y%m%d"))
    SERVICE_PROVIDER_ID = 6501026200

    CLAIM_2A = {
        "header": {
            "bin_number": 447225,
            "transaction_code": "B1",
            "processor_control_number": "PCS",
            "transaction_count": "1",
            "service_provider_id_qualifier": "01",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "date_of_service": CURRENT_DATE,
            "software_vendor_certification_id": "D001200015",
        },
        "segments": [
            {
                "segment_identification": "04",
                "cardholder_id": "NTWKS8948",
                "cardholder_first_name": "Cain",
                "cardholder_last_name": "Marko",
                "home_plan": "600",
                "plan_id": "12345678",
                "eligibility_clarification_code": "0",
                "group_id": "CB010001",
                "person_code": "01",
                "patient_relationship_code": 1,
            },
            {
                "segment_identification": "01",
                "patient_id_qualifier": "99",
                "patient_id": "ABCD1234",
                "date_of_birth": 19970510,
                "patient_gender_code": 1,
                "patient_first_name": "Cain",
                "patient_last_name": "Marko",
                "patient_street_address": "1234 MAPLE LN",
                "patient_city_address": "Newberg",
                "patient_state_province_address": "OR",
                "patient_zip_postal_zone": 97132,
                "patient_phone_number": 4805551234,
                "place_of_service": "01",
                "patient_e_mail_address": "TEST.MEMBER@DOMAIN.COM",
                "patient_residence": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "segment_identification": "07",
                        "prescription_service_reference_number_qualifier": "1",
                        "prescription_service_reference_number": reference_number(),
                        "product_service_id_qualifier": "03",
                        "product_service_id": "50458009405",
                        "procedure_modifier_code_count": "01",
                        "procedure_modifier_code": "01",
                        "quantity_dispensed": 1000 * 180,
                        "fill_number": 0,
                        "days_supply": 90,
                        "compound_code": 1,
                        "daw_product_selection_code": "0",
                        "date_prescription_written": CURRENT_DATE,
                        "number_of_refills_authorized": 0,
                        "submission_clarification_code_count": 1,
                        "submission_clarification_code": 1,
                        "special_packaging_indicator": 1,
                        "scheduled_prescription_id_number": "RX0111222333",
                        "unit_of_measure": "EA",
                        "level_of_service": "01",
                        "intermediary_authorization_type_id": "99",
                        "intermediary_authorization_id": "12345006789",
                        "pharmacy_service_type": "01",
                    },
                    {
                        "segment_identification": "11",
                        "ingredient_cost_submitted": 20000.00,
                        "dispensing_fee_submitted": 1.50,
                        "patient_paid_amount_submitted": 25.00,
                        "usual_and_customary_charge": 20000.00,
                        "gross_amount_due": 20001.50,
                        "basis_of_cost_determination": "00",
                    },
                    {"segment_identification": "02", "provider_id_qualifier": "05", "provider_id": 9876543213},
                    {
                        "segment_identification": "03",
                        "prescriber_id_qualifier": "01",
                        "prescriber_id": "1234567893",
                        "prescriber_last_name": "SMITH",
                        "prescriber_telephone_number": "4805556789",
                        "primary_care_provider_id_qualifier": "12",
                        "primary_care_provider_id": "AB1234563",
                        "primary_care_provider_last_name": "SMITH",
                        "prescriber_first_name": "JOSEPH",
                        "prescriber_street_address": "6789 maple LN",
                        "prescriber_city_address": "SCOTTSDALE",
                        "prescriber_state_province_address": "AZ",
                        "prescriber_zip_postal_zone": "85260",
                    },
                ]
            }
        ],
    }

    CLAIM_2B = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
            "version_releasenumber": "D0",
        },
        "segments": [
            {
                "cardholder_first_name": CLAIM_2A["segments"][0]["cardholder_first_name"],
                "cardholder_id": CLAIM_2A["segments"][0]["cardholder_id"],
                "cardholder_last_name": CLAIM_2A["segments"][0]["cardholder_last_name"],
                "eligibility_clarification_code": "0",
                "group_id": "CB010001",
                "home_plan": "600",
                "patient_relationship_code": "1",
                "person_code": "01",
                "plan_id": "12345678",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_2A["segments"][1]["date_of_birth"],
                "patient_city_address": CLAIM_2A["segments"][1]["patient_city_address"],
                "patient_e_mail_address": "TEST.MEMBER@DOMAIN.COM",
                "patient_first_name": CLAIM_2A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_2A["segments"][1]["patient_gender_code"],
                "patient_id": "ABCD1234",
                "patient_id_qualifier": "99",
                "patient_last_name": CLAIM_2A["segments"][1]["patient_last_name"],
                "patient_phone_number": "4805551234",
                "patient_residence": "01",
                "patient_state_province_address": CLAIM_2A["segments"][1]["patient_state_province_address"],
                "patient_street_address": "1234 MAPLE LN",
                "patient_zip_postal_zone": CLAIM_2A["segments"][1]["patient_zip_postal_zone"],
                "place_of_service": "01",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "days_supply": "90",
                        "daw_product_selection_code": "0",
                        "fill_number": "00",
                        "intermediary_authorization_id": "12345006789",
                        "intermediary_authorization_type_id": "99",
                        "level_of_service": "01",
                        "number_of_refills_authorized": "00",
                        "pharmacy_service_type": "01",
                        "prescription_service_reference_number": CLAIM_2A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "prior_authorization_number_submitted": "88888888888",
                        "prior_authorization_type_code": "01",
                        "procedure_modifier_code": "01",
                        "procedure_modifier_code_count": "01",
                        "product_service_id_qualifier": "03",
                        "product_service_id": "50458009405",
                        "quantity_dispensed": 1000 * 180,
                        "scheduled_prescription_id_number": "RX0111222333",
                        "segment_identification": "07",
                        "special_packaging_indicator": "1",
                        "submission_clarification_code": "01",
                        "submission_clarification_code_count": "1",
                        "unit_of_measure": "EA",
                    },
                    {
                        "basis_of_cost_determination": "00",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "20001.50",
                        "ingredient_cost_submitted": "20000.00",
                        "patient_paid_amount_submitted": "25.00",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "20000.00",
                    },
                    {"provider_id": "9876543213", "provider_id_qualifier": "05", "segment_identification": "02"},
                    {
                        "prescriber_city_address": "SCOTTSDALE",
                        "prescriber_first_name": "JOSEPH",
                        "prescriber_id": "1234567893",
                        "prescriber_id_qualifier": "01",
                        "prescriber_last_name": "SMITH",
                        "prescriber_telephone_number": "4805556789",
                        "prescriber_state_province_address": "AZ",
                        "prescriber_street_address": "6789 maple LN",
                        "prescriber_zip_postal_zone": "85260",
                        "primary_care_provider_id": "AB1234563",
                        "primary_care_provider_id_qualifier": "12",
                        "primary_care_provider_last_name": "SMITH",
                        "segment_identification": "03",
                    },
                ]
            }
        ],
    }

    CLAIM_2C = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
            "version_release_number": "D0",
        },
        "segments": [
            {
                "cardholder_first_name": CLAIM_2A["segments"][0]["cardholder_first_name"],
                "cardholder_id": CLAIM_2A["segments"][0]["cardholder_id"],
                "cardholder_last_name": CLAIM_2A["segments"][0]["cardholder_last_name"],
                "eligibility_clarification_code": "0",
                "group_id": "CB010001",
                "home_plan": "600",
                "patient_relationship_code": "1",
                "person_code": "01",
                "plan_id": "12345678",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_2A["segments"][1]["date_of_birth"],
                "patient_city_address": CLAIM_2A["segments"][1]["patient_city_address"],
                "patient_e_mail_address": "TEST.MEMBER@DOMAIN.COM",
                "patient_first_name": CLAIM_2A["segments"][1]["patient_first_name"],
                "patient_gender_code": 1,
                "patient_id": "ABCD1234",
                "patient_id_qualifier": "99",
                "patient_last_name": CLAIM_2A["segments"][1]["patient_last_name"],
                "patient_phone_number": "4805551234",
                "patient_residence": "01",
                "patient_state_province_address": CLAIM_2A["segments"][1]["patient_state_province_address"],
                "patient_street_address": "1234 MAPLE LN",
                "patient_zip_postal_zone": CLAIM_2A["segments"][1]["patient_zip_postal_zone"],
                "place_of_service": "01",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "days_supply": "90",
                        "daw_product_selection_code": "0",
                        "fill_number": "00",
                        "intermediary_authorization_id": "12345006789",
                        "intermediary_authorization_type_id": "99",
                        "level_of_service": "01",
                        "number_of_refills_authorized": "00",
                        "pharmacy_service_type": "01",
                        "prescription_service_reference_number": CLAIM_2A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "prior_authorization_number_submitted": "88888888888",
                        "prior_authorization_type_code": "01",
                        "procedure_modifier_code": "01",
                        "procedure_modifier_code_count": "01",
                        "product_service_id_qualifier": "03",
                        "product_service_id": "50458009405",
                        "quantity_dispensed": 1000 * 180,
                        "scheduled_prescription_id_number": "RX0111222333",
                        "segment_identification": "07",
                        "special_packaging_indicator": "1",
                        "submission_clarification_code": "01",
                        "submission_clarification_code_count": "1",
                        "unit_of_measure": "EA",
                    },
                    {
                        "segment_identification": "11",
                        "basis_of_cost_determination": "00",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "20001.50",
                        "ingredient_cost_submitted": "20000.00",
                        "patient_paid_amount_submitted": "25.00",
                        "usual_and_customary_charge": "20000.00",
                    },
                    {"provider_id": "9876543213", "provider_id_qualifier": "05", "segment_identification": "02"},
                    {
                        "prescriber_city_address": "SCOTTSDALE",
                        "prescriber_first_name": "JOSEPH",
                        "prescriber_id": "1234567893",
                        "prescriber_id_qualifier": "01",
                        "prescriber_last_name": "SMITH",
                        "prescriber_telephone_number": "4805556789",
                        "prescriber_state_province_address": "AZ",
                        "prescriber_street_address": "6789 maple LN",
                        "prescriber_zip_postal_zone": "85260",
                        "primary_care_provider_id": "AB1234563",
                        "primary_care_provider_id_qualifier": "12",
                        "primary_care_provider_last_name": "SMITH",
                        "segment_identification": "03",
                    },
                ]
            }
        ],
    }

    CLAIM_2D = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
            "version_releasenumber": "D0",
        },
        "segments": [{"cardholder_id": CLAIM_2A["segments"][0]["cardholder_id"], "group_id": "CB010001", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "pharmacy_service_type": "01",
                        "prescription_service_reference_number_qualifier": "1",
                        "prescription_service_reference_number": CLAIM_2A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "product_service_id_qualifier": "03",
                        "product_service_id": "50458009405",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    CLAIM_3A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWKS2179",
                "group_id": "K3791101",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": "19830520",
                "patient_first_name": "Lucas",
                "patient_gender_code": 1,
                "patient_last_name": "Bishop",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "2",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number_qualifier": "1",
                        "prescription_service_reference_number": reference_number(),
                        "product_service_id": "00006074054",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 30,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "5.00",
                        "gross_amount_due": "495.99",
                        "ingredient_cost_submitted": "490.99",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "490.99",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                ]
            }
        ],
    }

    CLAIM_3B = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_3A["segments"][0]["cardholder_id"],
                "group_id": "K3791101",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_3A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_3A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_3A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_3A["segments"][1]["patient_last_name"],
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "2",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "originally_prescribed_product_service_code": "00006074054",
                        "originally_prescribed_product_service_id_qualifier": "03",
                        "originally_prescribed_quantity": "30",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": CLAIM_3A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "68180047902",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 30,
                        "segment_identification": "07",
                    },
                    {
                        "dur_co_agent_id": "00006074054",
                        "dur_co_agent_id_qualifier": "03",
                        "dur_pps_code_counter": "1",
                        "professional_service_code": "TH",
                        "reason_for_service_code": "PS",
                        "result_of_service_code": "1E",
                        "segment_identification": "08",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "5.00",
                        "gross_amount_due": "165.99",
                        "ingredient_cost_submitted": "160.99",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "160.99",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                ]
            }
        ],
    }

    CLAIM_3C = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_3A["segments"][0]["cardholder_id"], "group_id": "K3791101", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_3A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "68180047902",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    CLAIM_4A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "MEDDADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWKS4364",
                "group_id": "RXMD04",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": 19670926,
                "patient_first_name": "Douglas",
                "patient_gender_code": 1,
                "patient_last_name": "Ramsey",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "0",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": "1234",
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "54868525900",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 60,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "76.50",
                        "ingredient_cost_submitted": "75.00",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "87.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                ]
            }
        ],
    }

    CLAIM_4B = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_4A["segments"][0]["cardholder_id"],
                "group_id": "RXNMED",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_4A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_4A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_4A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_4A["segments"][1]["patient_last_name"],
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "0",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "other_coverage_code": "08",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": CLAIM_4A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "54868525900",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 60,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "76.50",
                        "ingredient_cost_submitted": "75.00",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "87.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {
                        "coordination_of_benefits_other_payments_count": "1",
                        "segment_identification": "05",
                        "other_payments": [
                            {
                                "other_payer_patient_responsibility_amount_count": "01",
                                "other_payer_patient_responsibility_amounts": [
                                    {
                                        "other_payer_patient_responsibility_amount_qualifier": "12",
                                        "other_payer_patient_responsibility_amount": "71.14",
                                    }
                                ],
                                "other_payer_coverage_type": "01",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_id": "447225",
                                "other_payer_id_qualifier": "03",
                                "benefit_stages": {"benefit_stage_count": "1", "benefit_stage_amount": "76.50", "benefit_stage_qualifier": "03"},
                            }
                        ],
                    },
                ]
            }
        ],
    }

    # Med D claim (OPPR) - Paid (Tertiary)
    CLAIM_4C = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBPCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_4A["segments"][0]["cardholder_id"],
                "group_id": "NMD20005",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_4A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_4A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_4A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_4A["segments"][1]["patient_last_name"],
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "0",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "other_coverage_code": "08",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": CLAIM_4A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "54868525900",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 60,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "76.50",
                        "ingredient_cost_submitted": "75.00",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "87.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {
                        "coordination_of_benefits_other_payments_count": "2",
                        "segment_identification": "05",
                        "other_payments": [
                            {
                                "other_payer_coverage_type": "02",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_id": "610511",
                                "other_payer_id_qualifier": "03",
                                "other_payer_patient_responsibility_amount_count": "01",
                                "other_payer_patient_responsibility_amounts": [
                                    {
                                        "other_payer_patient_responsibility_amount": "20.00",
                                        "other_payer_patient_responsibility_amount_qualifier": "06",
                                    }
                                ],
                            },
                            {
                                "other_payer_coverage_type": "01",
                                "other_payer_id_qualifier": "03",
                                "other_payer_id": "447225",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_patient_responsibility_amount_count": "01",
                                "other_payer_patient_responsibility_amounts": [
                                    {
                                        "other_payer_patient_responsibility_amount": "71.14",
                                        "other_payer_patient_responsibility_amount_qualifier": "12",
                                    }
                                ],
                            },
                        ],
                    },
                ]
            }
        ],
    }

    # Med D Claim (OPPR) - Reversal (Reversal of 4C)
    CLAIM_4D = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBPCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_4A["segments"][0]["cardholder_id"], "group_id": "NMD20005", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "other_coverage_code": "08",
                        "prescription_service_reference_number": CLAIM_4A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "54868525900",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    },
                    {
                        "coordination_of_benefits_other_payments_count": "1",
                        "segment_identification": "05",
                        "other_payments": [{"other_payer_coverage_type": "02"}],
                    },
                ]
            }
        ],
    }

    # Med D Claim (OPPR) - Reversal (reversal of 4B)
    CLAIM_4E = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_4A["segments"][0]["cardholder_id"], "group_id": "RXNMED", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "other_coverage_code": "08",
                        "prescription_service_reference_number": CLAIM_4A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "54868525900",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    },
                    {
                        "coordination_of_benefits_other_payments_count": "1",
                        "segment_identification": "05",
                        "other_payments": [{"other_payer_coverage_type": "01"}],
                    },
                ]
            }
        ],
    }

    # Med D Claim (OPPR) - Reversal (reversal of 4A)
    CLAIM_4F = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "MEDDADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_4A["segments"][0]["cardholder_id"], "group_id": "RXMD04", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_4A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "54868525900",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    # Med D Claim (OPAP) Paid (Primary)
    CLAIM_5A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "MEDDPCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWKS4416",
                "group_id": "MD620303",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": "19590217",
                "patient_first_name": "Kurt",
                "patient_gender_code": 1,
                "patient_last_name": "Wagner",
                "patient_residence": "01",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "0",
                        "days_supply": "90",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "patient_assignment_indicator": "N",
                        "pharmacy_service_type": "01",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": reference_number(),
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00703505103",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 90,
                        "segment_identification": "07",
                    },
                    {
                        "ingredient_cost_submitted": "450.00",
                        "dispensing_fee_submitted": "1.50",
                        "flat_sales_tax_amount_submitted": "2.00",
                        "percentage_sales_tax_amount_submitted": "35.64",
                        "percentage_sales_tax_rate_submitted": "792",
                        "percentage_sales_tax_basis_submitted": "02",
                        "patient_paid_amount_submitted": "0.00",
                        "usual_and_customary_charge": "540.00",
                        "gross_amount_due": "489.14",
                        "basis_of_cost_determination": "02",
                        "segment_identification": "11",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                ]
            }
        ],
    }

    # Med D Claim (OPAP) Paid (Secondary)
    CLAIM_5B = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBPCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_5A["segments"][0]["cardholder_id"],
                "group_id": "NMD20004",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_5A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_5A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_5A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_5A["segments"][1]["patient_last_name"],
                "patient_residence": "01",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "0",
                        "days_supply": "90",
                        "fill_number": "00",
                        "number_of_refills_authorized": "03",
                        "other_coverage_code": "02",
                        "patient_assignment_indicator": "N",
                        "pharmacy_service_type": "01",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": CLAIM_5A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00703505103",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 90,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "02",
                        "dispensing_fee_submitted": "1.50",
                        "flat_sales_tax_amount_submitted": "2.00",
                        "gross_amount_due": "489.14",
                        "ingredient_cost_submitted": "450.00",
                        "patient_paid_amount_submitted": "0.00",
                        "percentage_sales_tax_amount_submitted": "35.64",
                        "percentage_sales_tax_basis_submitted": "02",
                        "percentage_sales_tax_rate_submitted": "792",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "540.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {
                        "segment_identification": "05",
                        "coordination_of_benefits_other_payments_count": "1",
                        "other_payments": [
                            {
                                "other_payer_coverage_type": "01",
                                "other_payer_id_qualifier": "03",
                                "other_payer_id": "447225",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_amount_paid_count": "1",
                                "other_payer_amount_paid_qualifier": "07",
                                "other_payer_amount_paid": "139.69",
                            }
                        ],
                    },
                ]
            }
        ],
    }

    # Med D Claim (OPAP) Paid (Tertiary)
    CLAIM_5C = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_5A["segments"][0]["cardholder_id"],
                "group_id": "RXNTCT",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_5A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_5A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_5A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_5A["segments"][1]["patient_last_name"],
                "patient_residence": "01",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "segment_identification": "07",
                        "prescription_service_reference_number_qualifier": "1",
                        "prescription_service_reference_number": CLAIM_5A["transactions"][0]["segments"][0][
                            "prescription_service_reference_number"
                        ],  # Same as 5A
                        "product_service_id_qualifier": "03",
                        "product_service_id": "00703505103",
                        "quantity_dispensed": 1000 * 90,
                        "fill_number": "00",
                        "days_supply": "90",
                        "compound_code": "1",
                        "daw_product_selection_code": "0",
                        "date_prescription_written": CURRENT_DATE,
                        "number_of_refills_authorized": "03",
                        "prescription_origin_code": "1",
                        "other_coverage_code": "02",
                        "patient_assignment_indicator": "N",
                        "pharmacy_service_type": "01",
                    },
                    {
                        "segment_identification": "11",
                        "basis_of_cost_determination": "02",
                        "dispensing_fee_submitted": "1.50",
                        "flat_sales_tax_amount_submitted": "2.00",
                        "gross_amount_due": "489.14",
                        "ingredient_cost_submitted": "450.00",
                        "patient_paid_amount_submitted": "0.00",
                        "percentage_sales_tax_amount_submitted": "35.64",
                        "percentage_sales_tax_basis_submitted": "02",
                        "percentage_sales_tax_rate_submitted": "792",
                        "usual_and_customary_charge": "540.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {
                        "segment_identification": "05",
                        "coordination_of_benefits_other_payments_count": "2",
                        "other_payments": [
                            {
                                "other_payer_amount_paid": "198.75",
                                "other_payer_amount_paid_count": "1",
                                "other_payer_amount_paid_qualifier": "07",
                                "other_payer_coverage_type": "02",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_id": "610511",
                                "other_payer_id_qualifier": "03",
                            },
                            {
                                "other_payer_amount_paid": "139.69",
                                "other_payer_amount_paid_count": "1",
                                "other_payer_amount_paid_qualifier": "07",
                                "other_payer_coverage_type": "01",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_id": "447225",
                                "other_payer_id_qualifier": "03",
                            },
                        ],
                    },
                ]
            }
        ],
    }

    # Med D Claim (OPAP) - Reversal (reversal of 5C)
    CLAIM_5D = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_5A["segments"][0]["cardholder_id"], "group_id": "RXNTCT", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "other_coverage_code": "02",
                        "prescription_service_reference_number": CLAIM_5A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00703505103",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    },
                    {
                        "coordination_of_benefits_other_payments_count": "1",
                        "segment_identification": "05",
                        "other_payments": [{"other_payer_coverage_type": "02"}],
                    },
                ]
            }
        ],
    }

    # Med D Claim (OPAP) - Reversal (reversal of 5B)
    CLAIM_5E = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBPCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_5A["segments"][0]["cardholder_id"], "group_id": "NMD20004", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "other_coverage_code": "02",
                        "prescription_service_reference_number": CLAIM_5A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00703505103",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    },
                    {
                        "coordination_of_benefits_other_payments_count": "1",
                        "segment_identification": "05",
                        "other_payments": [{"other_payer_coverage_type": "01"}],
                    },
                ]
            }
        ],
    }

    CLAIM_5F = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "MEDDPCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_5A["segments"][0]["cardholder_id"], "group_id": "MD620303", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_5A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00703505103",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    # DISCOUNT CARD Paid Claim
    CLAIM_6A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWKS4198",
                "group_id": "25221000",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": 19650416,
                "patient_first_name": "Yvette",
                "patient_gender_code": 2,
                "patient_last_name": "Therese",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "2",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "00",
                        "prescription_service_reference_number": reference_number(),
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00378600401",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 100,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "2.00",
                        "gross_amount_due": "288.60",
                        "incentive_amount_submitted": "10.00",
                        "ingredient_cost_submitted": "265.41",
                        "other_amount_claimed_submitted": "11.19",
                        "other_amount_claimed_submitted_count": "1",
                        "other_amount_claimed_submitted_qualifier": "03",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "265.41",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                ]
            }
        ],
    }

    CLAIM_6B = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_6A["segments"][0]["cardholder_id"], "group_id": "25221000", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_6A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00378600401",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    CLAIM_7A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "ADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWKS1695",
                "group_id": "RXTNWK",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": 19950526,
                "patient_first_name": "Dean",
                "patient_gender_code": 1,
                "patient_last_name": "Boswell",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "2",
                        "compound_type": "99",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "1",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "00",
                        "prescription_service_reference_number": reference_number(),
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "0",
                        "product_service_id_qualifier": "00",
                        "quantity_dispensed": 1000 * 240,
                        "route_of_administration": "26643006",
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "208.04",
                        "ingredient_cost_submitted": "206.54",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "325.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {"dur_pps_code_counter": "1", "dur_pps_level_of_effort": "14", "segment_identification": "08"},
                    {
                        "modifier_codes": {"compound_ingredient_modifier_code_count": "1", "compound_ingredient_modifier_code": "A1"},
                        "compound_dosage_form_description_code": "15",
                        "compound_dispensing_unit_form_indicator": "3",
                        "segment_identification": "10",
                        "compound_ingredient_component_count": 25,
                        "ingredients": [
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.41",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "54868471000",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "4.80",
                                "compound_ingredient_quantity": 1000 * 2.2,
                                "compound_product_id": "63874028001",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_drug_cost": "13.87",
                                "compound_ingredient_quantity": 1000 * 35,
                                "compound_product_id": "00023917705",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.51",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "00378710601",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "10.73",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "00781104901",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "19.46",
                                "compound_ingredient_quantity": 1000 * 30,
                                "compound_product_id": "16252057301",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "14.45",
                                "compound_ingredient_quantity": 1000 * 30,
                                "compound_product_id": "63629378903",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "16.06",
                                "compound_ingredient_quantity": 1000 * 5,
                                "compound_product_id": "00310040160",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "11.35",
                                "compound_ingredient_quantity": 1000 * 0.5,
                                "compound_product_id": "00052010730",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "1.40",
                                "compound_ingredient_quantity": 1000 * 30,
                                "compound_product_id": "00378120001",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "7.26",
                                "compound_ingredient_quantity": 1000 * 10,
                                "compound_product_id": "68084040111",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.80",
                                "compound_ingredient_quantity": 1000 * 1,
                                "compound_product_id": "45802081841",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "17.24",
                                "compound_ingredient_quantity": 1000 * 25,
                                "compound_product_id": "00074336860",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "6.85",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "00085174701",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "16.38",
                                "compound_ingredient_quantity": 1000 * 10,
                                "compound_product_id": "65162064210",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.02",
                                "compound_ingredient_quantity": 1000 * 5,
                                "compound_product_id": "00173067601",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "1.35",
                                "compound_ingredient_quantity": 1000 * 0.25,
                                "compound_product_id": "00781183801",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.75",
                                "compound_ingredient_quantity": 1000 * 1,
                                "compound_product_id": "00078036715",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "1.49",
                                "compound_ingredient_quantity": 1000 * 2,
                                "compound_product_id": "00143999201",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "7.50",
                                "compound_ingredient_quantity": 1000 * 2.5,
                                "compound_product_id": "00009001755",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "8.26",
                                "compound_ingredient_quantity": 1000 * 10,
                                "compound_product_id": "00074052260",
                                "compound_product_id_qualifier": "03",
                            },
                        ],
                    },
                ]
            }
        ],
    }

    CLAIM_7B = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "ADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_7A["segments"][0]["cardholder_id"],
                "group_id": "RXTNWK",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_3A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_7A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_3A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_7A["segments"][1]["patient_last_name"],
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "2",
                        "compound_type": "99",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "1",
                        "days_supply": "30",
                        "fill_number": "00",
                        "number_of_refills_authorized": "00",
                        "prescription_service_reference_number": CLAIM_7A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "0",
                        "product_service_id_qualifier": "00",
                        "quantity_dispensed": 1000 * 240,
                        "route_of_administration": "26643006",
                        "segment_identification": "07",
                        "submission_clarification_code": "08",
                        "submission_clarification_code_count": "1",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "1.50",
                        "gross_amount_due": "208.04",
                        "ingredient_cost_submitted": "206.54",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "325.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {"dur_pps_code_counter": "1", "dur_pps_level_of_effort": "14", "segment_identification": "08"},
                    {
                        "compound_dispensing_unit_form_indicator": "3",
                        "modifier_codes": {"compound_ingredient_modifier_code": "A1", "compound_ingredient_modifier_code_count": "01"},
                        "compound_ingredient_component_count": "25",
                        "compound_dosage_form_description_code": "15",
                        "segment_identification": "10",
                        "ingredients": [
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.41",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "54868471000",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "4.80",
                                "compound_ingredient_quantity": 1000 * 2.2,
                                "compound_product_id": "63874028001",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "13.87",
                                "compound_ingredient_quantity": 1000 * 35,
                                "compound_product_id": "00002322730",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.51",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "0023917705",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "18.52",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "00378710601",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "10.73",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "00781104901",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "19.46",
                                "compound_ingredient_quantity": 1000 * 30,
                                "compound_product_id": "16252057301",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "14.45",
                                "compound_ingredient_quantity": 1000 * 30,
                                "compound_product_id": "63629378903",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "16.06",
                                "compound_ingredient_quantity": 1000 * 5,
                                "compound_product_id": "00054408425",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "11.35",
                                "compound_ingredient_quantity": 1000 * 5,
                                "compound_product_id": "00310040160",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.14",
                                "compound_ingredient_quantity": 1000 * 0.5,
                                "compound_product_id": "00052010730",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "1.40",
                                "compound_ingredient_quantity": 1000 * 30,
                                "compound_product_id": "00378120001",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "7.26",
                                "compound_ingredient_quantity": 1000 * 10,
                                "compound_product_id": "68084040111",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.80",
                                "compound_ingredient_quantity": 1000 * 1,
                                "compound_product_id": "45802081841",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "17.24",
                                "compound_ingredient_quantity": 1000 * 25,
                                "compound_product_id": "00172409760",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "6.85",
                                "compound_ingredient_quantity": 1000 * 20,
                                "compound_product_id": "00074336860",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.1",
                                "compound_ingredient_quantity": 1000 * 40,
                                "compound_product_id": "00085174701",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "16.38",
                                "compound_ingredient_quantity": 1000 * 10,
                                "compound_product_id": "65162064210",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.02",
                                "compound_ingredient_quantity": 1000 * 5,
                                "compound_product_id": "00173067601",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "1.35",
                                "compound_ingredient_quantity": 1000 * 0.25,
                                "compound_product_id": "00781183801",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.75",
                                "compound_ingredient_quantity": 1000 * 1,
                                "compound_product_id": "00185003410",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "0.75",
                                "compound_ingredient_quantity": 1000 * 1.49,
                                "compound_product_id": "00078036715",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "3",
                                "compound_ingredient_quantity": 1000 * 2,
                                "compound_product_id": "00143999201",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "7.50",
                                "compound_ingredient_quantity": 1000 * 2.5,
                                "compound_product_id": "00009001755",
                                "compound_product_id_qualifier": "03",
                            },
                            {
                                "compound_ingredient_basis_of_cost_determination": "01",
                                "compound_ingredient_drug_cost": "8.26",
                                "compound_ingredient_quantity": 1000 * 10,
                                "compound_product_id": "00074052260",
                                "compound_product_id_qualifier": "03",
                            },
                        ],
                    },
                ]
            }
        ],
    }

    CLAIM_7C = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "ADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_7A["segments"][0]["cardholder_id"], "group_id": "RXTNWK", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_7A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00",
                        "product_service_id_qualifier": "0",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    # Vaccine Claim Paid
    CLAIM_8A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "MEDDADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWK51695",
                "group_id": "RXMD04",
                "segment_identification": "04",
                "eligibility_clarification_code": 1,
                "person_code": "01",
                "patient_relationship_code": 1,
                "medigap_id": 123456789,
                "medicaid_indicator": "AZ",
                "provider_accept_assignment_indicator": "N",
                "cms_part_d_defined_qualified_facility": "N",
                "medicaid_id_number": 111000222,
            },
            {
                "date_of_birth": 19950526,
                "patient_first_name": "Dean",
                "patient_gender_code": 1,
                "patient_last_name": "Boswell",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "0",
                        "days_supply": "1",
                        "fill_number": "00",
                        "number_of_refills_authorized": "00",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": reference_number(),
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00006496300",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 1,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "00",
                        "dispensing_fee_submitted": "3.50",
                        "gross_amount_due": "128.50",
                        "incentive_amount_submitted": "25.00",
                        "ingredient_cost_submitted": "100.00",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "150.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {"dur_pps_code_counter": "1", "professional_service_code": "MA", "segment_identification": "08"},
                    {
                        "facility_city_address": "MEMPHIS",
                        "facility_id": "987654321",
                        "facility_name": "Shots r US",
                        "facility_street_address": "555 N ADDY RD",
                        "facility_zip_postal_zone": "38106",
                        "facility_state_province_address": "TN",
                        "segment_identification": "15",
                    },
                ]
            }
        ],
    }

    # Vaccine Claim Reversal
    CLAIM_8B = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "MEDDADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_8A["segments"][0]["cardholder_id"], "group_id": "RXMD04", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_8A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00006496300",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    # Gov COB Paid (Primary)
    CLAIM_9A = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": "NTWKS6434",
                "group_id": "MD620303",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": 19780521,
                "patient_first_name": "Jean",
                "patient_gender_code": 2,
                "patient_last_name": "Grey",
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "1",
                        "days_supply": "83",
                        "fill_number": "00",
                        "number_of_refills_authorized": "00",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": reference_number(),
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00002751001",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 90,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "5.00",
                        "flat_sales_tax_amount_submitted": "2.00",
                        "gross_amount_due": "554.50",
                        "ingredient_cost_submitted": "500.00",
                        "percentage_sales_tax_amount_submitted": "47.50",
                        "percentage_sales_tax_basis_submitted": "02",
                        "percentage_sales_tax_rate_submitted": "950",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "500.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {
                        "clinical_information_counter": "1",
                        "diagnosis_code": "250.00",
                        "diagnosis_code_count": "1",
                        "diagnosis_code_qualifier": "02",
                        "measurement_date": CURRENT_DATE,
                        "measurement_dimension": "99",
                        "measurement_time": "14:00",
                        "measurement_unit": "01",
                        "measurement_value": "150",
                        "segment_identification": "13",
                    },
                    {
                        "additional_documentation_type_id": "012",
                        "length_of_need": "5",
                        "length_of_need_qualifier": "2",
                        "prescriber_supplier_date_signed": CURRENT_DATE,
                        "question_number_letter_count": "05",
                        "request_period_begin_date": CURRENT_DATE,
                        "request_period_recert_revised_date": CURRENT_DATE,
                        "request_status": "2",
                        "segment_identification": "14",
                        "supporting_documentation": "TEST DOCUMENTATION SEGMENT",
                        "questions": [
                            {"question_number_letter": "1A", "question_percent_response": "25"},
                            {"question_number_letter": "1B", "question_date_response": CURRENT_DATE},
                            {"question_number_letter": "1C", "question_dollar_amount_response": "15.25"},
                            {"question_number_letter": "1D", "question_numeric_response": "123456789"},
                            {"question_number_letter": "1E", "question_alphanumeric_response": "TEST ALPHANUMERIC RESPONSE"},
                        ],
                    },
                    {"narrative_message": "TEST NARRATIVE SEGMENT", "segment_identification": "16"},
                ]
            }
        ],
    }

    # Gov COB Paid (Secondary)
    CLAIM_9B = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "cardholder_id": CLAIM_9A["segments"][0]["cardholder_id"],
                "group_id": "AZSPAP",
                "patient_relationship_code": "1",
                "person_code": "01",
                "segment_identification": "04",
            },
            {
                "date_of_birth": CLAIM_9A["segments"][1]["date_of_birth"],
                "patient_first_name": CLAIM_9A["segments"][1]["patient_first_name"],
                "patient_gender_code": CLAIM_9A["segments"][1]["patient_gender_code"],
                "patient_last_name": CLAIM_9A["segments"][1]["patient_last_name"],
                "segment_identification": "01",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "compound_code": "1",
                        "date_prescription_written": CURRENT_DATE,
                        "daw_product_selection_code": "1",
                        "days_supply": "83",
                        "fill_number": "00",
                        "number_of_refills_authorized": "00",
                        "other_coverage_code": "02",
                        "prescription_origin_code": "1",
                        "prescription_service_reference_number": CLAIM_9A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00002751001",
                        "product_service_id_qualifier": "03",
                        "quantity_dispensed": 1000 * 90,
                        "segment_identification": "07",
                    },
                    {
                        "basis_of_cost_determination": "01",
                        "dispensing_fee_submitted": "5.00",
                        "flat_sales_tax_amount_submitted": "2.00",
                        "gross_amount_due": "554.50",
                        "ingredient_cost_submitted": "500.00",
                        "percentage_sales_tax_amount_submitted": "47.50",
                        "percentage_sales_tax_basis_submitted": "02",
                        "percentage_sales_tax_rate_submitted": "950",
                        "segment_identification": "11",
                        "usual_and_customary_charge": "500.00",
                    },
                    {"prescriber_id": "1234567893", "prescriber_id_qualifier": "01", "segment_identification": "03"},
                    {
                        "segment_identification": "05",
                        "coordination_of_benefits_other_payments_count": "1",
                        "other_payments": [
                            {
                                "other_payer_amount_paid": "176.25",
                                "other_payer_amount_paid_count": "1",
                                "other_payer_amount_paid_qualifier": "07",
                                "other_payer_coverage_type": "01",
                                "other_payer_date": CURRENT_DATE,
                                "other_payer_id": "447225",
                                "other_payer_id_qualifier": "03",
                                "other_payer_patient_responsibility_amount_count": "2",
                                "other_payer_patient_responsibility_amounts": [
                                    {"other_payer_patient_responsibility_amount_qualifier": "01", "other_payer_patient_responsibility_amount": 265},
                                    {
                                        "other_payer_patient_responsibility_amount_qualifier": "07",
                                        "other_payer_patient_responsibility_amount": 58.75,
                                    },
                                ],
                            }
                        ],
                    },
                    {
                        "clinical_information_counter": "1",
                        "diagnosis_code": "250.00",
                        "diagnosis_code_count": "1",
                        "diagnosis_code_qualifier": "02",
                        "measurement_date": CURRENT_DATE,
                        "measurement_dimension": "99",
                        "measurement_time": "14:00",
                        "measurement_unit": "01",
                        "measurement_value": "150",
                        "segment_identification": "13",
                    },
                    {
                        "additional_documentation_type_id": "012",
                        "length_of_need": "5",
                        "length_of_need_qualifier": "2",
                        "prescriber_supplier_date_signed": CURRENT_DATE,
                        "question_number_letter_count": "05",
                        "request_period_begin_date": CURRENT_DATE,
                        "request_period_recert_revised_date": CURRENT_DATE,
                        "request_status": "2",
                        "segment_identification": "14",
                        "supporting_documentation": "TEST DOCUMENTATION SEGMENT",
                        "questions": [
                            {"question_number_letter": "1A", "question_percent_response": "25"},
                            {"question_number_letter": "1B", "question_date_response": CURRENT_DATE},
                            {"question_number_letter": "1C", "question_dollar_amount_response": "15.25"},
                            {"question_number_letter": "1D", "question_numeric_response": "123456789"},
                            {"question_number_letter": "1E", "question_alphanumeric_response": "TEST ALPHANUMERIC RESPONSE"},
                        ],
                    },
                    {"narrative_message": "TEST NARRATIVE SEGMENT", "segment_identification": "16"},
                ]
            }
        ],
    }

    # Gov COB Reversal (Secondary 9B)
    CLAIM_9C = {
        "header": {
            "bin_number": "610511",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "COBADV",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [
            {"cardholder_id": CLAIM_9A["segments"][0]["cardholder_id"], "group_id": "AZSPAP", "segment_identification": "04"},
            {
                "fill_number": "00",
                "other_coverage_code": "02",
                "prescription_service_reference_number": CLAIM_9A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                "prescription_service_reference_number_qualifier": "1",
                "product_service_id": "00002751001",
                "product_service_id_qualifier": "03",
                "segment_identification": "07",
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "coordination_of_benefits_other_payments_count": "1",
                        "segment_identification": "05",
                        "other_payments": [{"other_payer_coverage_type": "01"}],
                    }
                ]
            }
        ],
    }

    CLAIM_9D = {
        "header": {
            "bin_number": "447225",
            "date_of_service": CURRENT_DATE,
            "processor_control_number": "PCS",
            "service_provider_id": SERVICE_PROVIDER_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": "D001200015",
            "transaction_code": "B2",
            "transaction_count": "1",
        },
        "segments": [{"cardholder_id": CLAIM_9A["segments"][0]["cardholder_id"], "group_id": "MD620303", "segment_identification": "04"}],
        "transactions": [
            {
                "segments": [
                    {
                        "fill_number": "00",
                        "prescription_service_reference_number": CLAIM_9A["transactions"][0]["segments"][0]["prescription_service_reference_number"],
                        "prescription_service_reference_number_qualifier": "1",
                        "product_service_id": "00002751001",
                        "product_service_id_qualifier": "03",
                        "segment_identification": "07",
                    }
                ]
            }
        ],
    }

    return [
        CLAIM_2A,
        CLAIM_2B,
        CLAIM_2C,
        CLAIM_2D,
        CLAIM_3A,
        CLAIM_3B,
        CLAIM_3C,
        CLAIM_4A,
        CLAIM_4B,
        CLAIM_4C,
        CLAIM_4D,
        CLAIM_4E,
        CLAIM_4F,
        CLAIM_5A,
        CLAIM_5B,
        CLAIM_5C,
        CLAIM_5D,
        CLAIM_5E,
        CLAIM_5F,
        CLAIM_6A,
        CLAIM_6B,
        CLAIM_7A,
        CLAIM_7B,
        CLAIM_7C,
        CLAIM_8A,
        CLAIM_8B,
        CLAIM_9A,
        CLAIM_9B,
        CLAIM_9C,
        CLAIM_9D,
    ]


if __name__ == "__main__":
    run_claims(sys.stdout)
