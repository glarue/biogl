# authorship information
__author__ = 'Graham E. Larue'
__maintainer__ = "Graham E. Larue"
__email__ = 'egrahamlarue@gmail.com'
__license__ = 'GPL'

import os

def arg_info_header(args, comment_char='#'):
    '''
    Generate a commented string to use at top of output
    files.
    
    <args> is argparse.args object
    '''
    arg_bits = []
    for a, v in sorted(vars(args).items()):
        try:
            v = os.path.abspath(v)
        except:
            pass
        v = str(v)
        b = '{}: {}'.format(a, v)
        arg_bits.append(b)
    header_string = (
        '{} [location] {}\n{} [arguments] {}'
        .format(comment_char, os.getcwd(), comment_char, '; '.join(arg_bits))
    )

    return header_string