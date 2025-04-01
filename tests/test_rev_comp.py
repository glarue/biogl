import unittest

from biogl.rev_comp import rev_comp


class TestRevComp(unittest.TestCase):
    def test_uppercase_default(self):
        # Default behavior (ignore_lowercase=False) on an all-uppercase sequence.
        seq = "ATCGU"
        # Reverse of "ATCGU" is "UGCTA".
        # Mapping: U->A, G->C, C->G, T->A, A->T yields "ACGAT".
        expected = "ACGAT"
        self.assertEqual(rev_comp(seq, ignore_lowercase=False), expected)

    def test_lowercase_mapped(self):
        # With ignore_lowercase=False, lowercase letters should be mapped.
        seq = "atcgu"
        # Reverse "atcgu" -> "ugcta" then lowercase mapping: u->a, g->c, c->g, t->a, a->t
        expected = "acgat"
        self.assertEqual(rev_comp(seq, ignore_lowercase=False), expected)

    def test_ignore_lowercase(self):
        # With ignore_lowercase=True, only uppercase letters are processed; lowercase are left untouched.
        seq = "atcgu"
        # Reverse "atcgu" -> "ugcta". Since lowercase are NOT mapped, the result remains "ugcta".
        expected = "ugcta"
        self.assertEqual(rev_comp(seq, ignore_lowercase=True), expected)

    def test_mask_usage(self):
        # Test that non-ATCGU characters are replaced with the mask.
        seq = "ATXGU"
        # re.sub with mask_upper: pattern "[^ATCGU]" should match X and replace with "N" -> "ATNGU"
        # Then reverse: "UGNTA" and map using uppercase table: U->A, G->C, N unchanged, T->A, A->T
        expected = "ACNAT"
        self.assertEqual(rev_comp(seq, mask="N"), expected)

    def test_return_list(self):
        # Test that when as_string is False, a list is returned.
        seq = "ATCGU"
        expected = list("ACGAT")  # as computed in test_uppercase_default
        self.assertEqual(rev_comp(seq, as_string=False), expected)

    def test_mixed_case(self):
        # Test a sequence with both upper and lowercase when processing both.
        seq = "AtCgU"
        # ignore_lowercase defaults to False, so both cases are mapped:
        # Reverse "AtCgU" -> "UgCtA"; mapping: U->A, g->c, C->G, t->a, A->T gives "AcGaT"
        expected = "AcGaT"
        self.assertEqual(rev_comp(seq, ignore_lowercase=False), expected)

    def test_output_seq_type_dna(self):
        # For output_seq_type "dna", any U/u should be converted to T/t.
        # Given the default rev_comp output for "ATCGU" is "ACGAT" (already DNA-like),
        # it should remain unchanged.
        seq = "ATCGU"
        expected = "ACGAT"
        self.assertEqual(rev_comp(seq, output_seq_type="dna"), expected)

    def test_output_seq_type_rna(self):
        # For output_seq_type "rna", all T/t in the output should be replaced by U/u.
        # Default rev_comp output for "ATCGU" is "ACGAT". Converting T->U yields "ACGAU".
        seq = "ATCGU"
        expected = "ACGAU"
        self.assertEqual(rev_comp(seq, output_seq_type="rna"), expected)


if __name__ == "__main__":
    unittest.main()
