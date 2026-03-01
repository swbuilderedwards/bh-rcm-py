"""This module simplifies working with batch claims submission."""
from lib.ncpdp import encoders


BATCH_ROW_PREFIX = "\x02G1" + " " * 10

TRAILER_INCIPIT = b"          "


def for_certification_format_claim_dicts_to(filestream, claim_dicts):
    """This function exists for, and is solely called by, the NCPDP
    certification code.

    """
    for c in claim_dicts:
        filestream.write(encoders.Transmission.format(c, enforce_types=False))
        filestream.write("\n")
    filestream.flush()


def format_batch(transmission_dicts: list[dict]) -> str:
    lines = []
    for td in transmission_dicts:
        lines.append(BATCH_ROW_PREFIX + encoders.Transmission.format(td))
    return "\n".join(lines) + "\n"


RESPONSE_HEADER_LINE = "   R" + " " * 2000

RESPONSE_TRAILER_LINE = "0000000000"


def format_response_batch(response_dicts: list[dict]) -> str:
    """Format response transmission dicts into a batch response that parse_from() can read.

    Structure:
    - Line 1: header starting with "   R" (padded to match real CVS responses)
    - Lines 2–N: one encoded transmission per response dict (each starts with "D0")
    - Last line: trailer "0000000000" (stops parse_from because it doesn't start with "D0")
    """
    lines = [RESPONSE_HEADER_LINE]
    for rd in response_dicts:
        lines.append(encoders.Transmission.format(rd, enforce_types=False))
    lines.append(RESPONSE_TRAILER_LINE)
    return "\n".join(lines) + "\n"


def parse_from(filestream):
    """Given a filestream of a NCPDP batch file, attempt to parse multiple
    transmissions out of it.
    """
    for header in filestream:
        assert header.startswith(b"   R")
        break

    for line in filestream:
        if line.startswith(TRAILER_INCIPIT) or not line.startswith(
            encoders.VERSION_NUMBER.encode()
        ):
            # This identifies the trailer.
            break
        yield encoders.Transmission.parse(line.decode("utf-8").rstrip())
