# GxfParse Refactoring Summary

## Overview

Refactored `GxfParse` class with type hints, improved documentation, and additional convenience attributes while maintaining API compatibility with one intentional breaking change.

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

## Recommendations

1. **Version bump**: Recommend bumping to 2.0.0 due to breaking change
2. **Changelog**: Document the `feature_None` → `None` change
3. **Migration guide**: Simple for users: just change string checks to `is None`

## References

- [GFF3 Specification](https://gmod.org/wiki/GFF3.html)
- [Ensembl GFF/GTF Guide](https://useast.ensembl.org/info/website/upload/gff.html)
