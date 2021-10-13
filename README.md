# brs_utils
Basic Utilities
| Name | Downloads | Version | Platforms |
| --- | --- | --- | --- |
| [![Conda Recipe](https://img.shields.io/badge/recipe-brs_utils-green.svg)](https://anaconda.org/conda-forge/brs_utils) | [![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/brs_utils.svg)](https://anaconda.org/conda-forge/brs_utils) | [![Conda Version](https://img.shields.io/conda/vn/conda-forge/brs_utils.svg)](https://anaconda.org/conda-forge/brs_utils) | [![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/brs_utils.svg)](https://anaconda.org/conda-forge/brs_utils) |

## Description
*brs_utils* provides some basic functions useful to handle files, lists, logger, printing...

## Installation
```sh
conda install -c conda-forge brs_utils
``` 

## Usage
Example: Computes the deep size of an object.
After a git clone:

```python
from brs_utils import total_size
total_size('tests/data/1l_file.txt')
```

## Tests
You need to install *pytest* and *pytest-cov* if it's not done yet (`conda install pytest pytest-cov`).
```bash
cd <repository>
python -m pytest -v --cov --cov-report term-missing
```
## CI/CD
For further tests and development tools, a CI toolkit is provided in `ci` folder (see [ci/README.md](ci/README.md)).

## Authors
* **Joan Hérisson**

## Licence
brs-utils is released under the MIT licence. See the LICENCE file for details.
