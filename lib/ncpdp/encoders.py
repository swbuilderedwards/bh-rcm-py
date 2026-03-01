"""Encoders take a dict representation of the NCPDP file and convert them to the
flat file representation associated with them.
"""
from collections import namedtuple
from decimal import Decimal
import itertools
import logging
import math
import typing


logger = logging.getLogger(__name__)


VERSION_NUMBER = "D0"


ALIGN_LEFT = True
ALIGN_RIGHT = False


class Dollar:
    """Dollar represents a 2-dp number as a string, with the interpolated
    decimal removed (implicitly specified) and the sign of the figure
    represented on the last character according to the lost lore of EBCIDIC.
    """

    PADDING = "0"
    ALIGN = ALIGN_RIGHT

    # Maps from a tuple, (n >= 0, str(n)), to the character that should be used to replace n.
    SIGN_LAST_CHAR_TO_OVERPUNCH_MAP = {
        (True, "0"): "{",
        (True, "1"): "A",
        (True, "2"): "B",
        (True, "3"): "C",
        (True, "4"): "D",
        (True, "5"): "E",
        (True, "6"): "F",
        (True, "7"): "G",
        (True, "8"): "H",
        (True, "9"): "I",
        (False, "0"): "}",
        (False, "1"): "J",
        (False, "2"): "K",
        (False, "3"): "L",
        (False, "4"): "M",
        (False, "5"): "N",
        (False, "6"): "O",
        (False, "7"): "P",
        (False, "8"): "Q",
        (False, "9"): "R",
    }

    OVERPUNCH_TO_SIGN_LAST_CHAR_MAP = {symbol: (sign, last_char) for (sign, last_char), symbol in SIGN_LAST_CHAR_TO_OVERPUNCH_MAP.items()}

    @classmethod
    def format(cls, amount: typing.Union[int, float, Decimal], width: int = None, enforce_types: bool = True,) -> str:
        """Returns the correct representation of this dollar amount in NCPDP
        format.

        Raises:
            TypeError: if called with a non-numeric argument.
            OverflowError: if called with +/- Infinity.
        """
        if enforce_types:
            if not isinstance(amount, (int, float, Decimal)):
                raise TypeError("Call this function only with numbers, not %s" % type(amount))
        else:
            amount = Decimal(amount)

        cents = amount * 100
        if int(cents) != cents:
            # This could be a float precision error. If you landed here looking
            # for the problem, consider formatting your field as a Decimal
            # instead.
            raise ValueError("Amount to be encoded must be whole cents, not (%s)." % amount)
        non_negative = cents >= 0
        if not non_negative:
            cents *= -1
        cents = math.floor(cents)
        cents_str = "{0:02d}".format(cents)

        output = cents_str[:-1] + Dollar.SIGN_LAST_CHAR_TO_OVERPUNCH_MAP[non_negative, cents_str[-1]]

        return ensure_width(output, cls.PADDING, width, cls.ALIGN)

    @staticmethod
    def parse(string: str) -> Decimal:
        """Parse the string representing a Dollar value, and return a Decimal.

        Raises:
            ValueError: If the string was not a valid Overpunch character.

        """
        try:
            non_negative, last_char = Dollar.OVERPUNCH_TO_SIGN_LAST_CHAR_MAP[string[-1:]]
        except KeyError:
            raise ValueError("Unknown overpunch symbol in string: %s" % string)

        if not non_negative:
            string = "-" + string

        return Decimal(string[:-2] + "." + string[-2] + last_char)


class Alphanumeric:
    """Alphanumeric Fields are ...? What are the reenforce_typesions."""

    PADDING = " "
    ALIGN = ALIGN_LEFT

    ALLOWED_CHARACTERS = set(r''' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ~`!@#$%^&*()_-=+\|{[]}:,<.>/?;'"''')

    @classmethod
    def format(cls, string: str, width: int = None, enforce_types: bool = True) -> str:
        if enforce_types:
            if not isinstance(string, str):
                raise TypeError("Call this function only with strings, not %s" % type(string))
        elif string is None:
            # Never allow None
            raise TypeError("Call this function only with strings, not %s" % type(string))
        else:
            if not isinstance(string, str):
                string = str(string)

        string = string.upper()

        disallowed_characters = {char for char in string if char not in Alphanumeric.ALLOWED_CHARACTERS}
        if disallowed_characters:
            raise ValueError("Unexpcted characters found: %s" % disallowed_characters)
        output = string.rstrip()
        return ensure_width(output, cls.PADDING, width, cls.ALIGN)

    @staticmethod
    def parse(string: str) -> str:
        if not isinstance(string, str):
            raise TypeError("Call this function only with strings, not %s" % type(string))

        return string.rstrip()


class Numeric:
    """Numeric represents unsigned whole numbers. Their textual representations
    are always right justified, and zero-filled, if the field is fixed-width.
    """

    PADDING = "0"
    ALIGN = ALIGN_RIGHT

    @classmethod
    def format(cls, number: int, width: int = None, enforce_types: bool = True) -> str:
        if enforce_types:
            if not isinstance(number, int):
                raise TypeError("Numeric values must be integers only, not %s" % type(number))
        else:
            number = int(number)

        if number < 0:
            raise ValueError("Numeric values must be non-negative, not %s" % number)

        output = str(number)

        return ensure_width(output, cls.PADDING, width, cls.ALIGN)

    @staticmethod
    def parse(string: str) -> int:
        if not string:
            return 0

        return int(string)


