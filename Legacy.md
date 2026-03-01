# Legacy NCPDP Encoding Architecture

Reference documentation for the NCPDP D.0 encoding system in `cvs-integration-service-cluster`, to guide porting the encoder into `bh-rcm-py`.

Source: `cvs-integration-service-cluster/src/big_health/services/cvs/true_claims/encoders.py` and siblings.

---

## Overview

The legacy encoder serializes Python dicts into NCPDP D.0 flat-file format for submission to CVS Caremark, and parses CVS response files back into dicts. The entire pipeline is:

1. **Claim dict assembly** (`claim_service.py` `CaremarkMemberClaim.ncpdp_billing_claim()`) builds a nested dict with `header`, `segments`, and `transactions` keys.
2. **Encoding** (`encoders.py` `Transmission.format()`) serializes that dict into a flat-file string.
3. **Batching** (`batch.py` `format_to()`) resolves each claim's service date (from the claim's `service_date` column if set, otherwise `datetime.date.today()`), then writes multiple encoded transmissions into a batch file, each prefixed with `\x02G1` + 10 spaces and terminated with `\n`.
4. **Delivery** (`claim_delivery_service.py` `ClaimDeliveryManager.prepare()`) gathers triggered claims, streams to a temp file, uploads to S3, then SFTP to CVS.
5. **Response parsing** (`batch.py` `parse_from()` -> `Transmission.parse()`) reads CVS response files back into dicts.
6. **Confirmation** (`claim_delivery_service.py` `ClaimDeliveryManager.confirm()` -> `CaremarkMemberClaimManager.process_true_claim_response()`) updates claim status based on the response.

---

## Transmission Structure

A **Transmission** is the top-level unit. Its dict shape is:

```python
{
    "header": { ... },          # RequestHeader or ResponseHeader fields
    "segments": [ ... ],        # Top-level segments (Insurance, Patient)
    "transactions": [           # One or more transactions
        {
            "segments": [ ... ] # Per-transaction segments (Claim, Pricing)
        }
    ]
}
```

Serialized form: `<header><top-segments><GS><transaction-segments>[<GS><transaction-segments>...]`

Where `GS` = `\x1D` (Group Separator).

---

## Separator Characters

| Name              | Hex    | Python | Usage                           |
|-------------------|--------|--------|---------------------------------|
| Field Separator   | `\x1C` | `FS`   | Between field ID and next field |
| Segment Separator | `\x1E` | `RS`   | Before each segment             |
| Group Separator   | `\x1D` | `GS`   | Before each transaction         |
| Row Incipit       | `\x02` | `STX`  | Batch file row start: `\x02G1` + 10 spaces |

---

## Field Types

### `Alphanumeric`

- **Padding**: space (` `), left-aligned
- **Allowed characters**: `0-9 A-Z ~ \` ! @ # $ % ^ & * ( ) _ - = + \ | { [ ] } : , < . > / ? ; ' "`
- **Formatting**: uppercased, right-stripped, then padded to `width` if specified
- **Parsing**: right-strip spaces

### `Numeric`

- **Padding**: `0`, right-aligned
- **Constraint**: unsigned integers only (>= 0)
- **Formatting**: `str(number)`, zero-padded to `width`
- **Parsing**: `int(string)`, returns 0 for empty

### `Dollar`

- **Padding**: `0`, right-aligned
- **Representation**: 2-decimal-place number with the decimal point removed, sign encoded in the last character via EBCDIC overpunch convention
- **Formatting**:
  1. Round to 2 decimal places
  2. Remove the decimal point -> e.g. `400.00` -> `"40000"`
  3. Replace the last digit with an overpunch character encoding the sign
- **Overpunch map** (positive/negative):

| Digit | Positive | Negative |
|-------|----------|----------|
| 0     | `{`      | `}`      |
| 1     | `A`      | `J`      |
| 2     | `B`      | `K`      |
| 3     | `C`      | `L`      |
| 4     | `D`      | `M`      |
| 5     | `E`      | `N`      |
| 6     | `F`      | `O`      |
| 7     | `G`      | `P`      |
| 8     | `H`      | `Q`      |
| 9     | `I`      | `R`      |

