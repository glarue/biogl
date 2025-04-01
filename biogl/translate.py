# authorship information
__author__ = 'Graham E. Larue'
__maintainer__ = "Graham E. Larue"
__email__ = 'egrahamlarue@gmail.com'
__license__ = 'GPL'

def translate(
    string, 
    verbosity="single",
    phase=0,
    mask=True,
    stop_char='*',
    as_codons=False,
    remove_whitespace=True,
    codon_map={
        'AAA': ('K', 'Lys', 'Lysine'),
        'AAC': ('N', 'Asn', 'Asparagine'),
        'AAG': ('K', 'Lys', 'Lysine'),
        'AAT': ('N', 'Asn', 'Asparagine'),
        'ACA': ('T', 'Thr', 'Threonine'),
        'ACC': ('T', 'Thr', 'Threonine'),
        'ACG': ('T', 'Thr', 'Threonine'),
        'ACT': ('T', 'Thr', 'Threonine'),
        'AGA': ('R', 'Arg', 'Arginine'),
        'AGC': ('S', 'Ser', 'Serine'),
        'AGG': ('R', 'Arg', 'Arginine'),
        'AGT': ('S', 'Ser', 'Serine'),
        'ATA': ('I', 'Ile', 'Isoleucine'),
        'ATC': ('I', 'Ile', 'Isoleucine'),
        'ATG': ('M', 'Met', 'Methionine'),
        'ATT': ('I', 'Ile', 'Isoleucine'),
        'CAA': ('Q', 'Gln', 'Glutamine'),
        'CAC': ('H', 'His', 'Histidine'),
        'CAG': ('Q', 'Gln', 'Glutamine'),
        'CAT': ('H', 'His', 'Histidine'),
        'CCA': ('P', 'Pro', 'Proline'),
        'CCC': ('P', 'Pro', 'Proline'),
        'CCG': ('P', 'Pro', 'Proline'),
        'CCT': ('P', 'Pro', 'Proline'),
        'CGA': ('R', 'Arg', 'Arginine'),
        'CGC': ('R', 'Arg', 'Arginine'),
        'CGG': ('R', 'Arg', 'Arginine'),
        'CGT': ('R', 'Arg', 'Arginine'),
        'CTA': ('L', 'Leu', 'Leucine'),
        'CTC': ('L', 'Leu', 'Leucine'),
        'CTG': ('L', 'Leu', 'Leucine'),
        'CTT': ('L', 'Leu', 'Leucine'),
        'GAA': ('E', 'Glu', 'Glutamate'),
        'GAC': ('D', 'Asp', 'Aspartate'),
        'GAG': ('E', 'Glu', 'Glutamate'),
        'GAT': ('D', 'Asp', 'Aspartate'),
        'GCA': ('A', 'Ala', 'Alanine'),
        'GCC': ('A', 'Ala', 'Alanine'),
        'GCG': ('A', 'Ala', 'Alanine'),
        'GCT': ('A', 'Ala', 'Alanine'),
        'GGA': ('G', 'Gly', 'Glycine'),
        'GGC': ('G', 'Gly', 'Glycine'),
        'GGG': ('G', 'Gly', 'Glycine'),
        'GGT': ('G', 'Gly', 'Glycine'),
        'GTA': ('V', 'Val', 'Valine'),
        'GTC': ('V', 'Val', 'Valine'),
        'GTG': ('V', 'Val', 'Valine'),
        'GTT': ('V', 'Val', 'Valine'),
        'TAC': ('Y', 'Tyr', 'Tyrosine'),
        'TAT': ('Y', 'Tyr', 'Tyrosine'),
        'TCA': ('S', 'Ser', 'Serine'),
        'TCC': ('S', 'Ser', 'Serine'),
        'TCG': ('S', 'Ser', 'Serine'),
        'TCT': ('S', 'Ser', 'Serine'),
        'TGC': ('C', 'Cys', 'Cysteine'),
        'TGG': ('W', 'Trp', 'Tryptophan'),
        'TGT': ('C', 'Cys', 'Cysteine'),
        'TTA': ('L', 'Leu', 'Leucine'),
        'TTC': ('F', 'Phe', 'Phenylalanine'),
        'TTG': ('L', 'Leu', 'Leucine'),
        'TTT': ('F', 'Phe', 'Phenylalanine')
    }):

    def _get_codons(s, p=0):
        for i in range(0, len(s), 3):
            codon = s[i + p:i + p + 3]
            if codon:  # don't return blank strings
                yield codon

    verbosity_index = {"single": 0, "short": 1, "long": 2}
    if remove_whitespace is True:
        string = ''.join(string.split())
    if as_codons:
        codons = _get_codons(string, p=phase)
        return list(codons)
    string = string.replace('U', 'T')
    codons = _get_codons(string, p=phase)
    stop_codons = ('TAG', 'TGA', 'TAA')
    amino_acids = []
    v = verbosity_index[verbosity]
    if v == 0:
        join_char = ""
    else:
        join_char = "-"
    for c in codons:
        aa = None
        try:
            aa = codon_map[c.upper()][v]
        except KeyError:
            if c.upper() in stop_codons:
                aa = stop_char
            elif mask:
                aa = 'X'
            else:
                aa = c.lower()
        amino_acids.append(aa)
            
    return join_char.join(amino_acids)