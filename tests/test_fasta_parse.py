import io
import unittest

from biogl.fasta_parse import fasta_parse


class TestFastaParse(unittest.TestCase):
    def setUp(self):
        # Test FASTA input that will be used for all tests.
        # Record details:
        # >Header1_extra more_info   → trimmed becomes "Header1_extra"
        #   has one line: "1"
        # >Header2_extra           → trimmed becomes "Header2_extra"
        #   has two lines: "22" and "22" (joined: "2222")
        # >Header3_extra           → trimmed becomes "Header3_extra"
        #   has three lines: "333", "333", "333" (joined: "333333333")
        self.fasta_numeric = (
            ">Header1_extra more_info\n"
            "1\n"
            ">Header2_extra\n"
            "22\n"
            "22\n"
            ">Header3_extra\n"
            "333\n"
            "333\n"
            "333\n"
        )
        # This regex will capture everything before the underscore.
        self.header_pattern = r"^(.*?)_"

    def test_default_whitespace_trimming_and_joining(self):
        # Default settings with trim_header=True.
        # Header1 becomes "Header1_extra" (the first token from "Header1_extra more_info").
        # Header2 remains "Header2_extra" and Header3 remains "Header3_extra".
        # Sequences are joined using the default (empty string) separator.
        records = list(fasta_parse(self.fasta_numeric))
        expected = [
            ("Header1_extra", "1"),
            ("Header2_extra", "2222"),
            ("Header3_extra", "333333333"),
        ]
        self.assertEqual(records, expected)

    def test_return_list_when_separator_is_None(self):
        # When separator is None the sequence lines are returned as a list.
        records = list(fasta_parse(self.fasta_numeric, separator=None))
        expected = [
            ("Header1_extra", ["1"]),
            ("Header2_extra", ["22", "22"]),
            ("Header3_extra", ["333", "333", "333"]),
        ]
        self.assertEqual(records, expected)

    def test_header_pattern_after_trimming(self):
        # Here, header is first trimmed on whitespace; for Header1, "Header1_extra more_info" becomes "Header1_extra".
        # Then the header_pattern regex r"^(.*?)_" is applied, extracting "Header1" (and similarly for the others).
        records = list(
            fasta_parse(
                self.fasta_numeric, trim_header=True, header_pattern=self.header_pattern
            )
        )
        expected = [
            ("Header1", "1"),
            ("Header2", "2222"),
            ("Header3", "333333333"),
        ]
        self.assertEqual(records, expected)

    def test_input_as_iterator(self):
        # Supply the FASTA input as an iterator (list of lines).
        fasta_lines = self.fasta_numeric.splitlines()
        records = list(fasta_parse(fasta_lines))
        expected = [
            ("Header1_extra", "1"),
            ("Header2_extra", "2222"),
            ("Header3_extra", "333333333"),
        ]
        self.assertEqual(records, expected)

    def test_using_stringio(self):
        # Use io.StringIO to simulate a file input.
        stream = io.StringIO(self.fasta_numeric)
        records = list(fasta_parse(stream))
        expected = [
            ("Header1_extra", "1"),
            ("Header2_extra", "2222"),
            ("Header3_extra", "333333333"),
        ]
        self.assertEqual(records, expected)


if __name__ == "__main__":
    unittest.main()
