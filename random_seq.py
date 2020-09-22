import random

def random_seq(n, characters='ACTG', seed=None):
    """
    Returns a sequence of length >n<, composed
    of a random combination of characters chosen
    from >characters<. 
    
    """
    if seed:
        random.seed(seed)

    return ''.join(random.choices(characters, k=n))