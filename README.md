# biogl

[![PyPI version](https://badge.fury.io/py/biogl.svg)](https://badge.fury.io/py/biogl)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of useful small bioinformatics functions for working with genomic data formats.

## Features

- **GFF3/GTF Parsing**: Comprehensive parser with type hints and opt-in GFF3 spec compliance
- **FASTA Utilities**: Functions for parsing and manipulating FASTA files
- **Coordinate Operations**: Tools for working with genomic coordinates
- **Type Safety**: Full type hints for better IDE support and static analysis
- **Well Tested**: Comprehensive test suite with real genomic data

## Installation

### Using pip (recommended)

```bash
python3 -m pip install biogl
```

### Development Installation

```bash
git clone https://github.com/grahamlarue/biogl.git
cd biogl
pip install -e ".[dev]"
```

## Quick Start

```python
import biogl

# Parse a GFF3/GTF line
from biogl import GxfParse

line = "chr1\tEnsembl\tgene\t1000\t2000\t.\t+\t.\tID=gene1;Name=TEST"
parsed = GxfParse(line, line_number=1)

print(parsed.region)      # chr1
print(parsed.start)       # 1000
print(parsed.stop)        # 2000
print(parsed.strand)      # 1 (normalized)
print(parsed.name)        # gene1
print(parsed.attributes)  # {'ID': 'gene1', 'Name': 'TEST'}

# Enable GFF3 spec compliance features
parsed = GxfParse(
    line,
    line_number=1,
    url_decode=True,        # Decode percent-encoded values
    case_sensitive=True,    # Case-sensitive attribute matching
    strict_coordinates=True # Validate start <= end
)

# Parse FASTA files
from biogl import fasta_parse

for header, sequence in fasta_parse("genome.fa"):
    print(f"{header}: {len(sequence)} bp")

# Work with coordinates
from biogl import coord_overlap

overlap = coord_overlap(100, 200, 150, 250)  # Returns 50

# Reverse complement
from biogl import rev_comp

seq = "ATCG"
rc = rev_comp(seq)  # Returns "CGAT"
```

## Key Modules

- `GxfParse`: Parse GFF3/GTF annotation files with full type hints
- `fasta_parse`: Efficient FASTA file parsing
- `coord_overlap`: Calculate coordinate overlaps
- `rev_comp`: Reverse complement DNA sequences
- `translate`: Translate DNA to protein
- `flex_open`: Open compressed or uncompressed files transparently
- `window`: Sliding window generator
- And more...

## Breaking Changes in v3.0.0

**Important**: Version 3.0.0 introduces breaking changes to `GxfParse`:

- Features without explicit IDs now return `None` instead of `'feature_None'` strings
- **Migration**: Change `if name == 'exon_None'` to `if name is None`

See [CHANGELOG.md](CHANGELOG.md) for full details.

## Documentation

For detailed documentation on each module, use Python's built-in help:

```python
from biogl import GxfParse
help(GxfParse)
```

## Requirements

- Python 3.10+
- smart_open

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Graham Larue (egrahamlarue@gmail.com)

## Links

- [PyPI](https://pypi.org/project/biogl/)
- [GitHub](https://github.com/grahamlarue/biogl)
- [Issues](https://github.com/grahamlarue/biogl/issues)
- [Changelog](CHANGELOG.md)