class Field(namedtuple("Field", ["id", "name", "type", "required", "width"])):
    """This class is used to store practically relevent details
    associated with an NCPDPD field of a Segment.
    """

    def __new__(self, id, name, type, required=True, width=None):
        """Because Field is a subclass of namedtuple, it overrides __new__ instead of __init__."""
        return super().__new__(self, id, name, type, required, width)

    def format(self, value, enforce_types=True):
        if not self.required and value is None:
            # Special return value allows us to skip non-required and None values.
            return None
        try:
            return FIELD_SEPARATOR + self.id + self.type.format(value, width=self.width, enforce_types=enforce_types)
        except (ValueError, TypeError) as e:
            raise ValueError("Failed to format %s" % self.name) from e

    def parse(self, *args, **kwargs):
        return self.type.parse(*args, **kwargs)


class Transmission:
    """A transmission is the entire file that we send to NCPDPD---or that we receive.."""

    @staticmethod
    def format(transmission_dict, enforce_types=True):
        header_dict = transmission_dict["header"]
        if "header_response_status" in header_dict:
            header = ResponseHeader(**header_dict)
        else:
            header = RequestHeader(**header_dict)

        formatted_header = header.format(enforce_types=enforce_types)
        formatted_transaction_segments = "".join(
            BaseSegment.segment_for_id(segment_dict["segment_identification"])(**segment_dict).format(enforce_types=enforce_types)
            for segment_dict in transmission_dict["segments"]
        )

        transactions = [Transaction(transaction_dict) for transaction_dict in transmission_dict["transactions"]]

        formatted_transactions = "".join(transaction.format(enforce_types=enforce_types) for transaction in transactions)

        return formatted_header + formatted_transaction_segments + formatted_transactions

    @staticmethod
    def parse(string):
        """Parse the header, parse the transactions, and then for each
        transaction, parse the segments.
        """
        result = {}

        if string.startswith(VERSION_NUMBER):
            header = ResponseHeader.parse(string[: ResponseHeader.MAX_SIZE])
            result["header"] = header.to_dict()
            rest = string[ResponseHeader.MAX_SIZE :]
        else:
            header = RequestHeader.parse(string[: RequestHeader.MAX_SIZE])
            result["header"] = header.to_dict()
            rest = string[RequestHeader.MAX_SIZE :]

        top_segments, *transactions = rest.split(GROUP_SEPARATOR)

        result["segments"] = []

        for unparsed_segment in filter(None, top_segments.split(SEGMENT_SEPARATOR)):
            result["segments"].append(BaseSegment.parse(unparsed_segment).to_dict())

        # TODO(danver): Decide if you want to delegate this to a `parse` method
        # inside of transactions.
        result["transactions"] = []
        for unparsed_transaction in filter(None, transactions):
            segment_list = []
            result["transactions"].append({"segments": segment_list})
            for unparsed_segment in filter(None, unparsed_transaction.split(SEGMENT_SEPARATOR)):
                segment_list.append(BaseSegment.parse(unparsed_segment).to_dict())

        return result


class RequestHeader:
    """The first segment of every transmission.

    Does not have a Segment Identifier since it is a fixed field and length
    segment.

    In the RequestHeader Segment, all fields are required positionally and filled to their
    maximum designation. This is a fixed segment. If a required field is not used in
    the RequestHeader Segment, it must be filled with spaces or zeroes, as appropriate. The
    fields within the RequestHeader Segment do not use field separators.
    """

    MAX_SIZE = 56

    fields = [
        Field(*args)
        for args in [
            ("", "bin_number", Numeric),
            ("", "transaction_code", Alphanumeric),
            ("", "processor_control_number", Alphanumeric),
            ("", "transaction_count", Alphanumeric),
            ("", "service_provider_id_qualifier", Alphanumeric),
            ("", "service_provider_id", Alphanumeric),
            ("", "date_of_service", Numeric),
            ("", "software_vendor_certification_id", Alphanumeric),
        ]
    ]

    def __init__(self, *args, **kwargs):
        for arg, field in zip(args, self.fields):
            kwargs[field.name] = arg

        for field in self.fields:
            setattr(self, field.name, kwargs.get(field.name))

    def format(self, enforce_types=True):
        return "".join(
            [
                Numeric.format(self.bin_number, 6, enforce_types=enforce_types),
                Alphanumeric.format(VERSION_NUMBER, 2, enforce_types=enforce_types),
                Alphanumeric.format(self.transaction_code, 2, enforce_types=enforce_types),
                Alphanumeric.format(self.processor_control_number, 10, enforce_types=enforce_types),
                Alphanumeric.format(self.transaction_count, 1, enforce_types=enforce_types),
                Alphanumeric.format(self.service_provider_id_qualifier, 2, enforce_types=enforce_types),
                Alphanumeric.format(self.service_provider_id, 15, enforce_types=enforce_types),
                Numeric.format(self.date_of_service, 8, enforce_types=enforce_types),
                Alphanumeric.format(self.software_vendor_certification_id, 10, enforce_types=enforce_types,),
            ]
        )

    @classmethod
    def parse(cls, string):
        assert Alphanumeric.parse(string[6:8]) == VERSION_NUMBER

        return cls(
            Numeric.parse(string[:6]),
            Alphanumeric.parse(string[8:10]),
            Alphanumeric.parse(string[10:20]),
            Alphanumeric.parse(string[20:21]),
            Alphanumeric.parse(string[21:23]),
            Alphanumeric.parse(string[23:38]),
            Numeric.parse(string[38:46]),
            Alphanumeric.parse(string[46:56]),
        )

        return cls()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        for field in self.fields:
            if getattr(self, field.name) != getattr(other, field.name):
                return False
        return True

    def __repr__(self):
        return "RequestHeader(" + ", ".join(["%s=%r" % (field.name, getattr(self, field.name, None)) for field in self.fields]) + ")"

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.fields}


