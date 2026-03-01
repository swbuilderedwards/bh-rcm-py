"""CVS PBM Stub adjudication logic.

Parses NCPDP request transmissions and builds response transmission dicts
with coin-flip paid/rejected results.
"""
import random

from lib.ncpdp import batch, encoders

REJECT_CODES = ["75", "70", "65", "25"]


def adjudicate_transmission(request_td: dict) -> dict:
    """Given a parsed request transmission dict, build a response transmission dict.

    - ResponseHeader: transaction_code="B1", header_response_status="A",
      echoes service_provider_id and date_of_service
    - Segment 21 (ResponseStatusSegment): 50/50 paid ("P") or rejected ("R")
    - Segment 22 (ResponseClaimSegment): echoes prescription_service_reference_number
    - Segment 23 (ResponsePricingSegment): if paid, echoes submitted pricing amounts
    """
    req_header = request_td["header"]

    # Find segment 07 (ClaimSegment) in the first transaction
    claim_segment = None
    pricing_segment = None
    for tx in request_td.get("transactions", []):
        for seg in tx.get("segments", []):
            if seg.get("segment_identification") == "07":
                claim_segment = seg
            elif seg.get("segment_identification") == "11":
                pricing_segment = seg

    ref_number = claim_segment["prescription_service_reference_number"] if claim_segment else 0

    # Coin flip: 50% paid, 50% rejected
    is_paid = random.random() < 0.5

    # Build response segments
    segments = []

    # Segment 21 — ResponseStatusSegment
    status_seg = {
        "segment_identification": "21",
        "transaction_response_status": "P" if is_paid else "R",
    }
    if not is_paid:
        status_seg["reject_count"] = "1"
        status_seg["reject_code"] = random.choice(REJECT_CODES)
    segments.append(status_seg)

    # Segment 22 — ResponseClaimSegment
    segments.append({
        "segment_identification": "22",
        "prescription_service_reference_number_qualifier": "1",
        "prescription_service_reference_number": ref_number,
    })

    # Segment 23 — ResponsePricingSegment (only if paid)
    if is_paid and pricing_segment:
        segments.append({
            "segment_identification": "23",
            "patient_pay_amount": 0,
            "ingredient_cost_paid": pricing_segment.get("ingredient_cost_submitted", 0),
            "dispensing_fee_paid": pricing_segment.get("dispensing_fee_submitted", 0),
            "total_amount_paid": pricing_segment.get("gross_amount_due", 0),
            "basis_of_reimbursement_determination": "03",
            "amount_applied_to_periodic_deductible": 0,
            "other_amount_paid_count": 0,
            "other_amount_paid_qualifier": "00",
        })

    return {
        "header": {
            "transaction_code": "B1",
            "transaction_count": "1",
            "header_response_status": "A",
            "service_provider_id_qualifier": "01",
            "service_provider_id": str(req_header.get("service_provider_id", "")),
            "date_of_service": req_header.get("date_of_service", 0),
        },
        "segments": segments,
        "transactions": [],
    }


def adjudicate_batch(batch_text: str) -> str:
    """Parse an NCPDP request batch, adjudicate each transmission, return NCPDP response batch."""
    lines = batch_text.strip().split("\n")
    prefix = batch.BATCH_ROW_PREFIX

    request_transmissions = []
    for line in lines:
        if line.startswith(prefix):
            raw = line[len(prefix):]
            request_transmissions.append(encoders.Transmission.parse(raw))

    response_dicts = [adjudicate_transmission(rt) for rt in request_transmissions]
    return batch.format_response_batch(response_dicts)
