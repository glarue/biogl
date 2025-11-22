from typing import List, Optional


class GxfParse(object):
    """
    Takes a gff3/gtf/gff annotation line, and returns available metadata
    about it.

    Public attributes (backwards-compatible):
      - bits, region, start, stop, strand, phase, infostring
      - feat_type, parent, grandparent, name, line_number

    New convenience attributes (non-breaking):
      - raw_line  : original line without trailing newline
      - seqid     : alias for region (GFF3 col 1)
      - source    : GFF3 col 2
      - raw_feat_type : original type string (col 3)
      - raw_strand    : original strand symbol from col 7
      - score     : float(score) or None (col 6)
    """

    def __init__(self, line: str, line_number: int):
        # Preserve original line (without newline) for debugging if needed
        self.raw_line: str = line.rstrip("\n")
        self.bits = self.__split_on_tabs(self.raw_line)
        if self.bits is None:
            # Historically this would have raised a TypeError when trying to
            # subscript None. We keep the TypeError but make it explicit.
            raise TypeError("Comment or malformed annotation line")

        try:
            self.region: str = self.bits[0]
            # Alias closer to GFF3 terminology (non-breaking addition)
            self.seqid: str = self.region

            # Extra parsed columns (non-breaking additions)
            self.source: Optional[str] = self.bits[1] if len(self.bits) > 1 else None
            self.raw_feat_type: Optional[str] = (
                self.bits[2] if len(self.bits) > 2 else None
            )

            # start / stop: keep original min/max behaviour
            try:
                self.start: Optional[int] = min(map(int, self.bits[3:5]))
                self.stop: Optional[int] = max(map(int, self.bits[3:5]))
            except (ValueError, TypeError):
                self.start = None
                self.stop = None

            # Strand: keep historical behaviour of collapsing non + / - to '+'
            raw_strand = self.bits[6] if len(self.bits) > 6 else "+"
            self.raw_strand: str = raw_strand  # new: preserve original value
            self.strand: str = raw_strand if raw_strand in ("+", "-") else "+"

            # Phase (GFF3 col 8; only 0/1/2 are valid) :contentReference[oaicite:1]{index=1}
            if len(self.bits) > 7 and self.bits[7] in ["0", "1", "2"]:
                self.phase: Optional[int] = int(self.bits[7])
            else:
                self.phase = None

            # Optional score column (new, non-breaking)
            if len(self.bits) > 5 and self.bits[5] != ".":
                try:
                    self.score: Optional[float] = float(self.bits[5])
                except ValueError:
                    self.score = None
            else:
                self.score = None

            # Attributes / info string (col 9)
            self.infostring: str = self.bits[8] if len(self.bits) > 8 else ""

            # Classification + relationships
            self.feat_type: str = self.get_type()
            self.parent: List[Optional[str]] = self.get_parent()
            self.grandparent: Optional[str] = None

            # Try to get grandparent for child types using gene_id / geneID
            if self.feat_type in ("cds", "exon"):
                self.grandparent = self.__field_match(
                    self.infostring,
                    ["gene_id", "geneId", "geneID"],
                    delimiter=";",
                )

            # Primary identifier
            self.name: Optional[str] = self.get_ID()
            self.line_number: int = line_number

        except TypeError:
            # Preserve original behaviour of bubbling up TypeError
            raise

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def __split_on_tabs(l: str, n: int = 9):
        """
        Checks for a valid line (does not start with #).

        Splits valid line on tabs, and returns a list of the bits
        if the list length is <<n>>. Setting <<n>> to None will return
        the split line regardless of length.
        """
        if l.startswith("#"):
            return None
        # Use strip() as in original implementation
        columns = l.strip().split("\t")
        if n and len(columns) < n:
            return None

        return columns

    @staticmethod
    def __field_match(
        infostring: str,
        tags,
        delimiter: str,
        tag_order: bool = False,
    ) -> Optional[str]:
        """
        Return the value of the first attribute whose key matches any of
        ``tags`` (case-insensitive), using the given ``delimiter``.

        Examples
        --------
        infostring: 'ID=tx1;Parent=g1'
        tags: ['ID=']  -> 'tx1'

        infostring: 'gene_id "G1"; transcript_id "T1"'
        tags: ['gene_id'] -> 'G1'
        """
        if not infostring:
            return None

        if tag_order:
            # Check for first match of tags in order (case-insensitive)
            lower_info = infostring.lower()
            try:
                first_tag = next(t for t in tags if t.lower() in lower_info)
                tags = [first_tag]
            except StopIteration:
                return None

        info_bits = [e.strip() for e in infostring.split(delimiter)]
        try:
            match = next(
                e
                for e in info_bits
                if any(e.lower().startswith(p.lower()) for p in tags)
            )
        except StopIteration:  # no matches found
            return None

        # GFF3-style: key=value :contentReference[oaicite:2]{index=2}
        if "=" in match:
            substring = match.split("=", 1)[1]
        else:
            # GTF-style: key "value"
            pieces = match.split(None, 1)
            if len(pieces) < 2:
                return None
            substring = pieces[1]

        return substring.strip().strip('"')

    @staticmethod
    def __extract_all_values(
        infostring: str,
        key: str,
        delimiter: str = ";",
        comma_split: bool = True,
    ) -> List[str]:
        """
        Extract *all* values for a given key, handling:
          - repeated key entries
          - comma-separated lists (e.g. Parent=ID1,ID2)

        This follows the GFF3 rule that multiple values of the same tag
        are comma-separated. :contentReference[oaicite:3]{index=3}
        """
        if not infostring:
            return []
        key_lower = key.lower()
        values: List[str] = []
        for field in infostring.split(delimiter):
            field = field.strip()
            if not field:
                continue
            if not field.lower().startswith(key_lower):
                continue

            if "=" in field:
                val = field.split("=", 1)[1].strip()
            else:
                pieces = field.split(None, 1)
                if len(pieces) < 2:
                    continue
                val = pieces[1].strip()

            val = val.strip('"')
            if comma_split and "," in val:
                values.extend(v.strip() for v in val.split(",") if v.strip())
            elif val:
                values.append(val)

        return values

    # ------------------------------------------------------------------ #
    # Public methods
    # ------------------------------------------------------------------ #

    def get_type(self, delimiter: str = ";") -> str:
        """
        Classifies annotation lines into type categories,
        taking into account edge cases like 'processed transcript'
        and 'pseudogenic transcript'.
        """
        og_type = (self.bits[2] or "").lower()
        if og_type == "mrna":
            og_type = "transcript"
        if og_type in ("gene", "transcript", "exon", "cds"):
            return og_type

        disqualifying = ["utr", "start", "stop"]
        if any(kw in og_type for kw in disqualifying):
            # UTRs / start_codon / stop_codon retain original subtype
            return og_type

        # Not an obvious type, so search for features of transcripts
        # and genes in infostring to try to infer type

        # BUGFIX: this used to say delimiter.split(self.infostring)
        # Check for explicit mention of transcript in ID
        try:
            id_string = next(
                f.strip()
                for f in self.infostring.split(delimiter)
                if f.strip().startswith("ID")
            )
            if any(tag in id_string.lower() for tag in ("transcript", "mrna")):
                return "transcript"
        except StopIteration:
            pass

        gene_tags = ["gene_id", "geneId", "geneID"]
        transcript_tags = ["transcript_id", "transcriptId", "transcript_ID"]
        # Transcripts first because genes shouldn't have transcript IDs,
        # but transcripts may have gene IDs
        match_type = None
        for ftype, tags in zip(["transcript", "gene"], [transcript_tags, gene_tags]):
            match = self.__field_match(self.infostring, tags, delimiter)
            if match:
                match_type = ftype
                break
        if match_type:
            feat_type = match_type
        else:
            feat_type = og_type

        return feat_type

    def get_ID(self, delimiter: str = ";") -> Optional[str]:
        """
        Finds the ID of a given annotation file line.

        Attempts, in order:
          1. Direct 'ID=' attribute (GFF3-style).
          2. Gene/transcript IDs inferred from typical tags.
          3. Fallback to the first (sole) attribute in the info string.
        """
        infostring = self.infostring

        # First, do it the easy (canonical GFF3) way
        match = self.__field_match(infostring, ["ID="], delimiter)
        if match:
            return match

        # Constrain feature types to simplify indexing
        feat_type = self.feat_type
        if feat_type == "mrna":
            feat_type = "transcript"

        # If there is no 'ID=', try to reference self via other attributes
        gene_tags = ["ID=", "gene_id", "geneId", "geneID"]
        transcript_tags = ["ID=", "transcript_id", "transcriptId", "transcript_ID"]
        tag_selector = {
            "gene": gene_tags,
            "transcript": transcript_tags,
        }
        prefix = None

        try:
            tags = tag_selector[feat_type]
        except KeyError:  # not gene or transcript
            # Get any ID available, prepended with the feature type
            # to keep different features of the same transcript unique
            prefix = self.feat_type
            tags = [
                "transcriptID",
                "transcript_ID",
                "transcript_id",
                "gene_ID",
                "geneID",
                "gene_id",
            ]

        match = self.__field_match(infostring, tags, delimiter, tag_order=True)

        # If nothing matches, return infostring if there's only
        # one tag in it (common for GTF parent features)
        if match is None and infostring and infostring.count(";") < 2:
            match = infostring.split(";")[0].strip()

        if match is None:
            return None

        if prefix:
            match = "{}_{}".format(prefix, match)

        return match

    def get_parent(self, delimiter: str = ";"):
        """
        Retrieves parent information from an annotation line.

        Returns
        -------
        list
            A list of parent IDs. Multiple parents are supported both
            via:
              - Parent=ID1,ID2 (GFF3 spec)
              - repeated Parent=ID1;Parent=ID2 (non-canonical but seen) :contentReference[oaicite:4]{index=4}
        """
        infostring = self.infostring

        # Preferred: explicit Parent= entries, possibly repeated / comma-separated
        parents = self.__extract_all_values(
            infostring, "Parent", delimiter=delimiter, comma_split=True
        )
        if parents:
            return parents

        # Heuristic fallback for formats / producers that don't use Parent=
        feat_type_converter = {"cds": "exon", "mrna": "transcript"}
        feat_type = self.feat_type
        if feat_type in feat_type_converter:
            feat_type = feat_type_converter[feat_type]

        child_tags = [
            "Parent=",
            "transcript_ID",
            "transcriptId",
            "transcript_id",
            "proteinId",
            "protein_ID",
            "protein_id",
        ]
        transcript_tags = [
            "Parent=",
            "gene_ID",
            "geneId",
            "geneID",
            "gene_id",
        ]
        gene_tags = ["Parent="]

        tag_selector = {
            "gene": gene_tags,
            "transcript": transcript_tags,
            "exon": child_tags,
        }
        try:
            tags = tag_selector[feat_type]
        except KeyError:
            tags = child_tags + transcript_tags

        match = self.__field_match(infostring, tags, delimiter, tag_order=True)

        if match is None:
            # No parent information found
            return [None]

        # Split multiple parents per GFF3 spec (Parent=A,B) :contentReference[oaicite:5]{index=5}
        parents = [p.strip() for p in match.split(",") if p.strip()]
        if not parents:
            return [None]

        return parents
