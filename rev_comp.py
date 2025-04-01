import re
from typing import List, Optional, Pattern, Union


def rev_comp(
    seq: str,
    ignore_lowercase: bool = False,
    mask: Optional[str] = None,
    as_string: bool = True,
    mask_upper: Pattern[str] = re.compile(r"[^ATCGU]"),
    mask_lower: Pattern[str] = re.compile(
        r"[^ATCGUatcgu]"
    ),  # for masking; adjust regex as needed
    output_seq_type: Optional[str] = None,
) -> Union[str, List[str]]:
    """
    Returns the reverse complement of a nucleotide sequence.

    Non-ATCGU characters are replaced with `mask` (if specified). The function uses an
    uppercase translation table by default. When `ignore_lowercase` is False, it also
    maps lowercase characters to their complements.

    Args:
        seq (str): Input nucleotide sequence.
        ignore_lowercase (bool): If False, applies lowercase mappings as well. Defaults to False.
        mask (Optional[str]): Replacement character for any character not in ATCGU. Defaults to None.
        as_string (bool): If True, returns the result as a string; otherwise, as a list. Defaults to True.
        mask_upper (Pattern[str]): Regex pattern used for masking non-ATCGU uppercase characters.
        mask_lower (Pattern[str]): Regex pattern used for masking non-ATCGU characters when including lowercase.
        output_seq_type (Optional[Literal["dna", "rna"]]): Convert output sequence:
            "dna" converts U/u to T/t; "rna" converts T/t to U/u.

    Returns:
        Union[str, List[str]]: The reverse complement of `seq` as a string if `as_string` is True,
        or as a list of characters otherwise.
    """
    # Create a translation table for uppercase letters.
    trans_table = str.maketrans("ATCGU", "TAGCA")
    # When ignoring lowercase is False, include lowercase mappings.
    if not ignore_lowercase:
        lower_table = str.maketrans("atcgu", "tagca")
        trans_table.update(lower_table)

    # Use appropriate regex mask.
    masker = mask_lower if not ignore_lowercase else mask_upper

    if mask is not None:
        seq = re.sub(masker, mask, seq)
    # Reverse and complement the sequence.
    reverse_comp_seq = seq[::-1].translate(trans_table)
    match output_seq_type:
        case None:
            pass
        case seq_type:
            match seq_type.lower():
                case "dna":
                    seq_type_table = str.maketrans("Uu", "Tt")
                    reverse_comp_seq = reverse_comp_seq.translate(seq_type_table)
                case "rna":
                    seq_type_table = str.maketrans("Tt", "Uu")
                    reverse_comp_seq = reverse_comp_seq.translate(seq_type_table)
                case _:
                    raise ValueError("output_seq_type must be 'dna' or 'rna'")
    if not as_string:
        reverse_comp_seq = list(reverse_comp_seq)

    return reverse_comp_seq
