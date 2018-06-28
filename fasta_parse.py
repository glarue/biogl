def fasta_parse(fasta, delimiter=">", separator="", trim_header=True):
    """
    Iterator which takes FASTA as input. Yields
    header/value pairs.

	{delimiter} is the character used to define
	new records in the input file.

	{separator} will be used to join the return value;
	use separator=None to return a list.

    If {trim_header}, parser will return the
    FASTA header up to the first space character.
    Otherwise, it will return the full, unaltered
    header string.

    """
    header, seq = None, []
    try:
        f = open(fasta)
    except (FileNotFoundError, OSError):  # passed in directly as a string
        f = fasta.split('\n')
    except TypeError:  # is fileinput
        f = fasta
    for line in f:
        if line.startswith(delimiter):
            if header is not None:
                if separator is not None:
                    seq = separator.join(str(e) for e in seq)
                yield header, seq
            header = line.strip().lstrip(delimiter)
            if trim_header:
                try:
                    header = header.split()[0]
                except IndexError:  # blank header
                    header = ""
            seq = []
        elif line.startswith('#'):
            continue
        else:
            if line.strip():  # don't collect blank lines
                seq.append(line.rstrip('\n'))
    if separator is not None:
        seq = separator.join(str(e) for e in seq)

    yield header, seq
