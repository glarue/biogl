from itertools import islice

def window(seq, n=2):
    """
    Taken from https://docs.python.org/release/2.3.5/lib/itertools-example.html

    Returns a sliding window (of width n) over data from the iterable
    s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    """
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result