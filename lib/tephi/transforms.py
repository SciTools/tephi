# (C) British Crown Copyright 2014, Met Office
#
# This file is part of tephi.
#
# Tephi is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tephi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with tephi.  If not, see <http://www.gnu.org/licenses/>.
"""
Tephigram transform support.

"""

import matplotlib as mpl
from matplotlib.transforms import Transform
import numpy as np
import types

from _constants import CONST_K, CONST_KELVIN, CONST_L, CONST_MA, CONST_RV


#
# Reference: http://www-nwp/~hadaa/tephigram/tephi_plot.html
#


def temperature_theta_to_pressure_temperature(temperature, theta):
    """
    Transform temperature and potential temperature into
    pressure and temperature.

    Args:

    * temperature:
        Temperature in degC.

    * theta:
        Potential temperature in degC.

    Returns:
        Tuple of pressure, in mb or hPa, and temperature, in degC.

    """
    temperature, theta = np.asarray(temperature), np.asarray(theta)

    # Convert temperature and theta from degC to kelvin.
    kelvin = temperature + CONST_KELVIN
    theta = theta + CONST_KELVIN

    # Calculate the associated pressure given the temperature and
    # potential temperature.
    pressure = 1000.0 * np.power(kelvin / theta, 1 / CONST_K)

    return pressure, temperature


def pressure_temperature_to_temperature_theta(pressure, temperature):
    """
    Transform pressure and temperature into temperature and
    potential temperature.

    Args:

    * pressure:
        Pressure in mb or hPa.

    * temperature:
        Temperature in degC.

    Returns:
        Tuple of temperature, in degC, and potential temperature, in degC.

    """
    pressure, temperature = np.asarray(pressure), np.asarray(temperature)

    # Convert temperature from degC to kelvin.
    kelvin = temperature + CONST_KELVIN

    # Calculate the potential temperature given the pressure and temperature.
    theta = kelvin * ((1000.0 / pressure) ** CONST_K)

    # Convert potential temperature from kelvin to degC.
    return temperature, theta - CONST_KELVIN


def pressure_theta_to_pressure_temperature(pressure, theta):
    """
    Transform pressure and potential temperature into pressure and temperature.

    Args:

    * pressure:
        Pressure in mb or hPa.

    * theta:
        Potential temperature in degC.

    * Returns:
        Tuple of pressure, in mb or hPa, and temperature, in degC.

    """
    pressure, theta = np.asarray(pressure), np.asarray(theta)

    # Convert potential temperature from degC to kelvin.
    theta = theta + CONST_KELVIN

    # Calculate the temperature given the pressure and
    # potential temperature.
    kelvin = theta * (pressure ** CONST_K) / (1000.0 ** CONST_K)

    # Convert temperature from kelvin to degC.
    return pressure, kelvin - CONST_KELVIN


def temperature_theta_to_xy(temperature, theta):
    """
    Transform temperature and potential temperature to native display
    coordinates.

    Args:

    * temperature:
        Temperature in degC.

    * theta:
        Potential temperature in degC.

    Returns:
        Native display x and y coordinates.

    """
    temperature, theta = np.asarray(temperature), np.asarray(theta)

    # Convert potential temperature from degC to kelvin.
    theta = theta + CONST_KELVIN
    theta = np.clip(theta, 1, 1e10)

    phi = np.log(theta)

    x_data = phi * CONST_MA + temperature
    y_data = phi * CONST_MA - temperature

    return x_data, y_data


def xy_to_temperature_theta(x_data, y_data):
    """
    Transform native display coordinates to temperature and
    potential temperature.

    Args:

    * x_data:
        Native display x-coordinate/s.

    * y_data:
        Native display y-coordinate/s.

    Returns:
        Temperature, in degC, and potential temperature, in degC.

    """
    x_data, y_data = np.asarray(x_data), np.asarray(y_data)

    phi = (x_data + y_data) / (2 * CONST_MA)
    temperature = (x_data - y_data) / 2.

    theta = np.exp(phi) - CONST_KELVIN

    return temperature, theta


def pressure_mixing_ratio_to_temperature(pressure, mixing_ratio):
    """
    Transform pressure and mixing ratios to temperature.

    Args:

    * pressure:
        Pressure in mb in hPa.

    * mixing_ratio:
        Dimensionless mixing ratios.

    Returns:
        Temperature in degC.

    """
    pressure = np.array(pressure)

    # Calculate the dew-point.
    vapp = pressure * (8.0 / 5.0) * (mixing_ratio / 1000.0)
    temp = 1.0 / ((1.0 / CONST_KELVIN) - ((CONST_RV / CONST_L) * np.log(vapp / 6.11)))

    return temp - CONST_KELVIN


class TephiTransform(Transform):
    """
    Tephigram transformation to convert from temperature and
    potential temperature to native plotting device coordinates.

    """
    input_dims = 2
    output_dims = 2
    is_separable = False
    has_inverse = True

    def transform_non_affine(self, values):
        """
        Transform from tephigram temperature and potential temperature
        to native plotting device coordinates.

        Args:

        * values:
            Values to be transformed, with shape (N, 2).

        """
        return np.concatenate(temperature_theta_to_xy(values[:, 0:1], values[:, 1:2]), axis=1)

    def inverted(self):
        """Return the inverse transformation."""
        return TephiTransformInverted()


class TephiTransformInverted(Transform):
    """
    Tephigram inverse transformation to convert from native
    plotting device coordinates to tephigram temperature and
    potential temperature.

    """
    input_dims = 2
    output_dims = 2
    is_separable = False
    has_inverse = True

    def transform_non_affine(self, values):
        """
        Transform from native plotting display coordinates to tephigram
        temperature and potential temperature.

        Args:

        * values:
           Values to be transformed, with shape (N, 2).

        """
        return np.concatenate(xy_to_temperature_theta(values[:, 0:1], values[:, 1:2]), axis=1)

    def inverted(self):
        """Return the inverse transformation."""
        return TephiTransform()
