import os
import re

def recursive_items(
    start_dir=None, is_file_filter=True, pattern=None):
    """
    Generator which searches all subdirectories of <start_dir> 
    and returns matching items.

    By default, returns only files.
    
    """
    if start_dir is None:
        start_dir = os.getcwd()
    if pattern is not None:
        pattern = re.compile(pattern)
    for root, dirs, items in os.walk(start_dir):
        dirs.sort()
        # dirs = sorted(dirs)
        for i in sorted(items + dirs, key=lambda x: x.lower()):
            ipath = os.path.join(root, i)
            if is_file_filter and not os.path.isfile(ipath):
                continue
            if pattern and not pattern.search(i):
                continue

            yield ipath