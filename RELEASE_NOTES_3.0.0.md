# biogl 3.0.0 Release Notes

## 🎉 Major Release: Breaking Changes and GFF3 Spec Compliance

This release represents a significant upgrade to the `biogl` package, with a focus on the `GxfParse` class. It includes breaking changes, comprehensive type hints, opt-in GFF3 specification compliance features, and professional packaging improvements.

---

## ⚠️ Breaking Changes

### GxfParse: `None` Instead of String Literals

**Previous behavior (v2.x):**
```python
# Exon without ID= attribute
parsed = GxfParse(exon_line, 1)
parsed.name  # Returns 'exon_None' (string)
```

**New behavior (v3.0.0):**
```python
# Exon without ID= attribute
parsed = GxfParse(exon_line, 1)
parsed.name  # Returns None (Python None object)
```

**Why this change?**
- More Pythonic: Use actual `None` instead of string representations
- Easier null checks: `if parsed.name is None` vs pattern matching
- Type safety: Better compatibility with type checkers

**Migration guide:**
```python
# Old code
if feature_name == 'exon_None' or 'None' in str(feature_name):
    # handle missing ID

# New code (recommended)
if feature_name is None:
    # handle missing ID
```

**Impact:** This change affects code that checks for features without explicit IDs. The `intronIC` codebase already handles both patterns correctly, making this change safe for existing users of `biogl` in that context.

---

## ✨ New Features

### 1. Comprehensive Type Hints

All methods and attributes in `GxfParse` now have complete type annotations:

```python
def __init__(
    self,
    line: str,
    line_number: int,
    *,  # Keyword-only arguments below
    url_decode: bool = False,
    case_sensitive: bool = False,
    strict_coordinates: bool = False,
) -> None:
    ...

def get_parent(self, delimiter: str = ";") -> Sequence[Optional[str]]:
    ...
```

**Benefits:**
- Better IDE autocompletion and error detection
- Static type checking with mypy
- Improved code documentation
- Added `py.typed` marker for PEP 561 compliance

### 2. Opt-in GFF3 Specification Compliance

Three new **optional** parameters enable strict GFF3 compliance while maintaining 100% backward compatibility:

#### a) URL Decoding (`url_decode: bool = False`)

Decode percent-encoded attribute values per GFF3 specification.

```python
# Default: no decoding (backward compatible)
parsed = GxfParse("chr1\t...\tID=gene%3B1", 1)
assert parsed.name == "gene%3B1"  # Encoded

# With URL decoding
parsed = GxfParse("chr1\t...\tID=gene%3B1", 1, url_decode=True)
assert parsed.name == "gene;1"  # Decoded semicolon
```

**GFF3 spec:** Reserved characters (`;`, `=`, `,`, `%`) must be percent-encoded in attribute values.

#### b) Case-Sensitive Matching (`case_sensitive: bool = False`)

Use case-sensitive attribute name matching per GFF3 specification.

```python
# Default: case-insensitive (better for messy files/GTF)
parsed = GxfParse("chr1\t...\tparent=tx1", 1)
assert parsed.parent == ["tx1"]  # Matches despite lowercase

# Strict GFF3: case-sensitive
parsed = GxfParse("chr1\t...\tparent=tx1", 1, case_sensitive=True)
assert parsed.parent == [None]  # Does NOT match lowercase 'parent'
```

**GFF3 spec:** Attribute names are case-sensitive. `Parent` ≠ `parent`.

#### c) Strict Coordinate Validation (`strict_coordinates: bool = False`)

Validate that start ≤ end, raising `ValueError` if violated.

```python
# Default: auto-correct with min/max (permissive)
parsed = GxfParse("chr1\t...\t9000\t8000\t...", 1)
assert parsed.start == 8000  # Auto-corrected
assert parsed.stop == 9000

# Strict validation
try:
    parsed = GxfParse("chr1\t...\t9000\t8000\t...", 1, strict_coordinates=True)
except ValueError as e:
    print(e)  # "Invalid coordinates: start (9000) > end (8000)"
```

**GFF3 spec:** "Start is always less than or equal to end."

