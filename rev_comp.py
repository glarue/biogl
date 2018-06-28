def rev_comp(seq):
    """
    Returns reverse complement of {seq}, with
    any non-ACTG characters replaced with Ns

    """
    transform = {'A': 'T',
                 'T': 'A',
                 'C': 'G',
                 'G': 'C',
                 'N': 'N'}
    try:
        comp = [transform[e] for e in seq]
    except KeyError:  # non-ATCGN characters in seq
        seq = [e if e in "ACTGN" else "N" for e in seq]
        comp = [transform[e] for e in seq]
    reverse_comp = comp[::-1]
    reverse_comp_string = ''.join(reverse_comp)

    return reverse_comp_string