class ResponseHeader:
    """The first segment of every transmitted response..

    Does not have a Segment Identifier since it is a fixed field and length
    segment.

    In the ResponseHeader Segment, all fields are required positionally and filled to their
    maximum designation. This is a fixed segment. If a required field is not used in
    the ResponseHeader Segment, it must be filled with spaces or zeroes, as appropriate. The
    fields within the RequestHeader Segment do not use field separators.
    """

    MAX_SIZE = 31

    fields = [
        Field(*args)
        for args in [
            ("", "transaction_code", Alphanumeric, True),
            ("", "transaction_count", Alphanumeric, True),
            ("", "header_response_status", Alphanumeric, True),
            ("", "service_provider_id_qualifier", Alphanumeric, True),
            ("", "service_provider_id", Alphanumeric, True),
            ("", "date_of_service", Numeric, True),
        ]
    ]

    def __init__(
        self, transaction_code, transaction_count, header_response_status, service_provider_id_qualifier, service_provider_id, date_of_service,
    ):
        self.transaction_code = transaction_code
        self.transaction_count = transaction_count
        self.header_response_status = header_response_status
        self.service_provider_id_qualifier = service_provider_id_qualifier
        self.service_provider_id = service_provider_id
        self.date_of_service = date_of_service

    def format(self, enforce_types=True):
        return "".join(
            [
                Alphanumeric.format(VERSION_NUMBER, 2, enforce_types=enforce_types),
                Alphanumeric.format(self.transaction_code, 2, enforce_types=enforce_types),
                Alphanumeric.format(self.transaction_count, 1, enforce_types=enforce_types),
                Alphanumeric.format(self.header_response_status, 1, enforce_types=enforce_types),
                Alphanumeric.format(self.service_provider_id_qualifier, 2, enforce_types=enforce_types),
                Alphanumeric.format(self.service_provider_id, 15, enforce_types=enforce_types),
                Numeric.format(self.date_of_service, 8, enforce_types=enforce_types),
            ]
        )

    @classmethod
    def parse(cls, string):
        # NOTE(danver): Consider whether it's worth it to augment Segment to
        # work with fixed-widths, so that we can parse this generically. Right
        # now, no.

        assert Alphanumeric.parse(string[0:2]) == VERSION_NUMBER

        return cls(
            Alphanumeric.parse(string[2:4]),
            Alphanumeric.parse(string[4:5]),
            Alphanumeric.parse(string[5:6]),
            Alphanumeric.parse(string[6:8]),
            Alphanumeric.parse(string[8:23]),
            Numeric.parse(string[23:31]),
        )

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.fields}

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        if (
            self.transaction_code == other.transaction_code
            and self.transaction_count == other.transaction_count
            and self.header_response_status == other.header_response_status
            and self.service_provider_id_qualifier == other.service_provider_id_qualifier
            and self.service_provider_id == other.service_provider_id
            and self.date_of_service == other.date_of_service
        ):
            return True
        return False

    def __repr__(self):
        return (
            "ResponseHeader("
            + ", ".join(
                [
                    "%s=%r" % (name, getattr(self, name, None))
                    for name in [
                        "transaction_code",
                        "transaction_count",
                        "header_response_status",
                        "service_provider_id_qualifier",
                        "service_provider_id",
                        "date_of_service",
                    ]
                ]
            )
            + ")"
        )


class Transaction:
    """A transaction aggregates multiple segments."""

    def __init__(self, transaction_dict):
        """Transactions are initialized with just a dict, and do not
        parse the dict out into an object.."""
        self.transaction_dict = transaction_dict

    def format(self, enforce_types=True):
        segments = [
            BaseSegment.segment_for_id(segment_dict["segment_identification"])(**segment_dict) for segment_dict in self.transaction_dict["segments"]
        ]

        return GROUP_SEPARATOR + "".join(segment.format(enforce_types=enforce_types) for segment in segments)

    @staticmethod
    def parse(string):
        return {}


def ensure_width(string: str, padding: str, width: int, align_left: bool):
    """For fixed-width fields, ensure that the string fits within the size."""
    if width is None:
        return string

    if len(string) > width:
        raise ValueError("Input string was too long")

    if len(padding) != 1:
        raise ValueError("Padding must be one character long.")

    required_padding = padding * (width - len(string))

    if align_left:
        return string + required_padding
    else:
        return required_padding + string


