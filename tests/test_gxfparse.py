#!/usr/bin/env python3
"""
Unit tests for GxfParse class.

Test data is embedded inline for portability and speed, with support
for optional external file testing.
"""

import pytest
import sys
from pathlib import Path
import importlib.util

# Load GxfParse directly without going through package __init__
_gxf_path = Path(__file__).parent.parent / "biogl" / "GxfParse.py"
spec = importlib.util.spec_from_file_location("gxfparse_module", _gxf_path)
_gxf_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_gxf_module)
GxfParse = _gxf_module.GxfParse


# =============================================================================
# Test Data (embedded for portability)
# =============================================================================

# Real Ensembl GFF3 examples
GFF3_GENE = "19\thavana\tpseudogene\t60951\t71626\t.\t-\t.\tID=gene:ENSG00000282458;Name=WASH5P;biotype=transcribed_processed_pseudogene;gene_id=ENSG00000282458;version=1"

GFF3_TRANSCRIPT = "19\thavana\tlnc_RNA\t60951\t70976\t.\t-\t.\tID=transcript:ENST00000632506;Parent=gene:ENSG00000282458;Name=WASH5P-206;transcript_id=ENST00000632506;version=1"

# Exon without explicit ID= (tests None return)
GFF3_EXON_NO_ID = "19\thavana\texon\t60951\t61894\t.\t-\t.\tParent=transcript:ENST00000632506;Name=ENSE00003783010;exon_id=ENSE00003783010;rank=3;version=1"

# CDS with phase
GFF3_CDS_PHASE_0 = "19\thavana\tCDS\t110679\t111596\t.\t+\t0\tID=CDS:ENSP00000467301;Parent=transcript:ENST00000585993;protein_id=ENSP00000467301"
GFF3_CDS_PHASE_1 = "19\tensembl_havana\tCDS\t282752\t282809\t.\t-\t1\tID=CDS:ENSP00000329697;Parent=transcript:ENST00000327790"
GFF3_CDS_PHASE_2 = "19\tensembl_havana\tCDS\t288020\t288171\t.\t-\t2\tID=CDS:ENSP00000329697;Parent=transcript:ENST00000327790"

# GTF-style examples
GTF_GENE = 'chr2\tEnsembl\tgene\t5000\t6000\t.\t-\t.\tgene_id "ENSG001"; gene_name "FOO"'
GTF_TRANSCRIPT = 'chr2\tEnsembl\ttranscript\t5000\t6000\t.\t-\t.\tgene_id "ENSG001"; transcript_id "ENST001"'
GTF_EXON = 'chr2\tEnsembl\texon\t5000\t5200\t.\t-\t.\tgene_id "ENSG001"; transcript_id "ENST001"; exon_id "E1"'

# Multiple parents (GFF3 comma-separated)
GFF3_MULTI_PARENT = "chr3\tEnsembl\texon\t7000\t7200\t.\t+\t.\tID=shared_exon;Parent=tx1,tx2,tx3"

# Edge cases
REVERSED_COORDS = "chr4\tEnsembl\tgene\t9000\t8000\t.\t+\t.\tID=reversed"
UNKNOWN_STRAND = "chr5\tEnsembl\tgene\t10000\t11000\t.\t?\t.\tID=unknown_strand"
MRNA_TYPE = "chr6\tEnsembl\tmRNA\t12000\t13000\t.\t+\t.\tID=mrna1;Parent=gene2"
FIVE_PRIME_UTR = "chr7\tEnsembl\tfive_prime_utr\t14000\t14100\t.\t+\t.\tParent=tx1"
WITH_SCORE = "chr1\tEnsembl\ttranscript\t1000\t2000\t100.5\t+\t.\tID=tx1;Parent=gene1"

# Invalid lines
COMMENT_LINE = "# This is a comment"
MALFORMED_LINE = "chr8\tEnsembl\tgene"


# =============================================================================
# Basic Parsing Tests
# =============================================================================

