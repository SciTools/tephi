# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""Tephigram transform and isopleth constants."""

# The specific heat capacity of dry air at a constant pressure,
# in units of J kg-1 K-1.
# TBC: This was originally set to 1.01e3
Cp = 1004.0

# Dimensionless ratio: Rd / Cp.
K = 0.286

# Conversion offset between degree Celsius and Kelvin.
KELVIN = 273.15

# The specific latent heat of vapourisation of water at 0 degC,
# in units of J kg-1.
L = 2.501e6

MA = 300.0

# The specific gas constant for dry air, in units of J kg-1 K-1.
Rd = 287.0

# The specific gas constant for water vapour, in units of J kg-1 K-1.
Rv = 461.0

# Dimensionless ratio: Rd / Rv.
E = 0.622

# Base surface pressure.
P_BASE = 1000.0

# TODO: add in hodograph and mode defaults
default = {
    "barbs_gutter": 0.1,
    "barbs_length": 7,
    "barbs_linewidth": 1.5,
    "barbs_zorder": 10,
    "isobar_line": dict(color="blue", linewidth=0.5, clip_on=True),
    "isobar_min_theta": 0,
    "isobar_max_theta": 250,
    "isobar_nbins": None,
    "isobar_text": dict(
        size=8, color="blue", clip_on=True, va="bottom", ha="right"
    ),
    "isobar_ticks": [
        1050,
        1000,
        950,
        900,
        850,
        800,
        700,
        600,
        500,
        400,
        300,
        250,
        200,
        150,
        100,
        70,
        50,
        40,
        30,
        20,
        10,
    ],
    "isopleth_picker": 3,
    "isopleth_zorder": 10,
    "mixing_ratio_line": dict(color="green", linewidth=0.5, clip_on=True),
    "mixing_ratio_text": dict(
        size=8, color="green", clip_on=True, va="bottom", ha="right"
    ),
    "mixing_ratio_min_pressure": 10,
    "mixing_ratio_max_pressure": P_BASE,
    "mixing_ratio_nbins": 10,
    "mixing_ratio_ticks": [
        0.001,
        0.002,
        0.005,
        0.01,
        0.02,
        0.03,
        0.05,
        0.1,
        0.15,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.8,
        1.0,
        1.5,
        2.0,
        2.5,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        12.0,
        14.0,
        16.0,
        18.0,
        20.0,
        24.0,
        28.0,
        32.0,
        36.0,
        40.0,
        44.0,
        48.0,
        52.0,
        56.0,
        60.0,
        68.0,
        80.0,
    ],
    "wet_adiabat_line": dict(color="orange", linewidth=0.5, clip_on=True),
    "wet_adiabat_min_temperature": -50,
    "wet_adiabat_max_pressure": P_BASE,
    "wet_adiabat_nbins": 10,
    "wet_adiabat_text": dict(
        size=8, color="orange", clip_on=True, va="top", ha="left"
    ),
    "wet_adiabat_ticks": range(1, 61),
}
