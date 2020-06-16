import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rplibs",
    version="0.0.2",
    author="Melchior du Lac, Joan Hérisson",
    author_email="joan.herisson@univ-evry.fr",
    description="SBML structure with RetroPath2 fields",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brsynth/rpUtils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
