# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""
The tephi module provides tephigram plotting of pressure, temperature and wind
barb data.

.. warning::
    This is a beta release module and is liable to change.

"""
from collections import namedtuple
from collections.abc import Iterable

from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist import Subplot
from mpl_toolkits.axisartist.grid_helper_curvelinear import (
    GridHelperCurveLinear,
)
from mpl_toolkits.axisartist.grid_finder import MaxNLocator
import numpy as np
import os.path
import math
from . import artists, isopleths, transforms

__version__ = "0.4.0.post0"

from .artists import WetAdiabatArtist, IsobarArtist, HumidityMixingRatioArtist

RESOURCES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "etc")
DATA_DIR = os.path.join(RESOURCES_DIR, "test_data")

# TODO: Decide on whether to keep this, or come up with an alternate
#  method of loading files
def loadtxt(*filenames, **kwargs):
    """
    Load one or more text files of pressure, temperature, wind speed and wind
    direction value sets.

    Each line should contain, at minimum, a single pressure value (mb or hPa),
    and a single temperature value (degC), but may also contain a dewpoint
    value (degC), wind speed (knots) and wind direction value (degrees from
    north).

    Parameters
    ----------
    filenames : iterable of str
        One or more filenames.

    Other Parameters
    ----------------

    column_titles : list of iterables, optional
        List of iterables, or None. If specified, should contain one title
        string for each column of data per specified file. If all of multiple
        files loaded have the same column titles, then only one tuple of column
        titles need be specified.
    delimiter : str, optional
        The string used to separate values. This is passed directly to
        :func:`np.loadtxt`, which defaults to using any whitespace as delimiter
        if this keyword is not specified.
    dtype : type, optional
        The datatype to cast the data in the text file to. Passed directly to
        :func:`np.loadtxt`.

    Returns
    -------
    data : collections.namedtuple
    Contains one tuple, named with the relevant column title if specified,
    for each column of data in the text file loaded. If more than one file
    is loaded, a sequence of namedtuples is returned.

    Notes
    -----
    Note that blank lines and comment lines beginning with a '#' are ignored.

    Examples
    --------
    >>> import os.path
    >>> import tephi
    >>> winds = os.path.join(tephi.DATA_DIR, 'barbs.txt')
    >>> columns = ('pressure', 'dewpoint', 'wind_speed', 'wind_direction')
    >>> data = tephi.loadtxt(winds, column_titles=columns)
    >>> pressure = data.pressure
    >>> dews = data.dewpoint
    >>> wind_speed = data.wind_speed
    >>> wind_direction = data.wind_direction

    See Also
    --------
    :func:`numpy.loadtxt`.

    """

    def _repr(nt):
        """An improved representation of namedtuples over the default."""

        typename = nt.__class__.__name__
        fields = nt._fields
        n_fields = len(fields)
        return_str = "{}(\n".format(typename)
        for i, t in enumerate(fields):
            gap = " " * 4
            if i == n_fields - 1:
                ender = ""
            else:
                ender = "\n"
            return_str += "{}{}={!r}{}".format(gap, t, getattr(nt, t), ender)
        return_str += ")"
        return return_str

    column_titles = kwargs.pop("column_titles", None)
    delimiter = kwargs.pop("delimiter", None)
    dtype = kwargs.pop("dtype", "f4")

    if column_titles is not None:
        fields = column_titles[0]
        if not isinstance(column_titles, str):
            if isinstance(fields, Iterable) and not isinstance(fields, str):
                # We've an iterable of iterables - multiple titles is True.
                multiple_titles = True
                if len(column_titles) > len(filenames):
                    msg = "Received {} files but {} sets of column titles."
                    raise ValueError(
                        msg.format(len(column_titles), len(filenames))
                    )
            elif isinstance(fields, str):
                # We've an iterable of title strings - use for namedtuple.
                tephidata = namedtuple("tephidata", column_titles)
                multiple_titles = False
            else:
                # Whatever we've got it isn't iterable, so raise TypeError.
                msg = "Expected title to be string, got {!r}."
                raise TypeError(msg.format(type(column_titles)))
        else:
            msg = "Expected column_titles to be iterable, got {!r}."
            raise TypeError(msg.format(type(column_titles)))

    else:
        tephidata = namedtuple("tephidata", ("pressure", "temperature"))
        multiple_titles = False

    data = []
    for ct, arg in enumerate(filenames):
        if isinstance(arg, str):
            if os.path.isfile(arg):
                if multiple_titles:
                    tephidata = namedtuple("tephidata", column_titles[ct])
                tephidata.__repr__ = _repr
                payload = np.loadtxt(arg, dtype=dtype, delimiter=delimiter, converters=float)
                item = tephidata(*payload.T)
                data.append(item)
            else:
                msg = "Item {} is either not a file or does not exist."
                raise OSError(msg.format(arg))

    if len(data) == 1:
        data = data[0]

    return data


class _FormatterTheta(object):
    """
    Dry adiabats potential temperature axis tick formatter.

    """

    def __call__(self, direction, factor, values):
        return [r"$\theta={:.1f}$".format(value) for value in values]


class _FormatterIsotherm(object):
    """
    Isotherms temperature axis tick formatter.

    """

    def __call__(self, direction, factor, values):
        return [r"$T={:.1f}$".format(value) for value in values]


class Locator(object):
    """
    Determine the fixed step axis tick locations when called with a tick range.

    """

    def __init__(self, step):
        """
        Set the fixed step value for the axis tick locations.

        Generate tick location specification when called with a tick range.

        For example:

            >>> from tephi import Locator
            >>> locator = Locator(10)
            >>> locator(-45, 23)
            (array([-50, -40, -30, -20, -10,   0,  10, 20, 30]), 9, 1)

        Args:

        * step:
            The step value for each axis tick.

        """
        self.step = int(step)

    def __call__(self, start, stop):
        """
        Calculate the axis ticks given the provided tick range.

        """
        step = self.step
        start = math.floor(int(start) / step) * step
        stop = math.ceil(int(stop) / step) * step
        ticks = np.arange(start, stop + step, step)
        return ticks, len(ticks), 1


class TephiAxes(Subplot):
    name = "tephigram"

    def __init__(self, *args, **kwargs):
        # Validate the subplot arguments.

        # TODO: Remove limit of super() behaviour.
        #  Currently, it only accepts format of 123 or (1, 2, 3).
        if len(args) == 0:
            args = (1, 1, 1)
        elif (len(args) == 1
              and isinstance(args[0], tuple)
              and len(args[0]) == 3):
            args = args[0]
        elif len(args) == 1 and isinstance(args[0], int):
            args = tuple([int(c) for c in str(args[0])])
            if len(args) != 3:
                msg = (
                    "Integer subplot specification must be a "
                    "three digit number. Not {}.".format(len(args))
                )
                raise ValueError(msg)
        else:
            msg = "Invalid arguments: " + ", ".join(["{}" for _ in len(args)])
            raise ValueError(msg.format(*args))

        # Process the kwargs
        figure = kwargs.get("figure")
        if figure is None:
            figure = plt.gcf()

        # TODO: xylim should be split, to mirror the super()
        xylim = kwargs.pop("xylim", None)

        dry_adiabat_locator = kwargs.pop("dry_adiabat_locator", None)
        isotherm_locator = kwargs.pop("isotherm_locator", None)

        if isotherm_locator and not isinstance(isotherm_locator, Locator):
            if isinstance(isotherm_locator, int):
                locator_T = MaxNLocator(
                    nbins=isotherm_locator,
                    steps=[10],
                    integer=True
                )
            else:
                raise ValueError("Invalid isotherm locator.")
        else:
            locator_T = isotherm_locator

        if dry_adiabat_locator and not isinstance(dry_adiabat_locator, Locator):
            if isinstance(dry_adiabat_locator, int):
                locator_theta = MaxNLocator(
                    nbins=dry_adiabat_locator,
                    steps=[10],
                    integer=True
                )
            else:
                raise ValueError("Invalid dry adiabat locator.")
        else:
            locator_theta = dry_adiabat_locator

        gridder = GridHelperCurveLinear(
            transforms.TephiTransform(),
            tick_formatter1=_FormatterIsotherm(),
            grid_locator1=locator_T,
            tick_formatter2=_FormatterTheta(),
            grid_locator2=locator_theta,
        )
        super(TephiAxes, self).__init__(
            figure, *args, grid_helper=gridder, **kwargs
        )

        # The tephigram cache.
        transform = transforms.TephiTransform() + self.transData

        self.tephi = dict(
            xylim=xylim,
            figure=figure.add_subplot(self),
            profiles=isopleths.ProfileList(),
            transform=transform,
        )

        # Create each axis.
        self.axis["isotherm"] = self.new_floating_axis(1, 0)
        self.axis["theta"] = self.new_floating_axis(0, 0)
        self.axis["left"].get_helper().nth_coord_ticks = 0
        self.axis["left"].toggle(all=True)
        self.axis["bottom"].get_helper().nth_coord_ticks = 1
        self.axis["bottom"].toggle(all=True)
        self.axis["top"].get_helper().nth_coord_ticks = 0
        self.axis["top"].toggle(all=False)  # Turned-off
        self.axis["right"].get_helper().nth_coord_ticks = 1
        self.axis["right"].toggle(all=True)
        self.gridlines.set_linestyle("solid")

        # Configure each axis.
        axis = self.axis["left"]
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va("baseline")
        axis.major_ticklabels.set_rotation(135)
        axis = self.axis["right"]
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va("baseline")
        axis.major_ticklabels.set_rotation(-135)
        self.axis["top"].major_ticklabels.set_fontsize(10)
        axis = self.axis["bottom"]
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_ha("left")
        axis.major_ticklabels.set_va("bottom")
        axis.major_ticklabels.set_rotation(-45)

        # Isotherms: lines of constant temperature (degC).
        axis = self.axis["isotherm"]
        axis.set_axis_direction("right")
        axis.set_axislabel_direction("-")
        axis.major_ticklabels.set_rotation(90)
        axis.major_ticklabels.set_fontsize(8)
        axis.major_ticklabels.set_va("bottom")
        axis.major_ticklabels.set_color("grey")
        axis.major_ticklabels.set_visible(False)  # Turned-off
        axis.major_ticklabels.set_clip_box(self.bbox)

        # Dry adiabats: lines of constant potential temperature (degC).
        axis = self.axis["theta"]
        axis.set_axis_direction("right")
        axis.set_axislabel_direction("+")
        axis.major_ticklabels.set_fontsize(8)
        axis.major_ticklabels.set_va("bottom")
        axis.major_ticklabels.set_color("grey")
        axis.major_ticklabels.set_visible(False)  # Turned-off
        axis.major_ticklabels.set_clip_box(self.bbox)
        axis.line.set_linewidth(3)
        axis.line.set_linestyle("--")

        # Lock down the aspect ratio.
        self.set_aspect("equal")
        self.grid(True)

        # Initialise the text formatter for the navigation status bar.
        self.format_coord = self._status_bar

        # Center the plot around the xylim extent.
        if xylim is not None:
            xylim = np.asarray(xylim)
            if xylim.shape != (2, 2):
                msg = (
                    "Invalid xylim, expecting [(BLHC-T, BLHC-t),"
                    "(TRHC-T, TRHC-t)]"
                )
                raise ValueError(msg)
            xlim, ylim = transforms.convert_Tt2xy(xylim[:, 0], xylim[:, 1])
            self.set_xlim(xlim)
            self.set_ylim(ylim)
            self.tephi["xylim"] = xlim, ylim

    def _search_artists(self, artist):
        list_of_relevant_artists = [a for a in self.artists if type(a) == artist]
        if len(list_of_relevant_artists) == 1:
            return list_of_relevant_artists[0]
        elif len(list_of_relevant_artists) == 0:
            return None
        else:
            raise ValueError(f"Found more than one {artist} artist.")

    @property
    def wet_adiabat(self):
        return self._search_artists(WetAdiabatArtist)

    @wet_adiabat.setter
    def wet_adiabat(self, artist):
        if type(artist) is WetAdiabatArtist:
            old_artist = self._search_artists(WetAdiabatArtist)
            if old_artist:
                old_artist.remove()
            self.add_artist(artist)
        else:
            raise ValueError(f"Artist {artist} is not of type {WetAdiabatArtist}.")

    @property
    def isobar(self):
        return self._search_artists(IsobarArtist)

    @isobar.setter
    def isobar(self, artist):
        if type(artist) is IsobarArtist:
            old_artist = self._search_artists(IsobarArtist)
            if old_artist:
                old_artist.remove()
            self.add_artist(artist)
        else:
            raise ValueError(f"Artist {artist} is not of type {IsobarArtist}.")

    @property
    def mixing_ratio(self):
        return self._search_artists(HumidityMixingRatioArtist)

    @mixing_ratio.setter
    def mixing_ratio(self, artist):
        if type(artist) is HumidityMixingRatioArtist:
            old_artist = self._search_artists(HumidityMixingRatioArtist)
            if old_artist:
                old_artist.remove()
            self.add_artist(artist)
        else:
            raise ValueError(f"Artist {artist} is not of type {HumidityMixingRatioArtist}.")

    def plot(self, data, **kwargs):
        """
        Plot the profile of the pressure and temperature data points.

        The pressure and temperature data points are transformed into
        potential temperature and temperature data points before plotting.

        By default, the tephigram will automatically center the plot around
        all profiles.

        .. warning::
            Pressure data points must be in units of mb or hPa, and temperature
            data points must be in units of degC.

        Args:

        * data:
            Pressure and temperature pair data points.

        .. note::
            All keyword arguments are passed through to
            :func:`matplotlib.pyplot.plot`.

        .. plot::
            :include-source:

            import matplotlib.pyplot as plt
            from tephi import TephiAxes

            ax = TephiAxes()
            data = [[1006, 26.4], [924, 20.3], [900, 19.8],
                    [850, 14.5], [800, 12.9], [755, 8.3]]
            profile = ax.plot(data, color='red', linestyle='--',
                              linewidth=2, marker='o')
            barbs = [(10, 45, 900), (20, 60, 850), (25, 90, 800)]
            profile.barbs(barbs)
            plt.show()

        For associating wind barbs with the profile, see
        :meth:`~tephi.isopleths.Profile.barbs`.

        """
        profile = isopleths.Profile(self, data)
        profile.plot(**kwargs)
        self.tephi["profiles"].append(profile)

        # Center the tephigram plot around all the profiles.
        if self.tephi["xylim"] is None:
            xlim, ylim = self._calculate_extents(xfactor=0.25, yfactor=0.05)
            self.set_xlim(xlim)
            self.set_ylim(ylim)

        # Show the plot legend.
        if "label" in kwargs:
            font_properties = FontProperties(size="x-small")
            plt.legend(
                loc="upper right",
                fancybox=True,
                shadow=True,
                prop=font_properties,
            )

        return profile

    def add_isobars(
            self,
            ticks=None,
            line=None,
            text=None,
            min_theta=None,
            max_theta=None,
            nbins=None,
    ):
        self.isobar = artists.IsobarArtist(
            ticks=ticks,
            line=line,
            text=text,
            min_theta=min_theta,
            max_theta=max_theta,
            nbins=nbins,
        )

    def add_wet_adiabats(
            self,
            ticks=None,
            line=None,
            text=None,
            min_temperature=None,
            max_pressure=None,
            nbins=None,
    ):
        self.wet_adiabat = artists.WetAdiabatArtist(
            ticks=ticks,
            line=line,
            text=text,
            min_temperature=min_temperature,
            max_pressure=max_pressure,
            nbins=nbins,
        )

    def add_mixing_ratios(
            self,
            ticks=None,
            line=None,
            text=None,
            min_pressure=None,
            max_pressure=None,
            nbins=None,
    ):
        self.mixing_ratio = artists.HumidityMixingRatioArtist(
            ticks=ticks,
            line=line,
            text=text,
            min_pressure=min_pressure,
            max_pressure=max_pressure,
            nbins=nbins,
        )

    def _status_bar(self, x_point, y_point):
        """
        Generate text for the interactive backend navigation status bar.

        """
        temperature, theta = transforms.convert_xy2Tt(x_point, y_point)
        pressure, _ = transforms.convert_Tt2pT(temperature, theta)
        text = "T={:.2f}\u00b0C, \u03b8={:.2f}\u00b0C, p={:.2f}hPa"
        return text.format(float(temperature), float(theta), float(pressure))

    def _calculate_extents(self, xfactor=None, yfactor=None):
        min_x = min_y = np.inf
        max_x = max_y = -np.inf

        if self.tephi["xylim"] is not None:
            xlim, ylim = self.tephi["xylim"]
        else:
            for profile in self.tephi["profiles"]:
                temperature = profile.points.temperature
                theta = profile.points.theta
                x_points, y_points = transforms.convert_Tt2xy(
                    temperature, theta
                )
                min_x, min_y = (
                    np.min([min_x, np.min(x_points)]),
                    np.min([min_y, np.min(y_points)]),
                )
                max_x, max_y = (
                    np.max([max_x, np.max(x_points)]),
                    np.max([max_y, np.max(y_points)]),
                )

            if xfactor is not None:
                delta_x = max_x - min_x
                min_x, max_x = (
                    (min_x - xfactor * delta_x),
                    (max_x + xfactor * delta_x),
                )

            if yfactor is not None:
                delta_y = max_y - min_y
                min_y, max_y = (
                    (min_y - yfactor * delta_y),
                    (max_y + yfactor * delta_y),
                )

            xlim, ylim = (min_x, max_x), (min_y, max_y)

        return xlim, ylim
