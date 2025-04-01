import re
from pathlib import Path
from typing import Iterator, List, Optional, Pattern, Tuple, Union

from smart_open import open as smart_open


def fasta_parse(
    fasta: Union[Path, str, Iterator[str]],
    delimiter: str = ">",
    separator: Optional[str] = "",
    trim_header: bool = True,
    header_pattern: Optional[Union[str, Pattern[str]]] = None,
) -> Iterator[Tuple[str, Union[str, List[str]]]]:
    """
    Iterator which takes FASTA as input and yields header/record pairs.

    Parameters:
        fasta (Union[Path, str, Iterator[str]]): The FASTA input, which can be a file path,
            a string, or an iterator of strings.
        delimiter (str, optional): The character used to define new records in the input file.
            Default is '>'.
        separator (Optional[str], optional): The separator used to join the sequence lines;
            specify None to return a list of strings per record. Default is ''.
        trim_header (bool, optional): If True, the parser will trim the FASTA header by splitting on whitespace
            and taking the first token. Default is True.
        header_pattern (Optional[Union[str, Pattern[str]]], optional): A regular expression used to further process
            the header to capture only the matching portion. If provided, it is applied after any trimming.
            If the pattern contains a capturing group, that group is returned; otherwise, the entire match is used.
            Default is None.

    Yields:
        Iterator[Tuple[str, Union[str, List[str]]]]:
            An iterator of tuples, where each tuple contains a header and a record
            (either as a string or a list of strings).

    Examples:
    ---------
    Example 1: Default behavior with whitespace trimming
    >>> fasta_string = ">Gene1 extra info\nATCGATCG\n>Gene2 additional info\nGGTAAC"
    >>> for h, s in fasta_parse(fasta_string):
    ...     print(f"Header: {h}")
    ...     print(f"Sequence: {s}")
    Header: Gene1
    Sequence: ATCGATCG
    Header: Gene2
    Sequence: GGTAAC

    Example 2: Trimming followed by custom header processing with a regex pattern.
           Here the header is first split on whitespace, then the regex extracts only the part before
           an underscore.
    >>> fasta_string = ">Gene1_extra info\nATCGATCG\n>Gene2_more info\nGGTAAC"
    >>> for h, s in fasta_parse(fasta_string, trim_header=True, header_pattern=r"^(.*?)_"):
    ...     print(f"Header: {h}")
    ...     print(f"Sequence: {s}")
    Header: Gene1
    Sequence: ATCGATCG
    Header: Gene2
    Sequence: GGTAAC
    """
    # Compile header_pattern once outside of the loop (if provided).
    pat = None
    if header_pattern is not None:
        pat = (
            header_pattern
            if isinstance(header_pattern, Pattern)
            else re.compile(header_pattern)
        )

    header, seq = None, []
    close_file = False
    try:
        fa = smart_open(fasta)
        close_file = True
    except (FileNotFoundError, OSError):  # passed in directly as a string
        fa = fasta.split("\n")
    except TypeError:  # if already an iterator (e.g., fileinput)
        fa = fasta
    try:
        for line in fa:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(delimiter):
                if header is not None:
                    if separator is not None:
                        seq = separator.join(str(e) for e in seq)
                    yield header, seq
                header = line.lstrip(delimiter)
                # First, trim header using whitespace splitting.
                if trim_header:
                    header = header.split()[0] if header.split() else ""
                # Then, further process the header using header_pattern if provided.
                if pat is not None:
                    m = pat.search(header)
                    if m:
                        header = m.group(1) if m.lastindex else m.group(0)
                seq = []
            else:
                seq.append(line.rstrip("\n"))
        if separator is not None:
            seq = separator.join(str(e) for e in seq)
        yield header, seq
    finally:
        if close_file is True:
            fa.close()