class _SegmentRegistry(type):
    """Simple registry pattern that makes it really easy to generate a
    mapping from Segment ID to the Segment and vice versa.
    """

    SEGMENTS = {}

    def __new__(cls, name, bases, namespace):
        namespace["fields"] = [OutputField("AM", "segment_identification", Alphanumeric)] + [Field(*args) for args in namespace["fields"]]

        retval = super().__new__(cls, name, bases, namespace)
        if namespace["segment_identification"]:
            cls.SEGMENTS[namespace["segment_identification"]] = retval
        return retval


class OutputField(Field):
    """Just a signifier that this field is only for output on a segment.
    OutputFields are not used as assigments during instantiation, nor are they used in parsing."""


FIELD_SEPARATOR = "\x1C"
SEGMENT_SEPARATOR = "\x1E"
GROUP_SEPARATOR = "\x1D"


class BaseSegment(metaclass=_SegmentRegistry):
    """Base Segment."""

    # For overriding by subclasses, with the segment id.
    segment_identification = ""
    fields = []

    def __init__(self, *args, **kwargs):
        for arg, field in zip(args, self.get_input_fields()):
            kwargs[field.name] = arg

        for field in self.get_input_fields():
            setattr(self, field.name, kwargs.pop(field.name, None))

        kwargs.pop("segment_identification", None)

        if kwargs:
            raise Exception(self.__class__.__name__, "unused", kwargs)

    @classmethod
    def get_input_fields(cls):
        """Only certain fields are actually read. This iterator returns only those fields."""
        yield from (field for field in cls.fields if not isinstance(field, OutputField))

    def format(self, enforce_types=True):
        return SEGMENT_SEPARATOR + "".join(
            filter(
                lambda value: value is not None,
                [field.format(getattr(self, field.name, None), enforce_types=enforce_types) for field in self.fields],
            )
        )

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(["%s=%r" % (field.name, getattr(self, field.name, None)) for field in self.fields]) + ")"

    @classmethod
    def segment_for_id(cls, id):
        return cls.SEGMENTS[id]

    @classmethod
    def parse(cls, segment_str):
        fields_to_parse = segment_str.split(FIELD_SEPARATOR)

        field_header_to_field_contents = {field_to_parse[:2]: field_to_parse[2:] for field_to_parse in fields_to_parse}

        segment_cls = cls.SEGMENTS[field_header_to_field_contents["AM"]]

        parsed_args = {}

        for field in segment_cls.get_input_fields():
            if field.id in field_header_to_field_contents:
                field_contents = field_header_to_field_contents[field.id]
                if field.name not in parsed_args:
                    try:
                        parsed_args[field.name] = field.type.parse(field_contents)
                    except Exception as e:
                        raise Exception(f"Failure parsing {field.name}") from e
                else:
                    logger.warn("Junk NCPDP: Attempting to overwrite set value.")

        return segment_cls(**parsed_args)

    def __eq__(self, other):
        """Compares two Segments for equality.

        Is not stable through serialization/deserialization. i.e.
        format(parse(a)) is not guaranteed to equal a.

        This is because of field length limits, case conversions, and
        precision errors.
        """
        if not isinstance(other, type(self)):
            return False

        for field in self.get_input_fields():
            if getattr(self, field.name) != getattr(other, field.name):
                return False

        return True

    def to_dict(self):
        """Returns a dictionary representation of this segment."""
        result = {field.name: getattr(self, field.name) for field in self.get_input_fields() if getattr(self, field.name) is not None}
        result["segment_identification"] = self.segment_identification
        return result

    @classmethod
    def select_from_transmission_dict(cls, transmission_dict):
        """Given a transmission dict, pick out the specific segment we want."""
        for segment in itertools.chain(
            transmission_dict["segments"], [segment for transaction in transmission_dict["transactions"] for segment in transaction["segments"]],
        ):
            if segment["segment_identification"] == cls.segment_identification:
                return segment
        else:
            raise KeyError(cls.segment_identification)


class PatientSegment(BaseSegment):

    segment_identification = "01"

    fields = [
        ("CX", "patient_id_qualifier", Alphanumeric, False),
        ("CY", "patient_id", Alphanumeric, False),
        ("C4", "date_of_birth", Numeric, False),
        ("C5", "patient_gender_code", Numeric),
        ("CA", "patient_first_name", Alphanumeric),
        ("CB", "patient_last_name", Alphanumeric),
        ("CM", "patient_street_address", Alphanumeric, False),
        ("CN", "patient_city_address", Alphanumeric, False),
        ("CO", "patient_state_province_address", Alphanumeric, False),
        ("CP", "patient_zip_postal_zone", Alphanumeric, False),
        ("CQ", "patient_phone_number", Numeric, False),
        ("C7", "place_of_service", Alphanumeric, False),
        ("HN", "patient_e_mail_address", Alphanumeric, False),
        ("4X", "patient_residence", Alphanumeric, False),
    ]


class PharmacyProviderSegment(BaseSegment):
    """Guidance is to leave this blank in production, but it used in testing."""

    segment_identification = "02"

    fields = [
        ("EY", "provider_id_qualifier", Alphanumeric),
        ("E9", "provider_id", Numeric),
    ]


