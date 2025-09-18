# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""
Tephigram transform support.

"""

from matplotlib.transforms import Transform
import numpy as np

import tephi.constants as constants


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
    kelvin = temperature + constants.KELVIN
    theta = theta + constants.KELVIN

    # Calculate the associated pressure given the temperature and
    # potential temperature.
    pressure = constants.P_BASE * np.power(kelvin / theta, 1 / constants.K)

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
    kelvin = temperature + constants.KELVIN

    # Calculate the potential temperature given the pressure and temperature.
    theta = kelvin * ((constants.P_BASE / pressure) ** constants.K)

    # Convert potential temperature from kelvin to degC.
    return temperature, theta - constants.KELVIN


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
    theta = theta + constants.KELVIN

    # Calculate the temperature given the pressure and potential temperature.
    denom = constants.P_BASE**constants.K
    kelvin = theta * (pressure**constants.K) / denom

    # Convert temperature from kelvin to degC.
    return pressure, kelvin - constants.KELVIN


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
    theta = theta + constants.KELVIN
    theta = np.clip(theta, 1, 1e10)

    phi = np.log(theta)

    x_data = phi * constants.MA + temperature
    y_data = phi * constants.MA - temperature

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

    phi = (x_data + y_data) / (2 * constants.MA)
    temperature = (x_data - y_data) / 2.0

    theta = np.exp(phi) - constants.KELVIN

    return temperature, theta


def convert_pw2T(pressure, mixing_ratio):
    """
    Transform pressure and mixing ratios to temperature.

    Args:

    * pressure:
        Pressure in mb in hPa.

    * mixing_ratio:
        Mixing ratio in g kg-1.

    Returns:
        Temperature in degC.

    """
    pressure = np.asarray(pressure)

    # Calculate the dew-point.
    vapp = pressure * (8.0 / 5.0) * (mixing_ratio / constants.P_BASE)
    temp = 1.0 / (
        (1.0 / constants.KELVIN)
        - ((constants.Rv / constants.L) * np.log(vapp / 6.11))
    )

    return temp - constants.KELVIN


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
            convert_Tt2xy(values[:, 0:1], values[:, 1:2]), axis=-1
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
            convert_xy2Tt(values[:, 0:1], values[:, 1:2]), axis=-1
        )

    def inverted(self):
        """Return the inverse transformation."""
        return TephiTransform()
