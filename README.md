# brs-utils

**Generic Utilities**

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/brs_utils/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/brs_utils) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/brs_utils/badges/version.svg)](https://anaconda.org/conda-forge/brs_utils)

## Installation

```sh
conda create --name <myenv>
conda activate <myenv>
conda install -c brsynth -c conda-forge brs_utils
``` 

## Usage

Example: Computes the deep size of an object.

After a git clone:

```python
from brs_utils import total_size
total_size('tests/data/1l_file.txt')
```

## Utilities

### total_size
Computes the deep size of an object.

### print functions
Defines some fancy print functions

### download, extract_gz, download_and_extract_gz
Functions to handle download and extract files

### file_length
Returns the number of lines of the given file

### logger
Create a logger from name and a log level. Handle argparse with `add_arguments` function which provides standard cli arguments.

## Tests

You need to install *pytest* and *pytest-cov* if it's not done yet (`conda install pytest pytest-cov`).

```bash
cd <repository>
cd tests
pytest -v --cov --cov-report term-missing
```

## CI/CD
For further tests and development tools, a CI toolkit is provided in `ci` folder (see [ci/README.md](ci/README.md)).


## Authors

* **Melchior du Lac**
* **Joan Hérisson**


## Licence
brs-utils is released under the MIT licence. See the LICENCE file for details.
