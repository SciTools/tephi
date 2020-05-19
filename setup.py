from __future__ import absolute_import, division, print_function

import os
from setuptools import find_packages, setup


NAME = 'tephi'
DIR = os.path.abspath(os.path.dirname(__file__))
BASE = os.path.join(DIR, 'lib')


def extract_version():
    version = None
    fname = os.path.join(BASE, NAME, '__init__.py')
    with open(fname, 'r') as fi:
        for line in fi:
            if (line.startswith('__version__')):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters
                break
    return version


def long_description():
    with open(os.path.join(DIR, 'README.rst'), 'r') as fi:
        long_description = ''.join(fi.readlines())
    return long_description


args = dict(
    name=NAME,
    version=extract_version(),
    author='UK Met Office',
    packages=find_packages(where=BASE),
    package_dir={'': 'lib'},
    package_data={'tephi': ['etc/test_data/*.txt',
                            'tests/results/*.npz',
                            'tests/results/*.json']},
    classifiers=['License :: OSI Approved :: '
                 'GNU Lesser General Public License v3 or later (LGPLv3+)',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8'],
    description='Tephigram plotting in Python',
    long_description=long_description(),
    long_description_content_type='text/x-rst',
    test_suite='{}.tests'.format(NAME),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)


if __name__ == '__main__':
    setup(**args)
