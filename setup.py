from setuptools import setup


setup(
    name='tephi',
    version='0.2.0-alpha',
    url='https://github.com/SciTools/tephi',
    author='Bill Little',
    author_email='bill.james.little@gmail.com',
    packages=['tephi', 'tephi.tests'],
    package_dir={'': 'lib'},
    package_data={'tephi': ['etc/test_data/*.txt'] + ['etc/test_results/*.pkl']},
    classifiers=['License :: OSI Approved :: '
                 'GNU Lesser General Public License v3 (LGPLv3)',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',],
    description='Tephigram plotting in Python',
    long_description=open('README.rst').read(),
    test_suite='tephi.tests',
)
