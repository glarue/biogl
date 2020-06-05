import re

def rev_comp(
    seq, 
    use_lower=True, 
    mask=None, 
    as_string=True, 
    mask_upper=re.compile('[^ATCG]'), 
    mask_lower=re.compile('[^ATCGatcg]')
):
    """
    Returns reverse complement of {seq}, with
    any non-ACTG characters replaced with {mask}

    If {as_string}, returns a string; else, returns 
    a list.

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
        masker = mask_lower
    else:
        mapper = transform
        masker = mask_upper
    if mask is not None:
        seq = re.sub(masker, mask, seq)
    mapper = str.maketrans(mapper)
    comp = seq.translate(mapper)
    reverse_comp = comp[::-1]
    if as_string is False:
        reverse_comp = list(reverse_comp)
    
    return reverse_comp