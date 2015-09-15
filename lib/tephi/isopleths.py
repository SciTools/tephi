# (C) British Crown Copyright 2014 - 2015, Met Office
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
Tephigram isopleth support for generating and plotting tephigram lines,
environment profiles and barbs.

"""
from __future__ import absolute_import, division, print_function

import math
from matplotlib.collections import PathCollection
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.path import Path
import numpy as np
from scipy.interpolate import interp1d

from ._constants import CONST_CP, CONST_L, CONST_KELVIN, CONST_RD, CONST_RV
from . import transforms


# Wind barb speed (knots) ranges used since 1 January 1955.
_BARB_BINS = np.arange(20) * 5 + 3
_BARB_GUTTER = 0.1
_BARB_DTYPE = np.dtype(dict(names=('speed', 'angle', 'pressure', 'barb'),
                            formats=('f4', 'f4', 'f4', np.object)))

#
# Reference: http://www-nwp/~hadaa/tephigram/tephi_plot.html
#


def mixing_ratio(min_pressure, max_pressure, axes,
                 transform, kwargs, mixing_ratio_value):
    """
    Generate and plot a humidity mixing ratio line.

    A line of constant saturation mixing ratio with respect to a
    plane water surface (g kg-1).

    Args:

    * min_pressure:
        Minumum pressure, in mb or hPa, for the mixing ratio line extent.

    * max_pressure:
        Maximum pressure, in mb or hPa, for the mixing ratio line extent.

    * axes:
        Tephigram plotting :class:`matplotlib.axes.AxesSubplot` instance.

    * transform:
        Tephigram plotting transformation
        :class:`matplotlib.transforms.CompositeGenericTransform` instance.

    * kwargs:
        Keyword arguments for the mixing ratio :class:`matplotlib.lines.Line2D`
        instance.

    * mixing_ratio_value:
        The mixing ratio value to be plotted.

    Returns:
        The mixing ratio :class:`matplotlib.lines.Line2D` instance.

    """
    pressures = np.linspace(min_pressure, max_pressure, 100)
    temps = transforms.pressure_mixing_ratio_to_temperature(pressures,
                                                            mixing_ratio_value)
    _, thetas = transforms.pressure_temperature_to_temperature_theta(pressures,
                                                                     temps)
    line, = axes.plot(temps, thetas, transform=transform, **kwargs)

    return line


def isobar(min_theta, max_theta, axes, transform, kwargs, pressure):
    """
    Generate and plot an isobar line.

    A line of constant pressure (mb).

    Args:

    * min_theta:
        Minimum potential temperature, in degC, for the isobar extent.

    * max_theta:
        Maximum potential temperature, in degC, for the isobar extent.

    * axes:
        Tephigram plotting :class:`matplotlib.axes.AxesSubplot` instance.

    * transform:
        Tephigram plotting transformation :class:`matplotlib.transforms.CompositeGenericTransform`
        instance.

    * kwargs:
        Keyword arguments for the isobar :class:`matplotlib.lines.Line2D` instance.

    * pressure:
        The isobar pressure value, in mb or hPa, to be plotted.

    Returns:
       The isobar :class:`matplotlib.lines.Line2D` instance.

    """
    steps = 100
    thetas = np.linspace(min_theta, max_theta, steps)
    _, temps = transforms.pressure_theta_to_pressure_temperature([pressure] * steps, thetas)
    line, = axes.plot(temps, thetas, transform=transform, **kwargs)

    return line


def _wet_adiabat_gradient(min_temperature, pressure, temperature, dp):
    """
    Calculate the wet adiabat change in pressure and temperature.

    Args:

    * min_temperature:
        Minimum potential temperature, in degC, for the wet adiabat line extent.

    * pressure:
        Pressure point value, in mb or hPa, from which to calculate the gradient
        difference.

    * temperature:
        Potential temperature point value, in degC, from which to calculate
        the gradient difference.

    * dp:
        The wet adiabat change in pressure, in mb or hPa, from which to calculate
        the gradient difference.

    Returns:
        The gradient change as a pressure, potential temperature value pair.

    """

    # TODO: Discover the meaning of the magic numbers.

    kelvin = temperature + CONST_KELVIN
    lsbc = (CONST_L / CONST_RV) * ((1.0 / CONST_KELVIN) - (1.0 / kelvin))
    rw = 6.11 * np.exp(lsbc) * (0.622 / pressure)
    lrwbt = (CONST_L * rw) / (CONST_RD * kelvin)
    nume = ((CONST_RD * kelvin) / (CONST_CP * pressure)) * (1.0 + lrwbt)
    deno = 1.0 + (lrwbt * ((0.622 * CONST_L) / (CONST_CP * kelvin)))
    gradi = nume / deno
    dt = dp * gradi

    if (temperature + dt) < min_temperature:
        dt = min_temperature - temperature
        dp = dt / gradi

    return dp, dt


def wet_adiabat(max_pressure, min_temperature, axes,
                transform, kwargs, temperature):
    """
    Generate and plot a pseudo saturated wet adiabat line.

    A line of constant equivalent potential temperature for saturated
    air parcels (degC).

    Args:

    * max_pressure:
        Maximum pressure, in mb or hPa, for the wet adiabat line extent.

    * min_temperature:
        Minimum potential temperature, in degC, for the wet adiabat line extent.

    * axes:
        Tephigram plotting :class:`matplotlib.axes.AxesSubplot` instance.

    * transform:
        Tephigram plotting transformation
        :class:`matplotlib.transforms.CompositeGenericTransform` instance.

    * kwargs:
        Keyword arguments for the mixing ratio :class:`matplotlib.lines.Line2D`
        instance.

    * temperature:
        The wet adiabat value, in degC, to be plotted.

    Returns:
        The wet adiabat :class:`matplotlib.lines.Line2D` instance.

    """
    temps = [temperature]
    pressures = [max_pressure]
    dp = -5.0

    for i in range(200):
        dp, dt = _wet_adiabat_gradient(min_temperature, pressures[i],
                                       temps[i], dp)
        temps.append(temps[i] + dt)
        pressures.append(pressures[i] + dp)

    _, thetas = transforms.pressure_temperature_to_temperature_theta(pressures,
                                                                     temps)
    line, = axes.plot(temps, thetas, transform=transform, **kwargs)

    return line


class Barbs(object):
    """Generate a wind arrow barb."""

    def __init__(self, axes):
        """
        Create a wind arrow barb for the given axes.

        Args:

        * axes:
            A :class:`matplotlib.axes.AxesSubplot` instance.

        """
        self.axes = axes
        self.barbs = None
        self._gutter = None
        self._transform = axes.tephigram_transform + axes.transData
        self._kwargs = None
        self._custom_kwargs = None
        self._custom = dict(color=['barbcolor', 'color', 'edgecolor', 'facecolor'],
                            linewidth=['lw', 'linewidth'],
                            linestyle=['ls', 'linestyle'])

    @staticmethod
    def _uv(magnitude, angle):
        """
        Convert magnitude and angle measured in degrees to u and v components,
        where u is -x and v is -y.

        """
        angle = angle % 360
        u = v = 0
        # Snap the magnitude of the barb vector to fall into one of the
        # _BARB_BINS ensuring it's a multiple of five. Five is the increment
        # step size for decorating with barb with flags.
        magnitude = np.searchsorted(_BARB_BINS, magnitude, side='right') * 5
        modulus = angle % 90
        if modulus:
            quadrant = int(angle / 90)
            radians = math.radians(modulus)
            y = math.cos(radians) * magnitude
            x = math.sin(radians) * magnitude
            if quadrant == 0:
                u, v = -x, -y
            elif quadrant == 1:
                u, v = -y, x
            elif quadrant == 2:
                u, v = x, y
            else:
                u, v = y, -x
        else:
            angle = int(angle)
            if angle == 0:
                v = -magnitude
            elif angle == 90:
                u = -magnitude
            elif angle == 180:
                v = magnitude
            else:
                u = magnitude
        return u, v

    def _make_barb(self, temperature, theta, speed, angle):
        """Add the barb to the plot at the specified location."""
        u, v = self._uv(speed, angle)
        if 0 < speed < _BARB_BINS[0]:
            # Plot the missing barbless 1-2 knots line.
            length = self._kwargs['length']
            pivot_points = dict(tip=0.0, middle=-length / 2.)
            pivot = self._kwargs.get('pivot', 'tip')
            offset = pivot_points[pivot]
            verts = [(0.0, offset), (0.0, length + offset)]
            verts = mtransforms.Affine2D().rotate(math.radians(-angle)).transform(verts)
            codes = [Path.MOVETO, Path.LINETO]
            path = Path(verts, codes)
            size = length ** 2 / 4
            xy = np.array([[temperature, theta]])
            barb = PathCollection([path], (size,), offsets=xy,
                                  transOffset=self._transform, **self._custom_kwargs)
            barb.set_transform(mtransforms.IdentityTransform())
            self.axes.add_collection(barb)
        else:
            barb = plt.barbs(temperature, theta, u, v,
                             transform=self._transform, **self._kwargs)
        return barb

    def refresh(self):
        """Refresh the plot with the barbs."""
        if self.barbs is not None:
            xlim = self.axes.get_xlim()
            ylim = self.axes.get_ylim()
            y = np.linspace(*ylim)[::-1]
            xdelta = xlim[1] - xlim[0]
            x = np.ones(y.size) * (xlim[1] - (xdelta * self._gutter))
            points = self.axes.tephigram_inverse.transform(np.column_stack((x, y)))
            temperature, theta = points[:, 0], points[:, 1]
            pressure, _ = transforms.temperature_theta_to_pressure_temperature(temperature,
                                                                               theta)
            min_pressure, max_pressure = np.min(pressure), np.max(pressure)
            func = interp1d(pressure, temperature)
            for i, (speed, angle, pressure, barb) in enumerate(self.barbs):
                if min_pressure < pressure < max_pressure:
                    temperature, theta = transforms.pressure_temperature_to_temperature_theta(pressure,
                                                                                              func(pressure))
                    if barb is None:
                        self.barbs[i]['barb'] = self._make_barb(temperature, theta, speed, angle)
                    else:
                        barb.set_offsets(np.array([[temperature, theta]]))
                        barb.set_visible(True)
                else:
                    if barb is not None:
                        barb.set_visible(False)

    def plot(self, barbs, **kwargs):
        """
        Plot the sequence of barbs.

        Args:

        * barbs:
            Sequence of speed, direction and pressure value triples for
            each barb. Where speed is measured in units of knots, direction
            in units of degrees (clockwise from north), and pressure must
            be in units of mb or hPa.

        Kwargs:

        * gutter:
            Proportion offset from the right hand side axis to plot the
            barbs. Defaults to 0.1

            Also see :func:`matplotlib.pyplot.barbs`

        """
        self._gutter = kwargs.pop('gutter', _BARB_GUTTER)
        self._kwargs = dict(length=7, zorder=10)
        self._kwargs.update(kwargs)
        self._custom_kwargs = dict(color=None, linewidth=1.5,
                                   zorder=self._kwargs['zorder'])
        for key, values in self._custom.items():
            common = set(values).intersection(kwargs)
            if common:
                self._custom_kwargs[key] = kwargs[sorted(common)[0]]
        barbs = np.asarray(barbs)
        if barbs.ndim != 2 or barbs.shape[-1] != 3:
            msg = 'The barbs require to be a sequence of wind speed, ' \
              'wind direction and pressure value triples.'
            raise ValueError(msg)
        self.barbs = np.empty(barbs.shape[0], dtype=_BARB_DTYPE)
        for i, barb in enumerate(barbs):
            self.barbs[i] = tuple(barb) + (None,)
        self.refresh()


class Profile(object):
    """Generate an environmental lapse rate profile."""

    def __init__(self, data, axes):
        """
        Create an environmental lapse rate profile from the sequence of
        pressure and temperature point data.

        Args:

        * data:
            Sequence of pressure and temperature points defining the
            environmental lapse rate.

        * axes:
            The axes on which to plot the profile.

        """
        self.data = np.asarray(data)
        if self.data.ndim != 2 or self.data.shape[-1] != 2:
            msg = 'The environment profile data requires to be a sequence ' \
              'of pressure, temperature value pairs.'
            raise ValueError(msg)
        self.axes = axes
        self._transform = axes.tephigram_transform + axes.transData
        self.pressure = self.data[:, 0]
        self.temperature = self.data[:, 1]
        _, self.theta = transforms.pressure_temperature_to_temperature_theta(self.pressure,
                                                                             self.temperature)
        self.line = None
        self._barbs = Barbs(axes)

    def plot(self, **kwargs):
        """
        Plot the environmental lapse rate profile.

        Kwargs:

            See :func:`matplotlib.pyplot.plot`.

        Returns:
            The profile :class:`matplotlib.lines.Line2D`

        """
        if self.line is not None and line in self.axes.lines:
            self.axes.lines.remove(line)

        if 'zorder' not in kwargs:
            kwargs['zorder'] = 10

        self.line, = self.axes.plot(self.temperature, self.theta,
                                    transform=self._transform, **kwargs)
        return self.line

    def refresh(self):
        """Refresh the plot with the profile and any associated barbs."""
        self._barbs.refresh()

    def barbs(self, barbs, **kwargs):
        """
        Plot the sequence of barbs associated with this profile.

        Args:

        * barbs:
            Sequence of speed, direction and pressure value triples for
            each barb. Where speed is measured in units of knots, direction
            in units of degrees (clockwise from north), and pressure must
            be in units of mb or hPa.

        Kwargs:

            See :func:`matplotlib.pyplot.barbs`

        """
        colors = ['color', 'barbcolor', 'edgecolor', 'facecolor']
        if not set(colors).intersection(kwargs):
            kwargs['color'] = self.line.get_color()
        self._barbs.plot(barbs, **kwargs)
