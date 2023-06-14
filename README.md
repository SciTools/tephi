<p align="center">
<a href="https://tephi.readthedocs.io/en/latest/">
    <img src="https://scitools.github.io/tephi/tephi-logo-200-137.png" alt="Tephi">
</a>
</p>

<h3 align="center"><strong>Tephigram plotting in Python</strong></h3>

|         |                                                                                                                                                                                                                                                                                                                             |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI      | [![Documentation Status](https://readthedocs.org/projects/tephi/badge/?version=latest)](https://readthedocs.org/projects/tephi/) [![Pre-Commit CI Status](https://results.pre-commit.ci/badge/github/SciTools/tephi/main.svg)](https://results.pre-commit.ci/latest/github/SciTools/tephi/main)                             |
| Health  | [![Coverage Status](https://coveralls.io/repos/github/SciTools/tephi/badge.svg?branch=main)](https://coveralls.io/github/SciTools/tephi?branch=main)                                                                                                                                                                        |
| Meta    | [![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)                                                                                                                                                                                                            | 
| Package | [![Launch MyBinder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/SciTools/tephi/main?filepath=index.ipynb) [![conda-forge](https://img.shields.io/conda/vn/conda-forge/tephi)](https://anaconda.org/conda-forge/tephi)  [![PyPI](https://img.shields.io/pypi/v/tephi)](https://pypi.org/project/tephi/) |
| Repo    | [![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/scitools/tephi?color=orange)](https://github.com/SciTools/tephi/releases) [![GitHub commits since tagged version](https://img.shields.io/github/commits-since/scitools/tephi/latest/main)](https://github.com/SciTools/tephi/commits/main)              |
|         |                                                                                                                                                                                                                                                                                                                             |

# Welcome to Tephi!

## Installation

### conda

Tephi is available on [conda-forge](https://anaconda.org/conda-forge/tephi), and can be easily installed with [conda](https://docs.conda.io/projects/conda/en/latest/index.html):
```shell
conda install -c conda-forge tephi
```
or alternatively with [mamba](https://github.com/mamba-org/mamba):
```shell
mamba install -c conda-forge tephi
```
For more information see the [feedstock](https://github.com/conda-forge/tephi-feedstock).

### pip

Tephi is available on [PyPI](https://pypi.org/project/tephi/):

```shell
pip install tephi
```
Check out our [PyPI Download Stats!](https://pypistats.org/packages/tephi)

## Developers

If you simply can't wait for the next release to play with the latest hot features, then you can easily
install the `main` development branch from GitHub:
```shell
pip install git+https://github.com/SciTools/tephi@main
```

Alternatively, to configure a full developer environment, first clone the GeoVista GitHub repository:
```shell
git clone git@github.com:SciTools/tephi.git
```
Change to the root directory:
```shell
cd tephi
```
Create the `tephi-dev` conda development environment:
```shell
mamba env create --file requirements/dev.yml
```
Now activate the environment and install the `main` development branch of tephi:
```shell
conda activate tephi-dev
pip install --no-deps --editable .
```

...and you're all set up!

## Documentation

The [documentation](https://tephi.readthedocs.io/en/latest/) is built by [Sphinx](https://www.sphinx-doc.org/en/master/) and hosted on [Read the Docs](https://docs.readthedocs.io/en/stable/).


## Support

Need help? 😢

Why not check out our [existing GitHub issues](https://github.com/SciTools/tephi/issues). See something similar?
Well, give it a thumbs up to raise its priority, and feel free to chip in on the conversation. Otherwise, don't hesitate to
create a [new GitHub issue](https://github.com/SciTools/tephi/issues/new/choose) instead.

However, if you'd rather have a natter, then head on over to our
[GitHub Discussions](https://github.com/SciTools/tephi/discussions).

## License

Tephi is distributed under the terms of the [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html) license.

## [#ShowYourStripes](https://showyourstripes.info/s/globe)

<h4 align="center">
  <a href="https://showyourstripes.info/s/globe">
    <img src="https://raw.githubusercontent.com/ed-hawkins/show-your-stripes/master/2021/GLOBE---1850-2021-MO.png"
         height="50" width="800"
         alt="#showyourstripes Global 1850-2021"></a>
</h4>

**Graphics and Lead Scientist**: [Ed Hawkins](http://www.met.reading.ac.uk/~ed/home/index.php), National Centre for Atmospheric Science, University of Reading.

**Data**: Berkeley Earth, NOAA, UK Met Office, MeteoSwiss, DWD, SMHI, UoR, Meteo France & ZAMG.

<p>
<a href="https://showyourstripes.info/s/globe">#ShowYourStripes</a> is distributed under a
<a href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>
<a href="https://creativecommons.org/licenses/by/4.0/">
  <img src="https://i.creativecommons.org/l/by/4.0/80x15.png" alt="creative-commons-by" style="border-width:0"></a>
</p>

<br>
