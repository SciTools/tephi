# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Tephigram transform support.

"""
from matplotlib.transforms import Transform
import numpy as np

from ._constants import CONST_K, CONST_KELVIN, CONST_L, CONST_MA, CONST_RV


#
# Reference: http://www-nwp/~hadaa/tephigram/tephi_plot.html
#


def convert_Tt2pT(temperature, theta):
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


def convert_pT2Tt(pressure, temperature):
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


def convert_pt2pT(pressure, theta):
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


def convert_Tt2xy(temperature, theta):
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


def convert_xy2Tt(x_data, y_data):
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
    temperature = (x_data - y_data) / 2.0

    theta = np.exp(phi) - CONST_KELVIN

    return temperature, theta


def convert_pw2T(pressure, mixing_ratio):
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
    temp = 1.0 / (
        (1.0 / CONST_KELVIN) - ((CONST_RV / CONST_L) * np.log(vapp / 6.11))
    )

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
        return np.concatenate(
            convert_Tt2xy(values[:, 0:1], values[:, 1:2]), axis=1
        )

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
        return np.concatenate(
            convert_xy2Tt(values[:, 0:1], values[:, 1:2]), axis=1
        )

    def inverted(self):
        """Return the inverse transformation."""
        return TephiTransform()
