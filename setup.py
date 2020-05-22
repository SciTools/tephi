# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.


import os
from setuptools import find_packages, setup


NAME = "tephi"
DIR = os.path.abspath(os.path.dirname(__file__))


def extract_version():
    version = None
    fname = os.path.join(DIR, NAME, "__init__.py")
    with open(fname, "r") as fi:
        for line in fi:
            if line.startswith("__version__"):
                _, version = line.split("=")
                version = version.strip()[1:-1]  # Remove quotation characters
                break
    return version


def load(fname):
    result = []
    with open(fname, "r") as fi:
        result = [package.strip() for package in fi.readlines()]
    return result


def long_description():
    with open(os.path.join(DIR, "README.md"), "r") as fi:
        long_description = "".join(fi.readlines())
    return long_description


args = dict(
    name=NAME,
    version=extract_version(),
    author="UK Met Office",
    url="https://github.com/SciTools/tephi",
    license="LGPLv3+",
    keywords=["tephigram", "radiosonde", "meteorology",],
    packages=find_packages(),
    package_data={
        "tephi": [
            "etc/test_data/*.txt",
            "tests/results/*.npz",
            "tests/results/*.json",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Tephigram plotting in Python",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    setup_requires=["setuptools>=40.8.0", "pytest-runner"],
    install_requires=load("requirements.txt"),
    tests_require=load("requirements-dev.txt"),
    test_suite=f"{NAME}.tests",
    python_requires=">=3.6",
)


if __name__ == "__main__":
    setup(**args)
