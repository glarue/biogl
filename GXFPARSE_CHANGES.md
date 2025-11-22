# GxfParse Refactoring Summary

## Overview

Refactored `GxfParse` class with type hints, improved documentation, additional convenience attributes, and **opt-in GFF3 spec compliance features** while maintaining backward compatibility.

## Changes Made

### 1. Type Annotations
- Added complete type hints throughout the class
- Parameters and return values now properly typed
- Improved IDE support and static type checking

### 2. New Non-Breaking Features

Added convenience attributes that don't affect existing code:

- `raw_line`: Original line without trailing newline
- `seqid`: Alias for `region` (GFF3 terminology)
- `source`: GFF3 column 2 (source)
- `raw_feat_type`: Original type string from column 3 (before normalization)
- `raw_strand`: Original strand symbol from column 7 (before normalization)
- `score`: Parsed score value as float or None

### 3. Improved Documentation

- Enhanced docstrings with examples
- Better parameter descriptions
- References to GFF3 specification where relevant
- Clear distinction between backwards-compatible and new attributes

### 4. Bug Fixes

- Fixed delimiter usage bug in `get_type()` (was `delimiter.split()` instead of `infostring.split(delimiter)`)
- Added case-insensitive matching in several places
- Improved error handling with explicit TypeError messages

### 5. Enhanced Parent Parsing

Added `__extract_all_values()` helper to properly handle:
- Multiple parent entries: `Parent=ID1;Parent=ID2`
- Comma-separated parents: `Parent=ID1,ID2` (GFF3 spec)
- Mixed formats

### 6. Breaking Change (Intentional)

**Changed behavior for features without explicit IDs:**

**Old behavior:**
```python
# Exon without ID= attribute
parsed.name  # Returns 'exon_None' (string)
```

**New behavior:**
```python
# Exon without ID= attribute
parsed.name  # Returns None (Python None object)
```

**Rationale:**
- More Pythonic (actual `None` instead of string `'None'`)
- Easier to check: `if parsed.name is None` vs checking for string patterns
- intronIC already handles both cases correctly

## Testing

### Unit Tests

Created comprehensive test suite in `tests/test_gxfparse.py`:
- 28 tests covering all functionality
- Real Ensembl GFF3/GTF examples
- Edge cases (reversed coordinates, unknown strand, etc.)
- Phase parsing (0, 1, 2)
- Multiple parents
- GTF and GFF3 formats
- Invalid input handling

**All tests pass:** ✅ 28/28

### Backwards Compatibility Test

Created `test_backwards_compatibility.py`:
- Compares old (git HEAD) vs new (working tree) versions
- Tests with real Ensembl data
- Supports `--allow-breaking-changes` flag
- Documents the `feature_None` → `None` breaking change

**Results:**
```bash
# Without flag: shows breaking change
python3 test_backwards_compatibility.py
# Test 3: name: old='exon_None', new=None

# With flag: all tests pass
python3 test_backwards_compatibility.py --allow-breaking-changes
# ✓ 19/19 tests passed
```

## Impact Analysis

### Impact on intronIC

The only place GxfParse.name is used in intronIC is in `file_io/parsers.py`:

```python
feature_name = line_info.name
if feature_name is None or feature_name == 'exon_None' or 'None' in str(feature_name):
    # Generate location-based ID
```

**This code already handles both the old and new behavior**, so the breaking change is safe for intronIC.

### Impact on Other Projects

If biogl is used elsewhere, this is a **breaking change** and warrants a version bump (e.g., 1.x → 2.0).

Projects using biogl should:
1. Check for `if name is None` instead of string pattern matching
2. Update any code that relies on `'feature_None'` strings

## Files Changed

- `biogl/GxfParse.py` - Refactored class with type hints and new features
- `tests/test_gxfparse.py` - New comprehensive unit test suite
- `test_backwards_compatibility.py` - Backwards compatibility validation
- `GXFPARSE_CHANGES.md` - This document

## New Opt-in GFF3 Spec Compliance Features

### 7. URL Decoding (`url_decode: bool = False`)

**Purpose:** Decode percent-encoded attribute values per GFF3 spec

**Example:**
```python
# Default behavior (backward compatible)
parsed = GxfParse("chr1\t...\tID=gene%3B1", 1)
assert parsed.name == "gene%3B1"  # Not decoded

# With URL decoding enabled
parsed = GxfParse("chr1\t...\tID=gene%3B1", 1, url_decode=True)
assert parsed.name == "gene;1"  # Decoded semicolon
```

**GFF3 spec:** Reserved characters (`;`, `=`, `,`, `%`) must be percent-encoded in attribute values

### 8. Case-Sensitive Matching (`case_sensitive: bool = False`)

**Purpose:** Use case-sensitive attribute name matching per GFF3 spec

**Example:**
```python
# Default: case-insensitive (better for GTF/messy files)
parsed = GxfParse("chr1\t...\tparent=tx1", 1)
assert parsed.parent == ["tx1"]  # Matches despite lowercase

# Case-sensitive per GFF3 spec
parsed = GxfParse("chr1\t...\tparent=tx1", 1, case_sensitive=True)
assert parsed.parent == [None]  # Does NOT match lowercase 'parent'
```

**GFF3 spec:** Attribute names are case-sensitive. `Parent` is not the same as `parent`.

### 9. Strict Coordinate Validation (`strict_coordinates: bool = False`)

**Purpose:** Validate that start ≤ end per GFF3 spec

**Example:**
```python
# Default: auto-correct with min/max swap (permissive)
parsed = GxfParse("chr1\t...\t9000\t8000\t...", 1)
assert parsed.start == 8000  # Corrected
assert parsed.stop == 9000

# Strict validation
parsed = GxfParse("chr1\t...\t9000\t8000\t...", 1, strict_coordinates=True)
# Raises: ValueError("Invalid coordinates: start (9000) > end (8000)")
```

**GFF3 spec:** "Start is always less than or equal to end"

### Usage Examples

```python
# Default behavior (fully backward compatible)
parsed = GxfParse(line, 1)

# Full GFF3 spec compliance
parsed = GxfParse(
    line, 1,
    url_decode=True,
    case_sensitive=True,
    strict_coordinates=True
)

# Mix and match as needed
parsed = GxfParse(line, 1, url_decode=True)  # Just decode URLs
```

## Testing

Enhanced test suite from 28 to 45 tests:
- **17 new tests** for opt-in spec compliance features
- Tests verify backward compatibility (defaults unchanged)
- Tests verify correct behavior with each option enabled
- Tests verify combined options work together

**All tests pass:** ✅ 45/45

## Recommendations

1. **Version bump**: Recommend bumping to 2.0.0 due to breaking change
2. **Changelog**: Document the `feature_None` → `None` change
3. **Migration guide**: Simple for users: just change string checks to `is None`
4. **Opt-in features**: Users can gradually adopt spec compliance features as needed

## References

- [GFF3 Specification](https://gmod.org/wiki/GFF3.html)
- [Ensembl GFF/GTF Guide](https://useast.ensembl.org/info/website/upload/gff.html)