class PrescriberSegment(BaseSegment):

    segment_identification = "03"

    fields = [
        ("EZ", "prescriber_id_qualifier", Alphanumeric),
        ("DB", "prescriber_id", Alphanumeric),
        ("DR", "prescriber_last_name", Alphanumeric, False),
        ("PM", "prescriber_telephone_number", Numeric, False),
        ("2E", "primary_care_provider_id_qualifier", Alphanumeric, False),
        ("DL", "primary_care_provider_id", Alphanumeric, False),
        ("4E", "primary_care_provider_last_name", Alphanumeric, False),
        ("2J", "prescriber_first_name", Alphanumeric, False),
        ("2K", "prescriber_street_address", Alphanumeric, False),
        ("2M", "prescriber_city_address", Alphanumeric, False),
        ("2N", "prescriber_state_province_address", Alphanumeric, False),
        ("2P", "prescriber_zip_postal_zone", Numeric, False),
    ]


class InsuranceSegment(BaseSegment):

    segment_identification = "04"

    fields = [
        ("C2", "cardholder_id", Alphanumeric),
        ("CC", "cardholder_first_name", Alphanumeric, False),
        ("CD", "cardholder_last_name", Alphanumeric, False),
        ("CE", "home_plan", Alphanumeric, False),
        ("FO", "plan_id", Alphanumeric, False),
        ("C9", "eligibility_clarification_code", Alphanumeric, False),
        ("C1", "group_id", Alphanumeric, False),
        ("C3", "person_code", Alphanumeric, False),
        ("C6", "patient_relationship_code", Numeric, False),
        ("2A", "medigap_id", Numeric, False),
        ("2B", "medicaid_indicator", Alphanumeric, False),
        ("2D", "provider_accept_assignment_indicator", Alphanumeric, False),
        ("G2", "cms_part_d_defined_qualified_facility", Alphanumeric, False),
        ("N5", "medicaid_id_number", Numeric, False),
    ]


class COBOtherPaymentSegment(BaseSegment):
    """Coordination of Benefits."""

    segment_identification = "05"

    fields = [("4C", "coordination_of_benefits_other_payments_count", Numeric)]

    def __init__(self, *args, **kwargs):
        other_payments = kwargs.pop("other_payments")
        super().__init__(*args, **kwargs)
        self.other_payments = other_payments

    def format(self, enforce_types=True):
        return (
            SEGMENT_SEPARATOR
            + "".join(
                filter(
                    lambda value: value is not None,
                    [field.format(getattr(self, field.name, None), enforce_types=enforce_types) for field in self.fields],
                )
            )
            + "".join(OtherPayment(**other_payment_args).format(enforce_types=enforce_types) for other_payment_args in self.other_payments)
        )


class ClaimSegment(BaseSegment):

    segment_identification = "07"

    fields = [
        ("EM", "prescription_service_reference_number_qualifier", Alphanumeric),
        ("D2", "prescription_service_reference_number", Numeric),
        ("E1", "product_service_id_qualifier", Alphanumeric),
        ("D7", "product_service_id", Alphanumeric),
        ("SE", "procedure_modifier_code_count", Alphanumeric, False),
        ("ER", "procedure_modifier_code", Alphanumeric, False),
        # TODO(danver): Add metric field.
        ("E7", "quantity_dispensed", Numeric, False),
        ("D3", "fill_number", Numeric, False, 2),
        ("D5", "days_supply", Numeric, False),
        ("D6", "compound_code", Numeric, False),
        ("D8", "daw_product_selection_code", Alphanumeric, False),
        ("DE", "date_prescription_written", Numeric, False),
        ("DF", "number_of_refills_authorized", Numeric, False, 2),
        ("NX", "submission_clarification_code_count", Numeric, False),
        ("DK", "submission_clarification_code", Numeric, False),
        ("DT", "special_packaging_indicator", Numeric, False),
        ("EK", "scheduled_prescription_id_number", Alphanumeric, False),
        ("28", "unit_of_measure", Alphanumeric, False),
        ("DI", "level_of_service", Alphanumeric, False),
        ("EU", "prior_authorization_type_code", Numeric, False),
        ("EV", "prior_authorization_number_submitted", Numeric, False),
        ("EW", "intermediary_authorization_type_id", Alphanumeric, False),
        ("EX", "intermediary_authorization_id", Alphanumeric, False),
        ("DJ", "prescription_origin_code", Numeric, False),
        ("EJ", "originally_prescribed_product_service_id_qualifier", Alphanumeric, False,),
        ("EA", "originally_prescribed_product_service_code", Alphanumeric, False),
        ("EB", "originally_prescribed_quantity", Numeric, False),
        ("C8", "other_coverage_code", Alphanumeric, False),
        ("MT", "patient_assignment_indicator", Alphanumeric, False, 1),
        ("U7", "pharmacy_service_type", Alphanumeric, False),
        ("EN", "associated_prescription_service_reference_number", Numeric, False),
        ("E2", "route_of_administration", Alphanumeric, False),
        ("G1", "compound_type", Alphanumeric, False),
    ]


