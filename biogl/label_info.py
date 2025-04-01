def label_info(intron_label, *args):
    """
    Takes an intronIC label and any of the
    following keywords to specify desired
    information: "gene", "transcript",
    "species", "score", "index", "out_of".
    Returns a list of specified features.

    """
    import re
    
    reG=re.compile(r"^[^-]+-([^@]+)")
    reT=re.compile(r"^[^-]+-(?:[^@]+)@(.+)-intron")
    reP=re.compile(r"-intron_([^;]+)")
    species = intron_label.split("-")[0]
    try:
        score = intron_label.split(";")[-1].rstrip("%")
    except IndexError:
        score = None
    position = reP.findall(intron_label)[0]
    index = position.split("(")[0]
    out_of = position.split("(")[1].split(")")[0]
    gene = reG.search(intron_label).group(1)
    transcript = reT.search(intron_label).group(1)
    argMap = {  # associate variables with args
        "gene": gene,
        "transcript": transcript,
        "species": species,
        "score": score,
        "index": index,
        "out_of": out_of
    }
    intron_feats = []
    for arg in args:
        intron_feats.append(argMap[arg])

    return intron_feats