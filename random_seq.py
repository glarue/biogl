import random

def random_seq(n, characters='ACTG'):
    """
    Returns a sequence of length >n<, composed
    of a random combination of characters chosen
    from >characters<. 
    
    """
    return ''.join(random.choices(characters, k=n))