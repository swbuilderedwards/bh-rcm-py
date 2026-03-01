import io
from pathlib import Path

import freezegun

from tests.ncpdp.data import ncpdp_certification


class TestNCPDPCertification:
    """This test just runs the ncpdp certification code, and asserts that it
    matches a previously-minted golden file.
    """

    def test_output_matches_golden_file(self):
        buf = io.StringIO()

        with freezegun.freeze_time("2020-02-26"):
            ncpdp_certification.run_claims(buf)
        buf.seek(0)

        golden_path = Path(__file__).parent / "data" / "golden_submission.ncpdp"
        assert golden_path.read_text() == buf.read()