class DURPPSSegment(BaseSegment):
    """Drug Utilization Review or Pharmacy Professional Service."""

    segment_identification = "08"

    fields = [
        ("7E", "dur_pps_code_counter", Alphanumeric, False),
        ("E4", "reason_for_service_code", Alphanumeric, False),
        ("E5", "professional_service_code", Alphanumeric, False),
        ("E6", "result_of_service_code", Alphanumeric, False),
        ("8E", "dur_pps_level_of_effort", Alphanumeric, False),
        ("J9", "dur_co_agent_id_qualifier", Alphanumeric, False),
        ("H6", "dur_co_agent_id", Alphanumeric, False),
    ]


class CompoundSegment(BaseSegment):
    """Compound Segment."""

    segment_identification = "10"

    fields = [
        ("EF", "compound_dosage_form_description_code", Alphanumeric),
        ("EG", "compound_dispensing_unit_form_indicator", Numeric),
        ("EC", "compound_ingredient_component_count", Numeric, True, 2),
    ]

    def __init__(self, *args, **kwargs):
        ingredients = kwargs.pop("ingredients")
        modifier_codes = kwargs.pop("modifier_codes", {})
        super().__init__(*args, **kwargs)
        self.ingredients = ingredients
        self.modifier_codes = modifier_codes

    def format(self, enforce_types=True):
        return (
            SEGMENT_SEPARATOR
            + "".join(
                filter(
                    lambda value: value is not None,
                    [field.format(getattr(self, field.name, None), enforce_types=enforce_types) for field in self.fields],
                )
            )
            + "".join(Ingredient(**ingredient_args).format(enforce_types=enforce_types) for ingredient_args in self.ingredients)
            + ModifierCodes(**self.modifier_codes).format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)
        )


class PricingSegment(BaseSegment):

    segment_identification = "11"

    fields = [
        ("D9", "ingredient_cost_submitted", Dollar),
        ("DC", "dispensing_fee_submitted", Dollar, False),
        ("HA", "flat_sales_tax_amount_submitted", Dollar, False),
        ("GE", "percentage_sales_tax_amount_submitted", Dollar, False),
        ("HE", "percentage_sales_tax_rate_submitted", Dollar, False),
        ("JE", "percentage_sales_tax_basis_submitted", Numeric, False, 2),
        ("DX", "patient_paid_amount_submitted", Dollar, False),
        ("DQ", "usual_and_customary_charge", Dollar, False),
        ("DU", "gross_amount_due", Dollar),
        ("DN", "basis_of_cost_determination", Alphanumeric, False),
        ("E3", "incentive_amount_submitted", Dollar, False),
        ("H7", "other_amount_claimed_submitted_count", Numeric, False),
        ("H8", "other_amount_claimed_submitted_qualifier", Alphanumeric, False),
        ("H9", "other_amount_claimed_submitted", Dollar, False),
    ]


class ClinicalSegment(BaseSegment):
    """To leave blank."""

    segment_identification = "13"

    fields = [
        ("VE", "diagnosis_code_count", Alphanumeric),
        ("WE", "diagnosis_code_qualifier", Alphanumeric),
        ("DO", "diagnosis_code", Alphanumeric, False),
        ("XE", "clinical_information_counter", Alphanumeric),
        ("ZE", "measurement_date", Alphanumeric, False),
        ("H1", "measurement_time", Alphanumeric, False),
        ("H2", "measurement_dimension", Alphanumeric, False),
        ("H3", "measurement_unit", Alphanumeric, False),
        ("H4", "measurement_value", Alphanumeric, False),
    ]


class AdditionalDocumentationSegment(BaseSegment):
    segment_identification = "14"

    fields = [
        ("2Q", "additional_documentation_type_id", Alphanumeric),
        ("2V", "request_period_begin_date", Alphanumeric, False),
        ("2W", "request_period_recert_revised_date", Numeric, False),
        ("2U", "request_status", Alphanumeric, False),
        ("2S", "length_of_need_qualifier", Alphanumeric),
        ("2R", "length_of_need", Alphanumeric, False),
        ("2T", "prescriber_supplier_date_signed", Alphanumeric, False),
        ("2X", "supporting_documentation", Alphanumeric, False),
        ("2Z", "question_number_letter_count", Alphanumeric),
    ]

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super().__init__(*args, **kwargs)
        self.questions = questions

    def format(self, enforce_types=True):
        return (
            SEGMENT_SEPARATOR
            + "".join(
                filter(
                    lambda value: value is not None,
                    [field.format(getattr(self, field.name, None), enforce_types=enforce_types) for field in self.fields],
                )
            )
            + "".join(Question(**question_args).format(enforce_types=enforce_types) for question_args in self.questions)
        )


class FacilitySegment(BaseSegment):
    segment_identification = "15"

    fields = [
        ("8C", "facility_id", Alphanumeric, False),
        ("3Q", "facility_name", Alphanumeric, False),
        ("3U", "facility_street_address", Alphanumeric, False),
        ("5J", "facility_city_address", Alphanumeric, False),
        ("3V", "facility_state_province_address", Alphanumeric, False),
        ("6D", "facility_zip_postal_zone", Alphanumeric, False),
    ]


