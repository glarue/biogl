import hashlib
from operator import methodcaller

def file_hash(*file_paths, hash_name='md5', buffer_size=65536):
    '''
    Generate a hash digest from one or more file paths.

    :param file_paths: Filename(s) of the file(s) to hash
    :param hash_name: The name of the hash to use, from hashlib (default: md5)
    :type hash_name: str
    :param buffer_size: Read buffer size in bytes (default: 65536)
    :type buffer_size: int
    '''
    h = methodcaller(hash_name)
    hash = h(hashlib)
    for p in file_paths:
        with open(p, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                hash.update(data)

    return hash.hexdigest()