from setuptools import setup
from os         import path   as os_path
from re         import search as re_search

_readme = 'README.md'

with open(_readme, 'r', encoding='utf-8') as f:
    long_description = f.read()

# _extras_path = 'extras'
# with open(_extras_path+'/.env', 'r', encoding='utf-8') as f:
#     for line in f:
#         if line.startswith('PACKAGE='):
#             _package = line.splitlines()[0].split('=')[1].lower()
#         if line.startswith('URL='):
#             _url = line.splitlines()[0].split('=')[1].lower()
#         if line.startswith('AUTHORS='):
#             _authors = line.splitlines()[0].split('=')[1].lower()
#         if line.startswith('DESCR='):
#             _descr = line.splitlines()[0].split('=')[1].lower()
#         if line.startswith('CORR_AUTHOR='):
#             _corr_author = line.splitlines()[0].split('=')[1].lower()
package = 'brs_utils'
url = 'https://github.com/brsynth/brs-utils'
authors = 'Joan Hérisson'
corr_author = 'joan.herisson@univ-evry.fr'
descr = 'Generic utilities'

# _version = os_path.join(
#     _package,
#     '_version.py'
# )
# with open(_version, 'r') as f:
#     m = re_search('"(.+)"', f.readline().split('=')[1])
#     if m:
#         version = m.group(1)
_release = 'CHANGELOG.md'
with open(_release, 'r') as f:
    lines = f.readlines()
pattern = "\[(.+)\]"
for line in lines:
    if line.startswith('##'):
        import re
        m = re.search(pattern, line)
        if m:
            version = m.group(1)
        break


setup(
    name                          = package,
    version                       = version,
    author                        = authors,
    author_email                  = corr_author,
    description                   = descr,
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
    url                           = url,
    packages                      = [package],
    package_dir                   = {package: package},
    include_package_data          = True,
    # install_requires              = required,
    test_suite                    = 'pytest',
    license                       = 'MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires               = '>=3.7',
)