#### Usage Examples

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
parsed = GxfParse(line, 1, url_decode=True)  # Just URL decoding
```

### 3. New Convenience Attributes

All backward-compatible additions:

```python
parsed = GxfParse(gff3_line, 1)

# New attributes
parsed.raw_line         # Original line without trailing newline
parsed.seqid            # Alias for region (GFF3 col 1 name)
parsed.source           # GFF3 col 2 (source)
parsed.raw_feat_type    # Original type string before normalization
parsed.raw_strand       # Original strand symbol before normalization
parsed.score            # Parsed as float or None (GFF3 col 6)
```

### 4. Enhanced Parent Parsing

Now properly handles all GFF3 parent formats:

- Multiple parent entries: `Parent=ID1;Parent=ID2`
- Comma-separated parents: `Parent=ID1,ID2` (GFF3 spec)
- Mixed formats
- URL-encoded parent IDs (when `url_decode=True`)

---

## 🔧 Bug Fixes

1. **Fixed delimiter bug in `get_type()`**: Was incorrectly calling `delimiter.split()` instead of `infostring.split(delimiter)`
2. **Improved error handling**: Explicit `TypeError` messages for malformed lines
3. **Type safety fixes**:
   - Changed `parent` attribute from `List[Optional[str]]` to `Sequence[Optional[str]]` for proper covariance
   - Fixed type narrowing for `bits` attribute after `None` check

---

## 📦 Packaging Improvements

### PyPI Enhancements

- **Enhanced README** with badges, quick start examples, and migration guide
- **Comprehensive metadata** in `pyproject.toml`:
  - Keywords: `bioinformatics`, `genomics`, `GFF3`, `GTF`, `FASTA`, etc.
  - PyPI classifiers for better discoverability
  - Project URLs (homepage, repository, changelog, issues)
  - Development dependencies specification
- **LICENSE file** (MIT)
- **CHANGELOG.md** following Keep a Changelog format
- **py.typed marker** for PEP 561 type hint distribution

### Development Workflow

- **GitHub Actions CI** for automated testing across:
  - OS: Ubuntu, macOS, Windows
  - Python: 3.10, 3.11, 3.12
  - Includes linting (black, flake8) and type checking (mypy)
- **Comprehensive .gitignore** for Python projects
- **Development dependencies** clearly specified in `pyproject.toml`

---

## 🧪 Testing

### Comprehensive Test Suite

- **45 total tests** (28 core + 17 spec compliance)
- Real Ensembl GFF3/GTF examples
- 100% test pass rate
- Tests verify:
  - Backward compatibility (all defaults unchanged)
  - Each opt-in feature individually
  - Combined feature usage
  - Edge cases and error conditions

### Test Coverage

```python
# Core functionality (28 tests)
- Basic GFF3 parsing
- GTF format support
- Parent/grandparent relationships
- Phase parsing
- Multiple parents
- Edge cases

# Spec compliance (17 tests)
- URL decoding scenarios
- Case-sensitive matching
- Strict coordinate validation
- Combined modes
```

---

## 📚 Documentation

- **Enhanced docstrings** with examples and parameter descriptions
- **GFF3 spec references** where relevant
- **Clear migration guide** for breaking changes
- **Type hints** throughout for better IDE support
- **GXFPARSE_CHANGES.md** with detailed technical documentation

---

## 🔗 References

- [GFF3 Specification](https://gmod.org/wiki/GFF3.html)
- [Ensembl GFF/GTF Guide](https://useast.ensembl.org/info/website/upload/gff.html)
- [PEP 561: Distributing Type Information](https://www.python.org/dev/peps/pep-0561/)

---

## 📥 Installation

```bash
# Upgrade to v3.0.0
pip install --upgrade biogl

# Or install fresh
pip install biogl==3.0.0

# Verify version
python -c "import biogl; print(biogl.__version__)"
```

---

## 🙏 Acknowledgments

This release was developed with assistance from [Claude Code](https://claude.com/claude-code), Anthropic's AI coding assistant.

---

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🐛 Issues

Report issues at: https://github.com/grahamlarue/biogl/issues

---

**Package:** biogl
**Version:** 3.0.0
**Release Date:** 2025-11-22
**License:** MIT
**PyPI:** https://pypi.org/project/biogl/3.0.0/
