import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="brs_utils",
    version="0.0.6",
    author="Joan Hérisson, Melchior du Lac",
    author_email="joan.herisson@univ-evry.fr",
    description="Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brsynth/brs-utils",
    packages=setuptools.find_packages(),
    install_requires=[
        'python-libsbml',
    ],
    test_suite = 'discover_tests',
    test_requires=[
        'python-libsbml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
