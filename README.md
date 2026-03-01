# bh-rcm-py

Python backend for Big Health's Revenue Cycle Management system. Encodes pharmacy claims into NCPDP D.0 flat-file format for submission to CVS Caremark and exposes API endpoints as Vercel serverless functions.

## Architecture

```
bh-rcm Supabase data  ──►  NcpdpClaimInput  ──►  build_transmission_dict()  ──►  encoders.Transmission.format()
     (patients, claims,       (pydantic            (adapter.py)                    (legacy encoder,
      products, enrollments)   validation)                                          copied verbatim)
```

### Project structure

```
bh-rcm-py/
├── api/
│   └── index.py                # FastAPI app (Vercel entry point)
├── lib/ncpdp/
│   ├── adapter.py              # Bridge from Supabase data model → NCPDP transmission dict
│   ├── batch.py                # Batch file formatting and response parsing
│   └── encoders.py             # NCPDP D.0 encoder/decoder (field types, segments, headers)
├── tests/ncpdp/
│   ├── test_adapter.py         # Adapter unit tests
│   ├── test_encoders.py        # Encoder unit tests (Dollar, Numeric, Alphanumeric, segments)
│   ├── test_encoders_b1.py     # B1 billing request/response round-trip tests
│   ├── test_encoders_b2.py     # B2 reversal request/response round-trip tests
│   ├── test_ncpdp_certification.py  # Golden file certification test
│   └── data/                   # Test fixtures (certification claims, golden files)
├── pyproject.toml
├── requirements.txt
└── vercel.json
```

### Key modules

- **`lib/ncpdp/encoders.py`** — Battle-tested NCPDP D.0 encoder/decoder copied from `cvs-integration-service-cluster`. Handles field types (Alphanumeric, Numeric, Dollar with EBCDIC overpunch), segment serialization, and header formatting. Stdlib only — no external dependencies.

- **`lib/ncpdp/adapter.py`** — Thin bridge layer. `NcpdpClaimInput` is a pydantic model that validates all required fields upfront (patient info, claim details, product pricing). `build_transmission_dict()` converts it into the dict that `encoders.Transmission.format()` expects.

- **`lib/ncpdp/batch.py`** — Utilities for batch NCPDP files: `parse_from()` reads batch response files, `for_certification_format_claim_dicts_to()` writes certification test output.

## Deployment

Deployed as **Vercel Python serverless functions**.

- **Runtime:** Python 3.13
- **Entry point:** `api/index.py` — a FastAPI app
- **Routing:** All requests route to the FastAPI app via `vercel.json`

```bash
# Local development
vercel dev

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Tests

102 tests covering the encoder, adapter, and NCPDP certification:

| Test file | What it covers | Count |
|---|---|---|
| `test_encoders.py` | Field types, segment format/parse, headers | 82 |
| `test_encoders_b1.py` | B1 billing request/response round-trips | 3 |
| `test_encoders_b2.py` | B2 reversal request/response round-trips | 4 |
| `test_ncpdp_certification.py` | Golden file match (30 certification claims) | 1 |
| `test_adapter.py` | Adapter validation, dict shape, encoder round-trip | 12 |

### Running tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run just the NCPDP tests
pytest tests/ncpdp/

# Run a specific test file
pytest tests/ncpdp/test_encoders.py -v

# Run with output
pytest tests/ncpdp/ -v
```

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework for API endpoints |
| `pydantic` | Data validation for `NcpdpClaimInput` |
| `pytest` | Test runner |
| `freezegun` | Time mocking for certification test |