class NarrativeSegment(BaseSegment):
    segment_identification = "16"

    fields = [("BM", "narrative_message", Alphanumeric)]


class ResponseMessageSegment(BaseSegment):
    """Contains a textual response from the server."""

    segment_identification = "20"
    fields = [("F4", "message", Alphanumeric, False)]


class ResponseStatusSegment(BaseSegment):
    """Contains the Status of the response."""

    segment_identification = "21"
    fields = [
        ("AN", "transaction_response_status", Alphanumeric),
        ("FA", "reject_count", Alphanumeric, False),
        ("FB", "reject_code", Alphanumeric, False),
        ("F3", "authorization_number", Numeric, False),
        ("UF", "additional_message_information_count", Numeric, False),
        ("UH", "additional_message_information_qualifier", Alphanumeric, False),
        ("FQ", "additional_message_information", Alphanumeric, False),
        ("7F", "help_desk_phone_number_qualifier", Alphanumeric, False),
        ("8F", "help_desk_phone_number", Numeric, False),
    ]


class ResponseClaimSegment(BaseSegment):
    """Contain Clam Information from the Response."""

    segment_identification = "22"

    fields = [
        ("EM", "prescription_service_reference_number_qualifier", Alphanumeric),
        ("D2", "prescription_service_reference_number", Numeric),
        ("9F", "preferred_product_count", Numeric, False),
        ("AP", "preferred_product_id_qualifier", Alphanumeric, False),
        ("AR", "preferred_product_id", Alphanumeric, False),
    ]


class ResponsePricingSegment(BaseSegment):
    """Contains information related to the pricing of this claim."""

    segment_identification = "23"

    fields = [
        ("F5", "patient_pay_amount", Dollar),
        ("F6", "ingredient_cost_paid", Dollar),
        ("F7", "dispensing_fee_paid", Dollar),
        ("AV", "tax_exempt_indicator", Numeric, False),
        ("J2", "other_amount_paid_count", Numeric),
        ("J3", "other_amount_paid_qualifier", Alphanumeric),
        ("J4", "other_amount_paid", Dollar, False),
        ("J5", "other_payer_amount_recognized", Dollar, False),
        ("F9", "total_amount_paid", Dollar),
        ("FM", "basis_of_reimbursement_determination", Numeric),
        ("FN", "amount_attributed_to_sales_tax", Dollar, False),
        ("FI", "amount_of_copay", Dollar, False),
        ("AW", "flat_sales_tax_amount_paid", Dollar, False),
        ("EQ", "patient_sales_tax_amount", Dollar, False),
        ("AX", "percentage_sales_tax_amount_paid", Dollar, False),
        ("AY", "percentage_sales_tax_rate_paid", Dollar, False),
        ("AZ", "percentage_sales_tax_basis_paid", Dollar, False),
        ("FL", "incentive_amount_paid", Dollar, False),
        ("FH", "amount_applied_to_periodic_deductible", Dollar, False),
    ]


class ResponseDURPPSSegment(BaseSegment):
    """Drug Utilization Review or Pharmacy Professional Service Response Segment."""

    segment_identification = "24"

    fields = [
        ("J6", "dur_pps_response_code_counter", Numeric, False),
        ("E4", "reason_for_service_code", Alphanumeric, False),
        ("FS", "clinical_significance_code", Numeric, False),
        ("FT", "other_pharmacy_indicator", Numeric, False),
        ("FU", "previous_date_of_fill", Alphanumeric, False),
        ("FV", "quantity_of_previous_fill", Alphanumeric, False),
        ("FW", "database_indicator", Alphanumeric, False),
        ("FX", "other_prescriber_indicator", Alphanumeric, False),
        ("FY", "dur_free_text_message", Alphanumeric, False),
        ("NS", "dur_additional_text", Alphanumeric, False),
    ]


class ResponseInsuranceSegment(BaseSegment):
    """Contains information related to the insurance of this claim."""

    segment_identification = "25"

    fields = [
        ("C1", "group_id", Alphanumeric, False),
        ("FO", "plan_id", Alphanumeric, False),
        ("2F", "network_reimbursement_id", Alphanumeric, False),
        ("J7", "payer_id_qualifier", Alphanumeric, False),
        ("J8", "payer_id", Alphanumeric, False),
        ("FO", "plan_id", Alphanumeric, False),
        ("C2", "cardholder_id", Alphanumeric, False),
    ]


class ResponsePriorAuthorizationSegment(BaseSegment):
    """Contains information related to the insurance of this claim."""

    segment_identification = "26"

    fields = [("PY", "prior_authorization_number_assigned", Numeric, False)]


class ResponseCOBSegment(BaseSegment):
    """Response Coordination of Benefits Segment."""

    segment_identification = "28"

    fields = [
        ("NT", "other_payer_id_count", Numeric, False),
        ("5C", "other_payer_coverage_type", Alphanumeric, False),
        ("6C", "other_payer_id_qualifier", Numeric, False),
        ("76", "other_payer_id", Alphanumeric, False),
        ("MH", "other_payer_processor_control_number", Alphanumeric, False),
        ("NU", "other_payer_cardholder_id", Alphanumeric, False),
        ("MJ", "other_payer_group_id", Alphanumeric, False),
        ("UV", "other_payer_person_code", Alphanumeric, False),
        ("UB", "other_payer_help_desk_phone_number", Alphanumeric, False),
        ("UW", "other_payer_patient_relationship_code", Numeric, False),
    ]


