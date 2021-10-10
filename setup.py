from setuptools import setup


## INFOS ##
package     = 'brs_utils'
descr       = 'Generic utilities'
url         = 'https://github.com/brsynth/brs-utils'
authors     = 'Joan Hérisson'
corr_author = 'joan.herisson@univ-evry.fr'

## LONG DESCRIPTION
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

def get_version(filename: str = None) -> str:
    if filename is None:
        filename = 'CHANGELOG.md'
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('##'):
            from re import search
            m = search("\[(.+)\]", line)
            if m:
                return m.group(1)

setup(
    name                          = package,
    version                       = get_version('CHANGELOG.md'),
    author                        = authors,
    author_email                  = corr_author,
    description                   = descr,
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
    url                           = url,
    packages                      = [package],
    package_dir                   = {package: package},
    include_package_data          = True,
    test_suite                    = 'pytest',
    license                       = 'MIT',
    classifiers                   = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires               = '>=3.7',
)

