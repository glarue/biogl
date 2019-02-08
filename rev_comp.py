def rev_comp(seq, use_lower=True):
    """
    Returns reverse complement of {seq}, with
    any non-ACTG characters replaced with Ns

    """
    transform = {
        'A': 'T',
        'T': 'A',
        'C': 'G',
        'G': 'C',
        'N': 'N'
    }
    transform_mixed = {
        'A': 'T',
        'T': 'A',
        'C': 'G',
        'G': 'C',
        'N': 'N',
        'a': 't',
        't': 'a',
        'c': 'g',
        'g': 'c',
        'n': 'n'
    }
    if use_lower is True:
        mapper = transform_mixed
    else:
        mapper = transform
    try:
        comp = [mapper[e] for e in seq]
    except KeyError:  # non-ATCGN characters in seq
        seq = [e if e in "ACTGNactgn" else "X" for e in seq]
        comp = [mapper[e] for e in seq]
    reverse_comp = comp[::-1]
    reverse_comp_string = ''.join(reverse_comp)

    return reverse_comp_string