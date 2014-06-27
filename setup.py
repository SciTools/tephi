from setuptools import setup

setup(
    name='tephi',
    version='0.1.0',
    url='https://github.com/SciTools/tephi',
    author='Bill Little',
    author_email='bill.james.little@gmail.com',
    packages=['tephi', 'tephi.tests'],
    classifiers=['License :: OSI Approved :: '
                 'GNU Lesser General Public License v3 (LGPLv3)'],
    description='Tephigram plotting in Python',
    long_description=open('README.rst').read(),
    test_suite='tephi.tests',
    zip_safe=False
)
