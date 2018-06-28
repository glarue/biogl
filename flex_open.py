import gzip
from functools import partial

def flex_open(filename):
    """
    A generator of lines from a variety of
    file types, including compressed files.
    
    """
    magic_dict = {
        b'\x1f\x8b\x08': partial(gzip.open, mode='rt')
        # "\x42\x5a\x68": "bz2",
        # "\x50\x4b\x03\x04": "zip"
        }

    max_len = max(len(x) for x in magic_dict)
    
    open_func = None
    
    # Try opening the file in binary mode and reading the first
    # chunk to see if it matches the signature byte pattern
    # expected for each compressed file type

    with open(filename, 'rb') as f:
        file_start = f.read(max_len)
    for magic, func in magic_dict.items():
        if file_start.startswith(magic):
            open_func = func
    
    if open_func:
        return open_func(filename)
    else:
        return open(filename)