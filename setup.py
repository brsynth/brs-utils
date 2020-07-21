from setuptools import setup
from pathlib import Path

_readme = 'README.md'

_extras_path = 'extras'

with open(_extras_path+'/.env', 'r') as f:
    line = f.readline()
    if line.startswith('PACKAGE='):
        _package = line.splitlines()[0].split('=')[1].lower()

with open(_readme, 'r') as f:
    long_description = f.read()

required = []
with open(_extras_path+'/requirements.txt', 'r') as f:
    required = [line[:-1] for line in f]

_release = 'RELEASE'

with open(_release, 'r') as f:
    _version = f.readline().split()[0]

setup(
    name=_package,
    version=_version,
    author='Melchior du Lac, Joan Hérisson',
    author_email='joan.herisson@univ-evry.fr',
    description='BRSynth Utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brsynth/RRulesParser',
    packages=[_package],
    package_dir={_package: _package},
    include_package_data=True,
    install_requires=required,
    test_suite='discover_tests',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
)
