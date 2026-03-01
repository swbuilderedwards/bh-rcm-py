"""Bridge layer from bh-rcm Supabase data model to NCPDP transmission dicts."""
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


BIG_HEALTH_PHARMACY_ID = "1316418981"
BIG_HEALTH_NCPDP_CERTIFICATION_ID = "D0315211BH"

FIRST_NAME_MAX_LEN = 12
LAST_NAME_MAX_LEN = 15

GENDER_TO_NCPDP = {"M": 1, "F": 2, "U": 3, "X": 3}


def _ncpdp_date(d: date) -> int:
    return int(d.strftime("%Y%m%d"))


class NcpdpClaimInput(BaseModel):
    # From patients
    bin_number: str
    caremark_id: str
    rx_group: str
    person_code: str
    relationship_code: str
    date_of_birth: date
    first_name: str
    last_name: str
    gender: Literal["M", "F", "U", "X"]

    # From claims
    service_date: date

    # From enrollments
    reference_number: int

    # From products
    upc: str
    ingredient_cost: Decimal
    dispensing_fee: Decimal
    usual_and_customary_charge: Decimal
    gross_amount_due: Decimal
    days_supply: int = 365
    quantity: int = 1


def build_transmission_dict(claim: NcpdpClaimInput) -> dict:
    """Convert a validated NcpdpClaimInput into the transmission dict
    that encoders.Transmission.format() expects.
    """
    service_date_int = _ncpdp_date(claim.service_date)

    return {
        "header": {
            "bin_number": int(claim.bin_number),
            "date_of_service": service_date_int,
            "processor_control_number": claim.rx_group,
            "service_provider_id": BIG_HEALTH_PHARMACY_ID,
            "service_provider_id_qualifier": "01",
            "software_vendor_certification_id": BIG_HEALTH_NCPDP_CERTIFICATION_ID,
            "transaction_code": "B1",
            "transaction_count": "1",
        },
        "segments": [
            {
                "segment_identification": "04",
                "cardholder_id": claim.caremark_id,
                "group_id": claim.rx_group,
                "person_code": claim.person_code,
                "patient_relationship_code": int(claim.relationship_code),
            },
            {
                "segment_identification": "01",
                "date_of_birth": _ncpdp_date(claim.date_of_birth),
                "patient_gender_code": GENDER_TO_NCPDP[claim.gender],
                "patient_first_name": claim.first_name[:FIRST_NAME_MAX_LEN],
                "patient_last_name": claim.last_name[:LAST_NAME_MAX_LEN],
            },
        ],
        "transactions": [
            {
                "segments": [
                    {
                        "segment_identification": "07",
                        "prescription_service_reference_number_qualifier": "1",
                        "prescription_service_reference_number": claim.reference_number,
                        "product_service_id_qualifier": "03",
                        "product_service_id": claim.upc,
                        "quantity_dispensed": claim.quantity * 1000,
                        "fill_number": 0,
                        "days_supply": claim.days_supply,
                        "compound_code": 1,
                        "daw_product_selection_code": "0",
                        "date_prescription_written": service_date_int,
                        "number_of_refills_authorized": 0,
                        "prescription_origin_code": 0,
                        "other_coverage_code": "0",
                    },
                    {
                        "segment_identification": "11",
                        "ingredient_cost_submitted": claim.ingredient_cost,
                        "dispensing_fee_submitted": claim.dispensing_fee,
                        "usual_and_customary_charge": claim.usual_and_customary_charge,
                        "gross_amount_due": claim.gross_amount_due,
                        "basis_of_cost_determination": "00",
                    },
                ]
            }
        ],
    }
