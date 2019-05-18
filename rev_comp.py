def rev_comp(seq, use_lower=True, mask=True):
    """
    Returns reverse complement of {seq}, with
    any non-ACTG characters replaced with Ns 
    if {mask}==True

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
    valid_chars = [
        'A', 'C', 'T', 'G', 'N', 'a', 'c', 't', 'g', 'n']
    if mask is True:
        seq = [e if e in valid_chars else 'N' for e in seq]
    try:
        comp = [mapper[e] for e in seq]
    except KeyError:  # non-ATCGN characters in seq
        comp = [mapper[e] if e in mapper else e for e in seq]
    reverse_comp = comp[::-1]
    reverse_comp_string = ''.join(reverse_comp)

    return reverse_comp_string