class TestBasicParsing:
    """Test basic line parsing functionality."""

    def test_parse_gff3_gene(self):
        """Test parsing a GFF3 gene line."""
        parsed = GxfParse(GFF3_GENE, 1)
        assert parsed.region == "19"
        assert parsed.start == 60951
        assert parsed.stop == 71626
        assert parsed.strand == "-"
        assert parsed.feat_type == "gene"
        assert parsed.name == "gene:ENSG00000282458"
        assert parsed.line_number == 1

    def test_parse_gff3_transcript(self):
        """Test parsing a GFF3 transcript line."""
        parsed = GxfParse(GFF3_TRANSCRIPT, 2)
        assert parsed.region == "19"
        assert parsed.feat_type == "transcript"
        assert parsed.name == "transcript:ENST00000632506"
        assert parsed.parent == ["gene:ENSG00000282458"]

    def test_parse_gff3_exon_without_id(self):
        """Test that exons without ID= return None (not 'exon_None')."""
        parsed = GxfParse(GFF3_EXON_NO_ID, 3)
        assert parsed.feat_type == "exon"
        assert parsed.name is None  # Breaking change: was 'exon_None'
        assert parsed.parent == ["transcript:ENST00000632506"]

    def test_parse_gtf_gene(self):
        """Test parsing GTF-style gene."""
        parsed = GxfParse(GTF_GENE, 4)
        assert parsed.region == "chr2"
        assert parsed.feat_type == "gene"
        assert parsed.name == "ENSG001"
        assert parsed.strand == "-"

    def test_parse_gtf_transcript(self):
        """Test parsing GTF-style transcript."""
        parsed = GxfParse(GTF_TRANSCRIPT, 5)
        assert parsed.feat_type == "transcript"
        assert parsed.name == "ENST001"
        assert parsed.parent == ["ENSG001"]

    def test_parse_gtf_exon(self):
        """Test parsing GTF-style exon with grandparent."""
        parsed = GxfParse(GTF_EXON, 6)
        assert parsed.feat_type == "exon"
        assert parsed.parent == ["ENST001"]
        assert parsed.grandparent == "ENSG001"


# =============================================================================
# Phase Parsing Tests
# =============================================================================

class TestPhase:
    """Test CDS phase parsing."""

    def test_phase_0(self):
        """Test phase 0 parsing."""
        parsed = GxfParse(GFF3_CDS_PHASE_0, 1)
        assert parsed.phase == 0
        assert parsed.feat_type == "cds"

    def test_phase_1(self):
        """Test phase 1 parsing."""
        parsed = GxfParse(GFF3_CDS_PHASE_1, 2)
        assert parsed.phase == 1

    def test_phase_2(self):
        """Test phase 2 parsing."""
        parsed = GxfParse(GFF3_CDS_PHASE_2, 3)
        assert parsed.phase == 2

    def test_no_phase(self):
        """Test features without phase."""
        parsed = GxfParse(GFF3_GENE, 4)
        assert parsed.phase is None


# =============================================================================
# Parent/Grandparent Tests
# =============================================================================

class TestRelationships:
    """Test parent and grandparent relationships."""

    def test_multiple_parents(self):
        """Test parsing multiple comma-separated parents."""
        parsed = GxfParse(GFF3_MULTI_PARENT, 1)
        assert parsed.parent == ["tx1", "tx2", "tx3"]
        assert len(parsed.parent) == 3

    def test_single_parent(self):
        """Test single parent."""
        parsed = GxfParse(GFF3_TRANSCRIPT, 2)
        assert parsed.parent == ["gene:ENSG00000282458"]
        assert len(parsed.parent) == 1

    def test_grandparent_extraction(self):
        """Test grandparent extraction for exons."""
        parsed = GxfParse(GTF_EXON, 3)
        assert parsed.feat_type == "exon"
        assert parsed.grandparent == "ENSG001"


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_reversed_coordinates(self):
        """Test that reversed coordinates get min/max normalization."""
        parsed = GxfParse(REVERSED_COORDS, 1)
        assert parsed.start == 8000  # min
        assert parsed.stop == 9000   # max

    def test_unknown_strand(self):
        """Test that non +/- strands default to +."""
        parsed = GxfParse(UNKNOWN_STRAND, 2)
        assert parsed.strand == "+"
        # New feature: raw_strand preserves original
        assert parsed.raw_strand == "?"

    def test_mrna_to_transcript_conversion(self):
        """Test that mRNA type converts to transcript."""
        parsed = GxfParse(MRNA_TYPE, 3)
        assert parsed.feat_type == "transcript"
        # New feature: raw_feat_type preserves original
        assert parsed.raw_feat_type == "mRNA"

    def test_utr_type_preservation(self):
        """Test that UTR types preserve their subtype."""
        parsed = GxfParse(FIVE_PRIME_UTR, 4)
        assert parsed.feat_type == "five_prime_utr"

    def test_score_parsing(self):
        """Test optional score field parsing."""
        parsed = GxfParse(WITH_SCORE, 5)
        assert parsed.score == 100.5
        assert isinstance(parsed.score, float)

    def test_no_score(self):
        """Test features without score."""
        parsed = GxfParse(GFF3_GENE, 6)
        assert parsed.score is None


