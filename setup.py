# Copyright (C) 2020 Samuel Baker

DESCRIPTION = "Assign individuals from the UK Biobank to phenotypes based on ICD codes"
LONG_DESCRIPTION = """
# ICDBioAssign

Individuals in the UK Biobank have ICD 9 and 10 codes, which we may wish to use either individual or multiple at a time
to construct a phenotype. This code just produce these phenotypes for you from a few lines of code. 
"""
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"

DISTNAME = 'ICDBioAssign'
MAINTAINER = 'Samuel Baker'
MAINTAINER_EMAIL = 'samuelbaker.researcher@gmail.com'
LICENSE = 'MIT'
DOWNLOAD_URL = "https://github.com/sbaker-dev/ICDBioAssign"
VERSION = "0.01.0"
PYTHON_REQUIRES = ">=3.7"

INSTALL_REQUIRES = [
    'csvObject'
]

PACKAGES = [
    "ICDBioAssign",
]

CLASSIFIERS = [
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
]

if __name__ == "__main__":

    from setuptools import setup

    import sys

    if sys.version_info[:2] < (3, 7):
        raise RuntimeError("ICDBioAssign requires python >= 3.7.")

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        license=LICENSE,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        packages=PACKAGES,
        classifiers=CLASSIFIERS
    )
