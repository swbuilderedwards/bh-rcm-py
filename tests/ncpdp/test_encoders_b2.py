"""Additional tests for the NCPDP encoders module: the B2 transaction."""
from lib.ncpdp import encoders


SPECIMEN_B2_TRANSMISSION_REQUEST_DICT = {
    "header": {
        "bin_number": 610066,
        "transaction_code": "B2",
        "processor_control_number": "1234567890",
        "transaction_count": "1",
        "service_provider_id_qualifier": "01",
        "service_provider_id": "4563663111",
        "date_of_service": 20070915,
        "software_vendor_certification_id": "98765",
    },
    "segments": [],
    "transactions": [
        {
            "segments": [
                {
                    "segment_identification": "07",
                    "prescription_service_reference_number_qualifier": "1",
                    "prescription_service_reference_number": 1234567,
                    "product_service_id_qualifier": "03",
                    "product_service_id": "00006094268",
                }
            ]
        }
    ],
}

SPECIMEN_B2_TRANSMISSION_REQUEST_BODY = (
    """610066D0B212345678901014563663111     2007091598765     \x1d\x1E\x1CAM07\x1CEM1\x1CD21234567\x1CE103\x1CD700006094268"""  # noqa: E501
)


def test_b2_request_encoding():
    assert encoders.Transmission.format(SPECIMEN_B2_TRANSMISSION_REQUEST_DICT) == SPECIMEN_B2_TRANSMISSION_REQUEST_BODY


def test_b2_request_decoding():
    assert encoders.Transmission.parse(SPECIMEN_B2_TRANSMISSION_REQUEST_BODY) == SPECIMEN_B2_TRANSMISSION_REQUEST_DICT


SPECIMEN_B2_TRANSMISSION_REVERSAL_ACCEPTED_RESPONSE_BODY = """D0B21A014563663111     20070915\x1E\x1CAM20\x1CF4TRANSMISSION MESSAGE TEXT\x1D\x1E\x1CAM21\x1CANC\x1E\x1CAM22\x1CEM1\x1CD21234567"""  # noqa: E501


SPECIMEN_B2_TRANSMISSION_REVERSAL_ACCEPTED_RESPONSE_DICT = {
    "header": {
        "transaction_code": "B2",
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
                {"segment_identification": "21", "transaction_response_status": "C"},
                {
                    "segment_identification": "22",
                    "prescription_service_reference_number_qualifier": "1",
                    "prescription_service_reference_number": 1234567,
                },
            ]
        }
    ],
}


def test_b2_response_encoding():
    assert (
        encoders.Transmission.format(SPECIMEN_B2_TRANSMISSION_REVERSAL_ACCEPTED_RESPONSE_DICT)
        == SPECIMEN_B2_TRANSMISSION_REVERSAL_ACCEPTED_RESPONSE_BODY
    )


def test_b2_response_decoding():
    assert (
        encoders.Transmission.parse(SPECIMEN_B2_TRANSMISSION_REVERSAL_ACCEPTED_RESPONSE_BODY)
        == SPECIMEN_B2_TRANSMISSION_REVERSAL_ACCEPTED_RESPONSE_DICT
    )
