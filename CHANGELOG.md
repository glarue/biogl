# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2025-11-22

### Fixed

- **fasta_parse**: Added missing `PathLike` import from `os` module that caused import errors

## [3.0.0] - 2025-11-22

### Breaking Changes

- **GxfParse**: Features without explicit IDs now return `None` instead of `'feature_None'` strings
  - **Impact**: Code checking for string patterns like `'exon_None'` needs to check for `None` instead
  - **Migration**: Change `if name == 'exon_None'` to `if name is None`
  - **Rationale**: More Pythonic behavior with actual `None` values instead of string representations

### Added

- **GxfParse**: Comprehensive type hints throughout the class for better IDE support and static type checking
- **GxfParse**: New convenience attributes (backward compatible):
  - `raw_line`: Original line without trailing newline
  - `seqid`: Alias for `region` (GFF3 terminology)
  - `source`: GFF3 column 2 (source)
  - `raw_feat_type`: Original type string from column 3 (before normalization)
  - `raw_strand`: Original strand symbol from column 7 (before normalization)
  - `score`: Parsed score value as float or None
- **GxfParse**: Opt-in GFF3 spec compliance features (all default to False for backward compatibility):
  - `url_decode` parameter: Decode percent-encoded attribute values per GFF3 spec (e.g., `%3B` → `;`)
  - `case_sensitive` parameter: Use case-sensitive attribute name matching per GFF3 spec
  - `strict_coordinates` parameter: Validate that start ≤ end, raising ValueError if violated
- **GxfParse**: Enhanced parent parsing to properly handle multiple formats:
  - Multiple parent entries: `Parent=ID1;Parent=ID2`
  - Comma-separated parents: `Parent=ID1,ID2` (GFF3 spec)
  - Mixed formats
- Comprehensive test suite with 45 tests covering all functionality
- Documentation of changes in `GXFPARSE_CHANGES.md`

### Fixed

- **GxfParse**: Fixed delimiter usage bug in `get_type()` method
- **GxfParse**: Improved error handling with explicit TypeError messages

### Documentation

- Enhanced docstrings with examples and better parameter descriptions
- Added references to GFF3 specification where relevant
- Clear distinction between backwards-compatible and new attributes

## [2.4.0] - Previous Release

(Previous changelog entries would go here)