- **Example**: `$400.00` (positive) -> `"4000{"`; `$-3.50` (negative) -> `"35}"`

---

## Segment Architecture

### Registry Pattern

`_SegmentRegistry` (a metaclass) auto-registers every `BaseSegment` subclass that has a non-empty `segment_identification` into `SEGMENTS = {}`. This enables `BaseSegment.segment_for_id("07")` to return `ClaimSegment`.

### Field Definition

Each segment declares `fields` as a list of tuples: `(field_id, field_name, field_type, required=True, width=None)`. The metaclass prepends an `OutputField("AM", "segment_identification", Alphanumeric)` to every segment.

A `Field` serializes as: `<FS><field_id><formatted_value>` where `FS` = `\x1C`.

An `OutputField` is format-only (not used in parsing or __init__).

### BaseSegment.format()

```
<RS> + join(field.format(value) for each field if value is not None)
```

Where `RS` = `\x1E` (Segment Separator).

### BaseSegment.parse()

Splits on `FS` (`\x1C`), reads the first 2 chars of each chunk as the field ID, looks up the segment class from the `AM` field, and hydrates the remaining fields by name.

### Pseudo-Segments

Several classes subclass `BaseSegment` with `segment_identification = None` so they don't enter the registry. They are sub-structures that serialize inline within their parent segment:

- `OtherPayment` — within `COBOtherPaymentSegment` (05)
- `BenefitStages` — within `OtherPayment`
- `OtherPayerPatientResponsibilityAmount` — within `OtherPayment`
- `Ingredient` — within `CompoundSegment` (10)
- `ModifierCodes` — within `CompoundSegment` (10)
- `Question` — within `AdditionalDocumentationSegment` (14)

These strip the leading `RS` via `.lstrip(SEGMENT_SEPARATOR)` and format inline after their parent.

---

## Segment Catalog

### Request Segments

| ID | Class | Purpose |
|----|-------|---------|
| — | `RequestHeader` | Fixed-length 56-char header (no segment ID, no field separators) |
| 01 | `PatientSegment` | Patient demographics |
| 02 | `PharmacyProviderSegment` | Pharmacy provider (testing only) |
| 03 | `PrescriberSegment` | Prescriber info |
| 04 | `InsuranceSegment` | Cardholder/insurance info |
| 05 | `COBOtherPaymentSegment` | Coordination of benefits |
| 07 | `ClaimSegment` | Claim detail (Rx reference, UPC, quantity, days supply) |
| 08 | `DURPPSSegment` | Drug utilization review |
| 10 | `CompoundSegment` | Compound ingredient details |
| 11 | `PricingSegment` | Submitted pricing (ingredient cost, dispensing fee, U&C, gross due) |
| 13 | `ClinicalSegment` | Diagnosis codes and clinical measurements |
| 14 | `AdditionalDocumentationSegment` | Supporting documentation / questions |
| 15 | `FacilitySegment` | Facility info |
| 16 | `NarrativeSegment` | Narrative message |

### Response Segments

| ID | Class | Purpose |
|----|-------|---------|
| — | `ResponseHeader` | Fixed-length 31-char header |
| 20 | `ResponseMessageSegment` | Textual message |
| 21 | `ResponseStatusSegment` | Paid / Rejected / Duplicated status + reject codes |
| 22 | `ResponseClaimSegment` | Claim reference echo-back |
| 23 | `ResponsePricingSegment` | Adjudicated pricing (paid amounts, copay, deductible) |
| 24 | `ResponseDURPPSSegment` | DUR response |
| 25 | `ResponseInsuranceSegment` | Insurance info echo-back |
| 26 | `ResponsePriorAuthorizationSegment` | PA number assigned |
| 28 | `ResponseCOBSegment` | COB other-payer info |
| 29 | `ResponsePatientSegment` | Patient info echo-back |

---

## Headers

### RequestHeader (56 chars, fixed-width, no separators)

