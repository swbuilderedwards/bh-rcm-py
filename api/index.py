import sys
import logging

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    force=True,
)
logger = logging.getLogger(__name__)

import io

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from lib.ncpdp import batch, encoders
from lib.ncpdp.adapter import NcpdpClaimInput, build_transmission_dict
from lib.ncpdp.adjudicator import adjudicate_batch

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/claims/ncpdp/encode")
def encode_claim(claim: NcpdpClaimInput):
    td = build_transmission_dict(claim)
    encoded = encoders.Transmission.format(td)
    return {"encoded": encoded}


@app.post("/api/claims/ncpdp/batch")
def batch_claims(claims: list[NcpdpClaimInput]):
    transmission_dicts = [build_transmission_dict(c) for c in claims]
    content = batch.format_batch(transmission_dicts)
    return PlainTextResponse(content)


@app.post("/api/claims/ncpdp/parse-response")
async def parse_response(file: UploadFile = File()):
    try:
        transmissions = list(batch.parse_from(file.file))
    except (AssertionError, Exception) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {exc}")
    return {"transmissions": transmissions}


@app.post("/api/claims/ncpdp/stub-adjudicate")
async def stub_adjudicate(request: Request):
    body = await request.body()
    batch_text = body.decode("utf-8")
    try:
        response_text = adjudicate_batch(batch_text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Adjudication failed: {exc}")
    return PlainTextResponse(response_text)


@app.post("/api/claims/ncpdp/parse-response-text")
async def parse_response_text(request: Request):
    body = await request.body()
    try:
        filestream = io.BytesIO(body)
        transmissions = list(batch.parse_from(filestream))
    except (AssertionError, Exception) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid response format: {exc}")
    return {"transmissions": transmissions}