# =============================================================================
# Invalid Input Tests
# =============================================================================

class TestInvalidInput:
    """Test handling of invalid or malformed input."""

    def test_comment_line_raises_typeerror(self):
        """Test that comment lines raise TypeError."""
        with pytest.raises(TypeError):
            GxfParse(COMMENT_LINE, 1)

    def test_malformed_line_raises_typeerror(self):
        """Test that malformed lines raise TypeError."""
        with pytest.raises(TypeError):
            GxfParse(MALFORMED_LINE, 2)

    def test_empty_line_raises_typeerror(self):
        """Test that empty lines raise TypeError."""
        with pytest.raises(TypeError):
            GxfParse("", 3)


# =============================================================================
# New Features Tests
# =============================================================================

class TestNewFeatures:
    """Test new non-breaking features added in refactoring."""

    def test_raw_line_preservation(self):
        """Test that raw_line attribute preserves original."""
        parsed = GxfParse(GFF3_GENE, 1)
        assert parsed.raw_line == GFF3_GENE

    def test_seqid_alias(self):
        """Test that seqid is an alias for region."""
        parsed = GxfParse(GFF3_GENE, 1)
        assert parsed.seqid == parsed.region
        assert parsed.seqid == "19"

    def test_source_extraction(self):
        """Test source field extraction (column 2)."""
        parsed = GxfParse(GFF3_GENE, 1)
        assert parsed.source == "havana"

    def test_raw_feat_type(self):
        """Test raw_feat_type preserves original type string."""
        parsed = GxfParse(MRNA_TYPE, 2)
        assert parsed.raw_feat_type == "mRNA"
        assert parsed.feat_type == "transcript"  # normalized

    def test_raw_strand(self):
        """Test raw_strand preserves original strand symbol."""
        parsed = GxfParse(UNKNOWN_STRAND, 3)
        assert parsed.raw_strand == "?"
        assert parsed.strand == "+"  # normalized


# =============================================================================
# Optional: External File Tests
# =============================================================================

class TestWithExternalFiles:
    """Optional tests using actual GFF3/GTF files if available."""

    @pytest.mark.skipif(
        not Path("~/code/intronIC/data/test_data/Homo_sapiens.Chr19.Ensembl_91.gff3.gz").expanduser().exists(),
        reason="Test data file not available"
    )
    def test_real_ensembl_file(self):
        """Test parsing a real Ensembl GFF3 file (if available)."""
        # Import flex_open directly from module file
        flex_open_path = Path(__file__).parent.parent / "biogl" / "flex_open.py"
        spec = importlib.util.spec_from_file_location("flex_open_module", flex_open_path)
        flex_open_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(flex_open_module)
        flex_open = flex_open_module.flex_open

        test_file = Path("~/code/intronIC/data/test_data/Homo_sapiens.Chr19.Ensembl_91.gff3.gz").expanduser()

        gene_count = 0
        transcript_count = 0
        exon_count = 0

        with flex_open(str(test_file)) as f:
            for line_num, line in enumerate(f, start=1):
                try:
                    parsed = GxfParse(line, line_num)
                    if parsed.feat_type == "gene":
                        gene_count += 1
                    elif parsed.feat_type == "transcript":
                        transcript_count += 1
                    elif parsed.feat_type == "exon":
                        exon_count += 1
                except TypeError:
                    # Skip comment/header lines
                    continue

        # Verify we parsed some features
        assert gene_count > 0, "Should parse some genes"
        assert transcript_count > 0, "Should parse some transcripts"
        assert exon_count > 0, "Should parse some exons"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
