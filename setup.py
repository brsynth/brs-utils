## INFOS ##
name        = 'brs_utils'
descr       = 'Basic utilities'
url         = f'https://github.com/brsynth/{name}'
authors     = 'Joan Hérisson'
corr_author = 'joan.herisson@univ-evry.fr'
###########

###########
from setuptools import (
    setup,
    find_packages
)
from os import path as os_path

here = os_path.dirname(os_path.realpath(__file__))
version_file = os_path.join(here, name, '_version.py')
exec(open(f"{version_file}").read())  # loads __version__
description = open(
    os_path.join(
        here,
        'README.md'
    ),
    encoding='utf-8'
).read()

setup(
    name                          = name,
    version                       = __version__,
    author                        = authors,
    author_email                  = corr_author,
    description                   = descr,
    long_description              = description,
    long_description_content_type = 'text/markdown',
    url                           = url,
    packages                      = find_packages(exclude=""),
#    packages                      = [src_dir],
#    package_dir                   = {package: package},
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