| Offset | Width | Field | Type |
|--------|-------|-------|------|
| 0 | 6 | bin_number | Numeric |
| 6 | 2 | version ("D0") | Alphanumeric |
| 8 | 2 | transaction_code | Alphanumeric |
| 10 | 10 | processor_control_number | Alphanumeric |
| 20 | 1 | transaction_count | Alphanumeric |
| 21 | 2 | service_provider_id_qualifier | Alphanumeric |
| 23 | 15 | service_provider_id | Alphanumeric |
| 38 | 8 | date_of_service | Numeric |
| 46 | 10 | software_vendor_certification_id | Alphanumeric |

### ResponseHeader (31 chars, fixed-width, no separators)

| Offset | Width | Field | Type |
|--------|-------|-------|------|
| 0 | 2 | version ("D0") | Alphanumeric |
| 2 | 2 | transaction_code | Alphanumeric |
| 4 | 1 | transaction_count | Alphanumeric |
| 5 | 1 | header_response_status | Alphanumeric |
| 6 | 2 | service_provider_id_qualifier | Alphanumeric |
| 8 | 15 | service_provider_id | Alphanumeric |
| 23 | 8 | date_of_service | Numeric |

---

## Claim Dict Assembly

`CaremarkMemberClaim.ncpdp_billing_claim(service_date)` builds the dict used by `Transmission.format()`. The claim must be test-claim-verified and true-claim-triggered.

### Header values

- `bin_number`: from claim record
- `transaction_code`: `"B1"` (billing)
- `processor_control_number`: `rx_group` from claim
- `service_provider_id`: `"1316418981"` (Big Health pharmacy ID)
- `service_provider_id_qualifier`: `"01"`
- `software_vendor_certification_id`: `"D0315211BH"`
- `date_of_service`: `YYYYMMDD` as integer

### Top-level segments

- **InsuranceSegment (04)**: `cardholder_id`, `group_id` (= rx_group), `patient_relationship_code`, `person_code`
- **PatientSegment (01)**: `date_of_birth`, `patient_gender_code`, `patient_first_name`, `patient_last_name`

### Transaction segments

- **ClaimSegment (07)**:
  - `prescription_service_reference_number_qualifier`: `"1"`
  - `prescription_service_reference_number`: claim's reference number
  - `product_service_id_qualifier`: `"03"` (UPC)
  - `product_service_id`: UPC resolved from product/bundle ID + legacy_pricing flag
  - `quantity_dispensed`: 1000 (= 1 unit in milli-units)
  - `fill_number`: 0
  - `days_supply`: 365 (or 14 for CVS Health org)
  - `compound_code`: 1
  - `daw_product_selection_code`: `"0"`
  - `date_prescription_written`: service date as YYYYMMDD int
  - `number_of_refills_authorized`: 0
  - `prescription_origin_code`: 0
  - `other_coverage_code`: `"0"`
- **PricingSegment (11)**:
  - `ingredient_cost_submitted`, `dispensing_fee_submitted`, `usual_and_customary_charge`, `gross_amount_due` — from pricing module
  - `basis_of_cost_determination`: `"00"`

---

## UPC Resolution

`CaremarkMemberClaim.product_upc` resolves the UPC to submit based on `product_id`, `bundle_id`, and the organization's `legacy_pricing` flag.

| Product | Legacy UPC | 2024 UPC |
|---------|-----------|----------|
| Sleepio (1) | 60001067190 | 60008003304 |
| Daylight (2) | 60001067191 | 60008033055 |
| Spark (4) | CVS_SPARK_UPC (setting) | CVS_SPARK_UPC_2024 (setting) |
| Grouped Bundle (1) | 60001067192 | 60008033079 |
| Stepped Bundle (2) | 60001067193 | 60008033062 |

---

## Pricing

`pricing.calculate(product_id, bundle_id, organization)` returns a `Pricing` namedtuple with `ingredient_cost`, `dispensing_fee`, `usual_and_customary_charge`, `gross_amount_due`.

Pricing is selected by product/bundle ID and the organization's `legacy_pricing` flag. Special case: Google org can override Sleepio pricing via org-level fields in cents.