class ResponsePatientSegment(BaseSegment):
    """Contains information related to the insurance of this claim."""

    segment_identification = "29"

    fields = [
        ("C4", "date_of_birth", Numeric, False),
        ("CA", "patient_first_name", Alphanumeric, False),
        ("CB", "patient_last_name", Alphanumeric, False),
    ]


class OtherPayment(BaseSegment):
    """Not a segment, though it looks like it."""

    segment_identification = None

    fields = [
        ("5C", "other_payer_coverage_type", Alphanumeric),
        ("6C", "other_payer_id_qualifier", Alphanumeric, False),
        ("7C", "other_payer_id", Alphanumeric, False),
        ("E8", "other_payer_date", Alphanumeric, False),
        ("NR", "other_payer_patient_responsibility_amount_count", Numeric, False),
        ("HB", "other_payer_amount_paid_count", Numeric, False),
        ("HC", "other_payer_amount_paid_qualifier", Alphanumeric, False),
        ("DV", "other_payer_amount_paid", Dollar, False),
    ]

    def __init__(self, *args, **kwargs):
        other_payer_patient_responsibility_amounts = kwargs.pop("other_payer_patient_responsibility_amounts", [])

        benefit_stages = kwargs.pop("benefit_stages", {})

        super().__init__(*args, **kwargs)
        self.fields = self.fields[1:]
        self.other_payer_patient_responsibility_amounts = other_payer_patient_responsibility_amounts
        self.benefit_stages = benefit_stages

    def format(self, enforce_types=True):
        return (
            super().format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)
            + "".join(
                OtherPayerPatientResponsibilityAmount(**other_payer_patient_responsibility_amount_args).format(enforce_types=enforce_types)
                for other_payer_patient_responsibility_amount_args in self.other_payer_patient_responsibility_amounts
            )
            + BenefitStages(**self.benefit_stages).format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)
        )


class BenefitStages(BaseSegment):
    """Not a segment, although it looks like it is.

    Note: This is hard-coded to only work with 1 Benefit Stage.
    """

    segment_identification = None

    fields = [
        ("MU", "benefit_stage_count", Numeric, False),
        ("MV", "benefit_stage_qualifier", Alphanumeric, False),
        ("MW", "benefit_stage_amount", Dollar, False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self.fields[1:]

    def format(self, enforce_types=True):
        return super().format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)


class OtherPayerPatientResponsibilityAmount(BaseSegment):
    """Not a segment, although it looks like it is."""

    segment_identification = None

    fields = [
        ("NP", "other_payer_patient_responsibility_amount_qualifier", Alphanumeric, False,),
        ("NQ", "other_payer_patient_responsibility_amount", Dollar, False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self.fields[1:]

    def format(self, enforce_types=True):
        return super().format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)


class ModifierCodes(BaseSegment):
    """A PseudoSegment that encodes ModifierCodes.

    Hardcoded to only work with 1 Modifier Code."""

    segment_identification = None

    fields = [
        ("2G", "compound_ingredient_modifier_code_count", Numeric, False, 2),
        ("2H", "compound_ingredient_modifier_code", Alphanumeric, False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self.fields[1:]

    def format(self, enforce_types=True):
        return super().format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)


class Ingredient(BaseSegment):
    """Despite being a subclass of BaseSegment, an Ingredient is not a true segment."""

    # Empty segment_identification means this doesn't go in the registry.
    segment_identification = None

    fields = [
        ("RE", "compound_product_id_qualifier", Numeric, True, 2),
        ("TE", "compound_product_id", Alphanumeric),
        ("ED", "compound_ingredient_quantity", Numeric, True),
        ("EE", "compound_ingredient_drug_cost", Dollar),
        ("UE", "compound_ingredient_basis_of_cost_determination", Alphanumeric, False),
    ]

    def __init__(self, *args, **kwargs):
        if "compound_ingredient_quantity" in kwargs:
            # This is how they insist on formatting the compound quantity.
            kwargs["compound_ingredient_quantity"] = int(float(kwargs["compound_ingredient_quantity"]) * 1000)
        super().__init__(*args, **kwargs)
        self.fields = self.fields[1:]

    def format(self, enforce_types=True):
        return super().format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)


class Question(BaseSegment):
    """Despite being a subclass of BaseSegment, a Question is not a true segment."""

    # Empty segment_identification means this doesn't go in the registry.
    segment_identification = None

    fields = [
        ("4B", "question_number_letter", Alphanumeric),
        ("4G", "question_date_response", Alphanumeric, False),
        ("4J", "question_numeric_response", Alphanumeric, False),
        ("4K", "question_alphanumeric_response", Alphanumeric, False),
        ("4H", "question_dollar_amount_response", Dollar, False),
        ("4D", "question_percent_response", Numeric, False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = self.fields[1:]

    def format(self, enforce_types=True):
        return super().format(enforce_types=enforce_types).lstrip(SEGMENT_SEPARATOR)
