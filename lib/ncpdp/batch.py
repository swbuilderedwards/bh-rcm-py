"""This module simplifies working with batch claims submission."""
from lib.ncpdp import encoders


TRAILER_INCIPIT = b"          "


def for_certification_format_claim_dicts_to(filestream, claim_dicts):
    """This function exists for, and is solely called by, the NCPDP
    certification code.

    """
    for c in claim_dicts:
        filestream.write(encoders.Transmission.format(c, enforce_types=False))
        filestream.write("\n")
    filestream.flush()


def parse_from(filestream):
    """Given a filestream of a NCPDP batch file, attempt to parse multiple
    transmissions out of it.
    """
    for header in filestream:
        assert header.startswith(b"   R")
        break

    for line in filestream:
        if line.startswith(TRAILER_INCIPIT):
            # This identifies the trailer.
            break
        yield encoders.Transmission.parse(line.decode("utf-8").rstrip())
