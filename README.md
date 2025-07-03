
# yuma_tools

`yuma_tools` is a Python library for downloading and parsing YUMA-format GPS almanac files.

## Installation

```bash
pip install .
```

## Usage

```python
from yuma_tools import download_yuma_almanac, yumaread

file = download_yuma_almanac(date(2025, 6, 23))
df = yumaread(file, display=True)
```
