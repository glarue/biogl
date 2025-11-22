#!/usr/bin/env python3
"""
Backwards compatibility test for GxfParse refactoring.
Compares outputs from the old (git HEAD) and new (working tree) versions.

BREAKING CHANGES in new version:
- Features without explicit IDs now return None instead of 'feature_None' strings
  (e.g., exons without ID= attribute return None instead of 'exon_None')
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def get_old_version():
    """Extract the old version of GxfParse from git HEAD."""
    result = subprocess.run(
        ["git", "show", "HEAD:biogl/GxfParse.py"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get old version: {result.stderr}")
    return result.stdout


def test_gxf_lines():
    """Test cases covering different GFF3/GTF scenarios."""
    return [
        # Real Ensembl GFF3 examples
        "19\thavana\tpseudogene\t60951\t71626\t.\t-\t.\tID=gene:ENSG00000282458;Name=WASH5P;biotype=transcribed_processed_pseudogene;description=WAS protein family homolog 5 pseudogene [Source:NCBI gene%3BAcc:375690];gene_id=ENSG00000282458;logic_name=havana;version=1",
        "19\thavana\tlnc_RNA\t60951\t70976\t.\t-\t.\tID=transcript:ENST00000632506;Parent=gene:ENSG00000282458;Name=WASH5P-206;biotype=processed_transcript;tag=basic;transcript_id=ENST00000632506;transcript_support_level=1;version=1",
        "19\thavana\texon\t60951\t61894\t.\t-\t.\tParent=transcript:ENST00000632506;Name=ENSE00003783010;constitutive=0;ensembl_end_phase=-1;ensembl_phase=-1;exon_id=ENSE00003783010;rank=3;version=1",
        "19\thavana\tCDS\t110679\t111596\t.\t+\t0\tID=CDS:ENSP00000467301;Parent=transcript:ENST00000585993;protein_id=ENSP00000467301",
        "19\tensembl_havana\tCDS\t282752\t282809\t.\t-\t1\tID=CDS:ENSP00000329697;Parent=transcript:ENST00000327790;protein_id=ENSP00000329697",
        "19\tensembl_havana\tCDS\t288020\t288171\t.\t-\t2\tID=CDS:ENSP00000329697;Parent=transcript:ENST00000327790;protein_id=ENSP00000329697",

        # Synthetic test cases for edge cases
        # GFF3 gene
        "chr1\tEnsembl\tgene\t1000\t2000\t.\t+\t.\tID=gene1;Name=TEST_GENE",

        # GFF3 transcript with score
        "chr1\tEnsembl\ttranscript\t1000\t2000\t100.5\t+\t.\tID=tx1;Parent=gene1",

        # Multiple parents (GFF3 spec: comma-separated)
        "chr3\tEnsembl\texon\t7000\t7200\t.\t+\t.\tID=shared_exon;Parent=tx1,tx2,tx3",

        # GTF-style gene
        'chr2\tEnsembl\tgene\t5000\t6000\t.\t-\t.\tgene_id "ENSG001"; gene_name "FOO"',

        # GTF-style transcript
        'chr2\tEnsembl\ttranscript\t5000\t6000\t.\t-\t.\tgene_id "ENSG001"; transcript_id "ENST001"',

        # GTF-style exon with grandparent
        'chr2\tEnsembl\texon\t5000\t5200\t.\t-\t.\tgene_id "ENSG001"; transcript_id "ENST001"; exon_id "E1"',

        # Reversed coordinates (tests min/max behavior)
        "chr4\tEnsembl\tgene\t9000\t8000\t.\t+\t.\tID=reversed",

        # Non-standard strand (should default to +)
        "chr5\tEnsembl\tgene\t10000\t11000\t.\t?\t.\tID=unknown_strand",

        # mRNA -> transcript conversion
        "chr6\tEnsembl\tmRNA\t12000\t13000\t.\t+\t.\tID=mrna1;Parent=gene2",

        # UTR types (should preserve subtype)
        "chr7\tEnsembl\tfive_prime_UTR\t14000\t14100\t.\t+\t.\tParent=tx1",
        "chr7\tEnsembl\tthree_prime_UTR\t15000\t15100\t.\t+\t.\tParent=tx1",

        # Comment line (should raise TypeError)
        "# This is a comment",

        # Malformed line (too few columns)
        "chr8\tEnsembl\tgene",
    ]


def compare_attribute(name, old_val, new_val):
    """Compare a single attribute, return True if compatible."""
    # Handle None comparisons
    if old_val is None and new_val is None:
        return True

    # For lists, compare sorted versions (order shouldn't matter for parents)
    if isinstance(old_val, list) and isinstance(new_val, list):
        return sorted(str(x) for x in old_val) == sorted(str(x) for x in new_val)

    # For numeric types, allow type conversion (int/float)
    if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
        return old_val == new_val

    # String comparison
    return str(old_val) == str(new_val)


def test_backwards_compatibility(allow_breaking_changes: bool = False):
    """Main test runner.

    Args:
        allow_breaking_changes: If True, allow known breaking changes
                                (features without IDs returning None instead of 'feature_None')
    """
    # Get old version
    old_code = get_old_version()

    # Write old version to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='_old.py', delete=False) as f:
        old_path = f.name
        f.write(old_code)

    try:
        # Import old version
        import importlib.util
        spec_old = importlib.util.spec_from_file_location("gxf_old", old_path)
        mod_old = importlib.util.module_from_spec(spec_old)
        spec_old.loader.exec_module(mod_old)
        GxfParse_old = mod_old.GxfParse

        # Import new version directly from file
        new_path = Path(__file__).parent / "biogl" / "GxfParse.py"
        spec_new = importlib.util.spec_from_file_location("gxf_new", new_path)
        mod_new = importlib.util.module_from_spec(spec_new)
        spec_new.loader.exec_module(mod_new)
        GxfParse_new = mod_new.GxfParse

        # Core attributes that must be backwards compatible
        core_attrs = [
            'bits', 'region', 'start', 'stop', 'strand', 'phase',
            'infostring', 'feat_type', 'parent', 'grandparent', 'name'
        ]

        test_lines = test_gxf_lines()
        failures = []
        successes = 0

        for i, line in enumerate(test_lines, 1):
            print(f"\nTest {i}: {line[:60]}...")

            # Test both versions
            old_obj = None
            new_obj = None
            old_error = None
            new_error = None

            try:
                old_obj = GxfParse_old(line, i)
            except Exception as e:
                old_error = type(e).__name__

            try:
                new_obj = GxfParse_new(line, i)
            except Exception as e:
                new_error = type(e).__name__

            # Check error compatibility
            if old_error or new_error:
                if old_error == new_error:
                    print(f"  ✓ Both raised {old_error}")
                    successes += 1
                else:
                    failures.append(f"Test {i}: Error mismatch - old: {old_error}, new: {new_error}")
                    print(f"  ✗ Error mismatch - old: {old_error}, new: {new_error}")
                continue

            # Compare core attributes
            mismatches = []
            for attr in core_attrs:
                old_val = getattr(old_obj, attr, "<missing>")
                new_val = getattr(new_obj, attr, "<missing>")

                if not compare_attribute(attr, old_val, new_val):
                    # Check if this is a known breaking change (feature_None -> None)
                    if (allow_breaking_changes and attr == 'name' and
                        isinstance(old_val, str) and '_None' in old_val and new_val is None):
                        continue  # Allow this breaking change
                    mismatches.append(f"{attr}: old={old_val!r}, new={new_val!r}")

            if mismatches:
                failures.append(f"Test {i} - {line[:40]}:\n  " + "\n  ".join(mismatches))
                print(f"  ✗ Mismatches found:")
                for m in mismatches:
                    print(f"    - {m}")
            else:
                print(f"  ✓ All core attributes match")
                successes += 1

        # Report results
        print("\n" + "="*70)
        print(f"RESULTS: {successes}/{len(test_lines)} tests passed")
        print("="*70)

        if failures:
            print("\nFAILURES:")
            for f in failures:
                print(f"\n{f}")
            return False
        else:
            print("\n✓ All backwards compatibility tests passed!")
            return True

    finally:
        Path(old_path).unlink()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test GxfParse backwards compatibility')
    parser.add_argument('--allow-breaking-changes', action='store_true',
                       help='Allow known breaking changes (feature_None -> None)')
    args = parser.parse_args()

    success = test_backwards_compatibility(allow_breaking_changes=args.allow_breaking_changes)
    sys.exit(0 if success else 1)
