class GxfParse(object):
    """
    Takes a gff3/gtf/gff annotation line, and returns available metadata
    about it.

    """
    def __init__(self, line, line_number):
        self.bits = self.__split_on_tabs(line)
        try:
            self.region = self.bits[0]
            try:
                self.start = min(map(int, self.bits[3:5]))
                self.stop = max(map(int, self.bits[3:5]))
            except ValueError:
                self.start = None
                self.stop = None
            self.strand = self.bits[6]
            if self.strand not in ('+', '-'):
                self.strand = '+'
            if self.bits[7] in ['0', '1', '2']:
                self.phase = int(self.bits[7])
            else:
                self.phase = None
            self.infostring = self.bits[8]
            # self.feat_type = self.bits[2].lower()
            self.feat_type = self.get_type()
            self.parent = self.get_parent()
            self.grandparent = None
            # try to get grandparent for child types
            if self.feat_type in ('cds', 'exon'):
                self.grandparent = self.__field_match(
                    self.infostring, ['gene_id', 'geneID'], delimiter=';')
            self.name = self.get_ID()
            self.line_number = line_number
        except TypeError:
            raise

    @staticmethod
    def __split_on_tabs(l, n=9):
        """
        Checks for a valid line (does not start with #).

        Splits valid line on tabs, and returns a list of the bits
        if the list length is <<n>>. Setting <<n>> to None will return
        the split line regardless of length.

        """
        if l.startswith('#'):
            return None
        columns = l.strip().split("\t")
        if n and len(columns) < n:
            return None
            
        return columns

    @staticmethod
    def __field_match(infostring, tags, delimiter, tag_order=False):
        if tag_order:
            # check for first match of tags in order
            try:
                tags = [next(t for t in tags if t.lower() in infostring.lower())]
            except StopIteration:
                return None
        info_bits = [e.strip() for e in infostring.split(delimiter)]
        try:
            match = next(
                e for e in info_bits
                if any(e.lower().startswith(p.lower()) for p in tags))
        except StopIteration:  # no matches found
            return None
        if "=" in match:
            substring = match.split("=")[1]
        else:
            substring = match.split()[1]

        return substring.strip("\"")


    def get_type(self, delimiter=';'):
        """
        Classifies annotation lines into type categories,
        taking into account edge cases like 'processed transcript'
        and 'pseudogenic transcript'.

        """
        og_type = self.bits[2].lower()
        if og_type == 'mrna':
            og_type = 'transcript'
        if og_type in ('gene', 'transcript', 'exon', 'cds'):
            return og_type

        disqualifying = ['utr', 'start', 'stop']
        if any(kw in og_type for kw in disqualifying):
            return og_type

        # Not an obvious type, so search for features of transcripts
        # and genes in infostring to try to infer type

        # check for explicit mention of transcript in ID
        try:
            id_string = next(
                (f for f in delimiter.split(self.infostring)
                if f.startswith("ID")))

            if any(tag in id_string for tag in ('transcript', 'mrna')):
                return 'transcript'
        except StopIteration:
            pass

        gene_tags = ["gene_id", "geneId"]
        transcript_tags = ["transcriptId", "transcript_ID"]
        # Transcripts first because genes shouldn't have transcript IDs,
        # but transcripts may have gene IDs
        match_type = None
        for ftype, tags in zip(
                ['transcript', 'gene'], [transcript_tags, gene_tags]
        ):
            match = self.__field_match(self.infostring, tags, delimiter)
            if match:
                match_type = ftype
                break
        if match_type:
            feat_type = match_type
        else:
            feat_type = og_type

        return feat_type


    def get_ID(self, delimiter=";"):
        """
        Finds the ID of a given annotation file line.

        """
        # first, do it the easy way
        prefix = None
        infostring = self.infostring
        match = self.__field_match(infostring, ["ID="], delimiter)
        if match:
            return match

        # Constrain feature types to simplify indexing
        feat_type = self.feat_type
        if feat_type == "mrna":
            feat_type = "transcript"
        # all get lowercased in the comparison
        # if is no 'ID=', should reference self via others
        gene_tags = ["ID=", "gene_id", "geneId"]
        transcript_tags = ["ID=", "transcriptId", "transcript_ID"]
        tag_selector = {
            "gene": gene_tags,
            "transcript": transcript_tags
        }
        try:
            tags = tag_selector[feat_type]
        except KeyError:  # not gene or transcript
            # get any ID available, prepended with the feature type
            # to keep different features of the same transcript unique
            prefix = self.feat_type
            tags = ['transcriptID', 'transcript_ID', 'gene_ID', 'geneID']

        match = self.__field_match(
            infostring, tags, delimiter, tag_order=True)

        # if nothing matches, return infostring if there's only
        # one tag in it (common for gtf parent features)
        if match is None and infostring.count(";") < 2:
            match = infostring.split(";")[0]
        if prefix:
            match = '{}_{}'.format(prefix, match)

        return match


    def get_parent(self, delimiter=";"):
        """
        Retrieves parent information from an annotation line.

        """
        # do it the easy way first
        infostring = self.infostring
        match = self.__field_match(infostring, ["Parent="], delimiter)
        if not match:
            feat_type_converter = {"cds": "exon", "mrna": "transcript"}
            feat_type = self.feat_type
            if feat_type in feat_type_converter:
                feat_type = feat_type_converter[feat_type]
            child_tags = [
                "Parent=", "transcript_ID",
                "transcriptId", "proteinId", "protein_ID"
            ]
            transcript_tags = ["Parent=", "gene_ID", "geneId"]
            gene_tags = ["Parent="]
            tag_selector = {
                "gene": gene_tags,
                "transcript": transcript_tags,
                "exon": child_tags
            }
            try:
                tags = tag_selector[feat_type]
            except KeyError:
                # tags = list(set(child_tags + transcript_tags))
                tags = child_tags + transcript_tags
            match = self.__field_match(infostring, tags, delimiter, tag_order=True)
        try:
            match = match.split(',') # updated GFF3 spec can list multiple parents
        except:
            match = [None]

        return match