from setuptools import setup, find_packages

with open("README.md") as f:
    long_desc = f.read()

setup(
    name="pdftextract",
    version="0.0.5",
    description="a very fast and efficient text and image pdf extractor.",
    include_package_data=True,
    packages=['pdftextract'],
    package_data={
        "xpdf":["*.exe"],
        "xpdf-linux": ["*.*"]
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords=["pdf", "text extractor", "pdf text extractor", 
            "pdf images extractor", "pdf parser", "pdf text"],
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/Bnilss/pdftextract",
    author="Iliass Benali",
    author_email="iliassben97@gmail.com"
)