| Product | Legacy Price | 2024 Price |
|---------|-------------|------------|
| Sleepio | $400 | $400 |
| Daylight | $400 | $430 |
| Spark | $400 | $430 |
| Grouped Bundle | $600 | $645 |
| Stepped Bundle | $200 | $215 |

All dispensing fees are $0.00. All four pricing fields (ingredient cost, dispensing fee, U&C, gross amount due) are set to the same values (fee is always 0, the other three are the product price).

---

## Claim Resolution

`resolver.resolve_receivable(claim_manager, claim)` determines which claim entity is actually billable:

1. If the org has no bundle election, the claim bills directly.
2. If the claim is already bundled, return the bundle claim.
3. `resolve_historical_bundle()` checks if the member had a previous grouped-bundle or individual-product claim, and routes to the appropriate bundle type (grouped or stepped).
4. Otherwise, delegates to the bundle's `.resolve()` method.

---

## Batch File Format

### Outgoing (to CVS)

`batch.format_to()` iterates over claims, resolving the service date per-claim: if `claim.get("service_date")` is set (a `DateTime` column added to `caremark_member_claim` in migration `dfb8a2d805e3`), that value is used; otherwise it falls back to `datetime.date.today()`. The resolved date is passed to `claim.ncpdp_billing_claim(service_date)`, which populates both the header `date_of_service` and the claim segment `date_prescription_written`.

Each row: `\x02G1` + 10 spaces + `Transmission.format(claim_dict)` + `\n`

### Incoming (from CVS)

- First line: header starting with `   R`
- Body lines: each parsed via `Transmission.parse(line)`
- Trailer: line starting with 10 spaces

---

## Delivery Lifecycle

`CaremarkClaimDelivery` progresses through four statuses:

1. **CREATED** — batch file written to S3
2. **DELIVERED** — SFTP'd to CVS
3. **RETRIEVED** — CVS response files pulled from SFTP, stored in S3
4. **CONFIRMED** — response parsed, claims updated (paid/duplicated/rejected)

Filenames follow the pattern `BGH<counter:03d><mmddyy>` where counter = `delivery.id % 1000`.

---

## Response Processing

`CaremarkMemberClaimManager.process_true_claim_response(dict)`:

1. Extracts `ResponseClaimSegment` (22) to find the claim by `prescription_service_reference_number`.
2. Extracts `ResponseStatusSegment` (21) to read `transaction_response_status`.
3. Updates the claim: `true_claim_verified_utc`, `true_claim_duplicated_utc`, or `true_claim_rejected_utc`.

---

## Key Constants

```python
BIG_HEALTH_PHARMACY_ID = "1316418981"
BIG_HEALTH_NCPDP_NUMBER = "8400018"
BIG_HEALTH_NCPDP_CERTIFICATION_ID = "D0315211BH"
VERSION_NUMBER = "D0"
ALLOWABLE_DAYS_SUPPLY = 365
CVS_ALLOWABLE_DAYS_SUPPLY = 14
ALLOWABLE_QUANTITY = 1
MIN_REPEAT_PAYMENT_REQUEST_DAYS = 345
```

---

## Porting Notes

When building the encoder in `bh-rcm-py`:

- The `Dollar` type with EBCDIC overpunch is the most complex formatting piece. Port it carefully with good test coverage.
- The `_SegmentRegistry` metaclass pattern is clever but optional — a simple dict mapping segment IDs to classes works equally well.
- Pseudo-segments (Ingredient, OtherPayment, etc.) don't have their own segment separator prefix — they serialize inline. Watch for the `.lstrip(SEGMENT_SEPARATOR)` calls.
- Headers are fixed-width with no field separators. Every other segment uses field separators.
- The `Field.format()` method returns `None` for non-required fields that are `None`, which `filter(None, ...)` removes from the output.
- Date fields are integers in `YYYYMMDD` format: `int(date.strftime("%Y%m%d"))`.
- `quantity_dispensed` is in milli-units (multiply by 1000). `compound_ingredient_quantity` similarly (`float * 1000`, cast to int).
