def is_fasta(some_file):
    with open(some_file) as f:
        last_was_header = False
        for l in f:
            if l.startswith("#"):
                continue
            if last_was_header is True:
                if not l.startswith('>'):
                    return True
                else:
                    return False
            elif l.startswith(">"):
                last_was_header = True
                continue
            else:
                return False