# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
The tephi module provides tephigram plotting of pressure, temperature and wind
barb data.

.. warning::
    This is a beta release module and is liable to change.

"""
from collections import namedtuple
from collections.abc import Iterable
from functools import partial
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from mpl_toolkits.axisartist.grid_helper_curvelinear import (
    GridHelperCurveLinear,
)
from mpl_toolkits.axisartist import Subplot
import numbers
import numpy as np
import os.path

from . import isopleths
from . import transforms


__version__ = "0.2.2"


#
# Miscellaneous constants.
#
DEFAULT_WIDTH = 700  # in pixels

ISOBAR_SPEC = [(25, 0.03), (50, 0.10), (100, 0.25), (200, 1.5)]
ISOBAR_LINE = {"color": "blue", "linewidth": 0.5, "clip_on": True}
ISOBAR_TEXT = {
    "size": 8,
    "color": "blue",
    "clip_on": True,
    "va": "bottom",
    "ha": "right",
}
ISOBAR_FIXED = [50, 1000]

WET_ADIABAT_SPEC = [(1, 0.05), (2, 0.15), (4, 1.5)]
WET_ADIABAT_LINE = {"color": "orange", "linewidth": 0.5, "clip_on": True}
WET_ADIABAT_TEXT = {
    "size": 8,
    "color": "orange",
    "clip_on": True,
    "va": "bottom",
    "ha": "left",
}
WET_ADIABAT_FIXED = None

MIXING_RATIO_SPEC = [(1, 0.05), (2, 0.18), (4, 0.3), (8, 1.5)]
MIXING_RATIO_LINE = {"color": "green", "linewidth": 0.5, "clip_on": True}
MIXING_RATIO_TEXT = {
    "size": 8,
    "color": "green",
    "clip_on": True,
    "va": "bottom",
    "ha": "right",
}
MIXING_RATIOS = [
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
]
MIXING_RATIO_FIXED = None

MIN_PRESSURE = 50  # mb = hPa
MAX_PRESSURE = 1000  # mb = hPa
MIN_THETA = 0  # degC
MAX_THETA = 250  # degC
MIN_WET_ADIABAT = 1  # degC
MAX_WET_ADIABAT = 60  # degC
MIN_TEMPERATURE = -50  # degC


RESOURCES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "etc")
DATA_DIR = os.path.join(RESOURCES_DIR, "test_data")


def loadtxt(*filenames, **kwargs):
    """
    Load one or more text files of pressure, temperature, wind speed and wind
    direction value sets.

    Each line should contain, at minimum, a single pressure value (mb or hPa),
    and a single temperature value (degC), but may also contain a dewpoint
    value (degC), wind speed (knots) and wind direction value (degrees from
    north).

    Note that blank lines and comment lines beginning with a '#' are ignored.

    For example:

    >>> import os.path
    >>> import tephi

    >>> winds = os.path.join(tephi.DATA_DIR, 'barbs.txt')
    >>> columns = ('pressure', 'dewpoint', 'wind_speed', 'wind_direction')
    >>> data = tephi.loadtxt(winds, column_titles=columns)
    >>> pressure = data.pressure
    >>> dews = data.dewpoint
    >>> wind_speed = data.wind_speed
    >>> wind_direction = data.wind_direction

    .. seealso:: :func:`numpy.loadtxt`.

    Args:

    * filenames: one or more filenames.

    Kwargs:

    * column_titles:
        List of iterables, or None. If specified, should contain one title
        string for each column of data per specified file. If all of multiple
        files loaded have the same column titles, then only one tuple of column
        titles need be specified.

    * delimiter:
        The string used to separate values. This is passed directly to
        :func:`np.loadtxt`, which defaults to using any whitespace as delimiter
        if this keyword is not specified.

    * dtype:
        The datatype to cast the data in the text file to. Passed directly to
        :func:`np.loadtxt`.

    Returns:
        A :func:`collections.namedtuple` instance containing one tuple, named
        with the relevant column title if specified, for each column of data
        in the text file loaded. If more than one file is loaded, a sequence
        of namedtuples is returned.

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
                payload = np.loadtxt(arg, dtype=dtype, delimiter=delimiter)
                item = tephidata(*payload.T)
                data.append(item)
            else:
                msg = "Item {} is either not a file or does not exist."
                raise OSError(msg.format(arg))

    if len(data) == 1:
        data = data[0]

    return data


class _FormatterTheta:
    """Dry adiabats potential temperature axis tick formatter."""

    def __call__(self, direction, factor, values):
        return [r"$\theta={:.1f}$".format(value) for value in values]


class _FormatterIsotherm:
    """Isotherms temperature axis tick formatter."""

    def __call__(self, direction, factor, values):
        return [r"  $T={:.1f}$".format(value) for value in values]


class Locator:
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
            (array([-50, -40, -30, -20, -10,   0,  10,  20]), 8, 1)

        Args:

        * step: the step value for each axis tick.

        """
        self.step = int(step)

    def __call__(self, start, stop):
        """Calculate the axis ticks given the provided tick range."""

        step = self.step
        start = (int(start) / step) * step
        stop = (int(stop) / step) * step
        ticks = np.arange(start, stop + step, step)

        return ticks, len(ticks), 1


def _refresh_isopleths(axes):
    """
    Refresh the plot isobars, wet adiabats and mixing ratios and associated
    text labels.

    Args:

    * axes:
        Tephigram plotting :class:`matplotlib.axes.AxesSubplot` instance.

    Returns:
        Boolean, whether the plot has changed.

    """
    changed = False

    # Determine the current zoom level.
    xlim = axes.get_xlim()
    delta_xlim = xlim[1] - xlim[0]
    ylim = axes.get_ylim()
    zoom = delta_xlim / axes.tephigram_original_delta_xlim

    # Determine the display mid-point.
    x_point = xlim[0] + delta_xlim * 0.5
    y_point = ylim[0] + (ylim[1] - ylim[0]) * 0.5
    xy = np.array([[x_point, y_point]])
    xy_point = axes.tephigram_inverse.transform(xy)[0]

    for profile in axes.tephigram_profiles:
        profile.refresh()

    for isopleth in axes.tephigram_isopleths:
        changed = isopleth.refresh(zoom, xy_point) or changed

    return changed


def _handler(event):
    """Matplotlib event handler."""

    for axes in event.canvas.figure.axes:
        if hasattr(axes, "tephigram"):
            if _refresh_isopleths(axes):
                event.canvas.figure.show()


class _PlotGroup(dict):
    """
    Container for a related group of tephigram isopleths.

    Manages the creation and plotting of all isopleths within the group.

    """

    def __init__(
        self,
        axes,
        plot_func,
        text_kwargs,
        step,
        zoom,
        tags,
        fixed=None,
        xfocus=None,
    ):
        self.axes = axes
        self.text_kwargs = text_kwargs
        self.step = step
        self.zoom = zoom

        pairs = []
        for tag in tags:
            text = plt.text(0, 0, str(tag), **text_kwargs)
            text.set_bbox(
                dict(
                    boxstyle="Round,pad=0.3",
                    facecolor="white",
                    edgecolor="white",
                    alpha=0.5,
                    clip_on=True,
                    clip_box=self.axes.bbox,
                )
            )
            pairs.append((tag, [plot_func(tag), text]))

        dict.__init__(self, pairs)
        for line, text in self.values():
            line.set_visible(True)
            text.set_visible(True)
        self._visible = True

        if fixed is None:
            fixed = []

        if not isinstance(fixed, Iterable):
            fixed = [fixed]

        if zoom is None:
            self.fixed = set(tags)
        else:
            self.fixed = set(tags) & set(fixed)

        self.xfocus = xfocus

    def __setitem__(self, tag, item):
        emsg = "Cannot add or set an item into the plot group {!r}"
        raise ValueError(emsg.format(self.step))

    def __getitem__(self, tag):
        if tag not in self.keys():
            emsg = "Tag item {!r} is not a member of the plot group {!r}"
            raise KeyError(emsg.format(tag, self.step))
        return dict.__getitem__(self, tag)

    def refresh(self, zoom, xy_point):
        """
        Refresh all isopleths within the plot group.

        Args:

        * zoom:
            Zoom level of the current plot, relative to the initial plot.
        * xy_point:
            The center point of the current point, transformed into
            temperature and potential temperature.

        Returns:
            Boolean, whether the plot group has changed.

        """
        if self.zoom is None or zoom <= self.zoom:
            changed = self._item_on()
        else:
            changed = self._item_off()
        self._refresh_text(xy_point)
        return changed

    def _item_on(self, zoom=None):
        changed = False
        if zoom is None or self.zoom is None or zoom <= self.zoom:
            if not self._visible:
                for line, text in self.values():
                    line.set_visible(True)
                    text.set_visible(True)
                changed = True
                self._visible = True
        return changed

    def _item_off(self, zoom=None):
        changed = False
        if self.zoom is not None and (zoom is None or zoom > self.zoom):
            if self._visible:
                for tag, (line, text) in self.items():
                    if tag not in self.fixed:
                        line.set_visible(False)
                        text.set_visible(False)
                        changed = True
                        self._visible = False
        return changed

    def _generate_text(self, tag, xy_point):
        line, text = self[tag]
        x_data = line.get_xdata()
        y_data = line.get_ydata()

        if self.xfocus:
            delta = np.power(x_data - xy_point[0], 2)
        else:
            delta = np.power(x_data - xy_point[0], 2) + np.power(
                y_data - xy_point[1], 2
            )
        index = np.argmin(delta)
        text.set_position((x_data[index], y_data[index]))

    def _refresh_text(self, xy_point):
        if self._visible:
            for tag in self:
                self._generate_text(tag, xy_point)
        elif self.fixed:
            for tag in self.fixed:
                self._generate_text(tag, xy_point)


class _PlotCollection:
    """
    Container for tephigram isopleths.

    Manages the creation and plotting of all tephigram isobars, mixing ratio
    lines and pseudo saturated wet adiabats.

    """

    def __init__(
        self,
        axes,
        spec,
        stop,
        plot_func,
        text_kwargs,
        fixed=None,
        minimum=None,
        xfocus=None,
    ):
        if isinstance(stop, Iterable):
            if minimum and minimum > max(stop):
                emsg = "Minimum value of {!r} exceeds all other values"
                raise ValueError(emsg.format(minimum))

            items = [
                [step, zoom, set(stop[step - 1 :: step])]
                for step, zoom in sorted(spec, reverse=True)
            ]
        else:
            if minimum and minimum > stop:
                emsg = "Minimum value of {!r} exceeds maximum threshold {!r}"
                raise ValueError(emsg.format(minimum, stop))

            items = [
                [step, zoom, set(range(step, stop + step, step))]
                for step, zoom in sorted(spec, reverse=True)
            ]

        for index, item in enumerate(items):
            if minimum:
                item[2] = set([value for value in item[2] if value >= minimum])

            for subitem in items[index + 1 :]:
                subitem[2] -= item[2]

        self.groups = {
            item[0]: _PlotGroup(
                axes, plot_func, text_kwargs, *item, fixed=fixed, xfocus=xfocus
            )
            for item in items
            if item[2]
        }

        if not self.groups:
            emsg = "The plot collection failed to generate any plot groups"
            raise ValueError(emsg)

    def refresh(self, zoom, xy_point):
        """
        Refresh all isopleth groups within the plot collection.

        Args:

        * zoom:
            Zoom level of the current plot, relative to the initial plot.
        * xy_point:
            The center point of the current plot, transformed into
            temperature and potential temperature.

        Returns:
            Boolean, whether any plot group has changed.

        """
        changed = False

        for group in self.groups.values():
            changed = group.refresh(zoom, xy_point) or changed

        return changed


class Tephigram:
    """
    Generate a tephigram of one or more pressure and temperature data sets.

    """

    def __init__(
        self,
        figure=None,
        isotherm_locator=None,
        dry_adiabat_locator=None,
        anchor=None,
    ):
        """
        Initialise the tephigram transformation and plot axes.

        Kwargs:

        * figure:
            An existing :class:`matplotlib.figure.Figure` instance for the
            tephigram plot. If a figure is not provided, a new figure will
            be created by default.
        * isotherm_locator:
            A :class:`tephi.Locator` instance or a numeric step size
            for the isotherm lines.
        * dry_adiabat_locator:
            A :class:`tephi.Locator` instance or a numeric step size
            for the dry adiabat lines.
        * anchor:
            A sequence of two pressure, temperature pairs specifying the extent
            of the tephigram plot in terms of the bottom left hand corner and
            the top right hand corner. Pressure data points must be in units of
            mb or hPa, and temperature data points must be in units of degC.

        For example:

        .. plot::
            :include-source:

            import matplotlib.pyplot as plt
            from numpy import column_stack
            import os.path
            import tephi
            from tephi import Tephigram

            dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
            dry_bulb = os.path.join(tephi.DATA_DIR, 'temps.txt')
            dew_data, temp_data = tephi.loadtxt(dew_point, dry_bulb)
            dews = column_stack((dew_data.pressure, dew_data.temperature))
            temps = column_stack((temp_data.pressure, temp_data.temperature))
            tpg = Tephigram()
            tpg.plot(dews, label='Dew-point', color='blue', linewidth=2)
            tpg.plot(temps, label='Dry-bulb', color='red', linewidth=2)
            plt.show()

        """
        if not figure:
            # Create a default figure.
            self.figure = plt.figure(0, figsize=(9, 9))
        else:
            self.figure = figure

        # Configure the locators.
        if isotherm_locator and not isinstance(isotherm_locator, Locator):
            if not isinstance(isotherm_locator, numbers.Number):
                raise ValueError("Invalid isotherm locator")
            locator_isotherm = Locator(isotherm_locator)
        else:
            locator_isotherm = isotherm_locator

        if dry_adiabat_locator and not isinstance(
            dry_adiabat_locator, Locator
        ):
            if not isinstance(dry_adiabat_locator, numbers.Number):
                raise ValueError("Invalid dry adiabat locator")
            locator_theta = Locator(dry_adiabat_locator)
        else:
            locator_theta = dry_adiabat_locator

        # Define the tephigram coordinate-system transformation.
        self.tephi_transform = transforms.TephiTransform()
        ghelper = GridHelperCurveLinear(
            self.tephi_transform,
            tick_formatter1=_FormatterIsotherm(),
            grid_locator1=locator_isotherm,
            tick_formatter2=_FormatterTheta(),
            grid_locator2=locator_theta,
        )
        self.axes = Subplot(self.figure, 1, 1, 1, grid_helper=ghelper)
        self.transform = self.tephi_transform + self.axes.transData
        self.axes.axis["isotherm"] = self.axes.new_floating_axis(1, 0)
        self.axes.axis["theta"] = self.axes.new_floating_axis(0, 0)
        self.axes.axis["left"].get_helper().nth_coord_ticks = 0
        self.axes.axis["left"].toggle(all=True)
        self.axes.axis["bottom"].get_helper().nth_coord_ticks = 1
        self.axes.axis["bottom"].toggle(all=True)
        self.axes.axis["top"].get_helper().nth_coord_ticks = 0
        self.axes.axis["top"].toggle(all=False)
        self.axes.axis["right"].get_helper().nth_coord_ticks = 1
        self.axes.axis["right"].toggle(all=True)
        self.axes.gridlines.set_linestyle("solid")

        self.figure.add_subplot(self.axes)

        # Configure default axes.
        axis = self.axes.axis["left"]
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va("baseline")
        axis.major_ticklabels.set_rotation(135)
        axis = self.axes.axis["right"]
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va("baseline")
        axis.major_ticklabels.set_rotation(-135)
        self.axes.axis["top"].major_ticklabels.set_fontsize(10)
        axis = self.axes.axis["bottom"]
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_ha("left")
        axis.major_ticklabels.set_va("top")
        axis.major_ticklabels.set_rotation(-45)

        # Isotherms: lines of constant temperature (degC).
        axis = self.axes.axis["isotherm"]
        axis.set_axis_direction("right")
        axis.set_axislabel_direction("-")
        axis.major_ticklabels.set_rotation(90)
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va("bottom")
        axis.major_ticklabels.set_color("grey")
        axis.major_ticklabels.set_visible(False)  # turned-off

        # Dry adiabats: lines of constant potential temperature (degC).
        axis = self.axes.axis["theta"]
        axis.set_axis_direction("right")
        axis.set_axislabel_direction("+")
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va("bottom")
        axis.major_ticklabels.set_color("grey")
        axis.major_ticklabels.set_visible(False)  # turned-off
        axis.line.set_linewidth(3)
        axis.line.set_linestyle("--")

        # Lock down the aspect ratio.
        self.axes.set_aspect(1.0)
        self.axes.grid(True)

        # Initialise the text formatter for the navigation status bar.
        self.axes.format_coord = self._status_bar

        # Factor in the tephigram transform.
        ISOBAR_TEXT["transform"] = self.transform
        WET_ADIABAT_TEXT["transform"] = self.transform
        MIXING_RATIO_TEXT["transform"] = self.transform

        # Create plot collections for the tephigram isopleths.
        func = partial(
            isopleths.isobar,
            MIN_THETA,
            MAX_THETA,
            self.axes,
            self.transform,
            ISOBAR_LINE,
        )
        self._isobars = _PlotCollection(
            self.axes,
            ISOBAR_SPEC,
            MAX_PRESSURE,
            func,
            ISOBAR_TEXT,
            fixed=ISOBAR_FIXED,
            minimum=MIN_PRESSURE,
        )

        func = partial(
            isopleths.wet_adiabat,
            MAX_PRESSURE,
            MIN_TEMPERATURE,
            self.axes,
            self.transform,
            WET_ADIABAT_LINE,
        )
        self._wet_adiabats = _PlotCollection(
            self.axes,
            WET_ADIABAT_SPEC,
            MAX_WET_ADIABAT,
            func,
            WET_ADIABAT_TEXT,
            fixed=WET_ADIABAT_FIXED,
            minimum=MIN_WET_ADIABAT,
            xfocus=True,
        )

        func = partial(
            isopleths.mixing_ratio,
            MIN_PRESSURE,
            MAX_PRESSURE,
            self.axes,
            self.transform,
            MIXING_RATIO_LINE,
        )
        self._mixing_ratios = _PlotCollection(
            self.axes,
            MIXING_RATIO_SPEC,
            MIXING_RATIOS,
            func,
            MIXING_RATIO_TEXT,
            fixed=MIXING_RATIO_FIXED,
        )

        # Initialise for the tephigram plot event handler.
        plt.connect("motion_notify_event", _handler)
        self.axes.tephigram = True
        self.axes.tephigram_original_delta_xlim = DEFAULT_WIDTH
        self.original_delta_xlim = DEFAULT_WIDTH
        self.axes.tephigram_transform = self.tephi_transform
        self.axes.tephigram_inverse = self.tephi_transform.inverted()
        self.axes.tephigram_isopleths = [
            self._isobars,
            self._wet_adiabats,
            self._mixing_ratios,
        ]

        # The tephigram profiles.
        self._profiles = []
        self.axes.tephigram_profiles = self._profiles

        # Center the plot around the anchor extent.
        self._anchor = anchor
        if self._anchor is not None:
            self._anchor = np.asarray(anchor)
            if (
                self._anchor.ndim != 2
                or self._anchor.shape[-1] != 2
                or len(self._anchor) != 2
            ):
                msg = (
                    "Invalid anchor, expecting [(bottom-left-pressure, "
                    "bottom-left-temperature), (top-right-pressure, "
                    "top-right-temperature)]"
                )
                raise ValueError(msg)
            (
                (bottom_pressure, bottom_temp),
                (top_pressure, top_temp),
            ) = self._anchor

            if (bottom_pressure - top_pressure) < 0:
                raise ValueError("Invalid anchor pressure range")
            if (bottom_temp - top_temp) < 0:
                raise ValueError("Invalid anchor temperature range")

            self._anchor = isopleths.Profile(anchor, self.axes)
            self._anchor.plot(visible=False)
            xlim, ylim = self._calculate_extents()
            self.axes.set_xlim(xlim)
            self.axes.set_ylim(ylim)

    def plot(self, data, **kwargs):
        """
        Plot the environmental lapse rate profile of the pressure and
        temperature data points.

        The pressure and temperature data points are transformed into
        potential temperature and temperature data points before plotting.

        By default, the tephigram will automatically center the plot around
        all profiles.

        .. warning::
            Pressure data points must be in units of mb or hPa, and temperature
            data points must be in units of degC.

        Args:

        * data: pressure and temperature pair data points.

        .. note::
            All keyword arguments are passed through to
            :func:`matplotlib.pyplot.plot`.

        For example:

        .. plot::
            :include-source:

            import matplotlib.pyplot as plt
            from tephi import Tephigram

            tpg = Tephigram()
            data = [[1006, 26.4], [924, 20.3], [900, 19.8],
                    [850, 14.5], [800, 12.9], [755, 8.3]]
            profile = tpg.plot(data, color='red', linestyle='--',
                               linewidth=2, marker='o')
            barbs = [(10, 45, 900), (20, 60, 850), (25, 90, 800)]
            profile.barbs(barbs)
            plt.show()

        For associating wind barbs with an environmental lapse rate profile,
        see :meth:`~tephi.isopleths.Profile.barbs`.

        """
        profile = isopleths.Profile(data, self.axes)
        profile.plot(**kwargs)
        self._profiles.append(profile)

        # Center the tephigram plot around all the profiles.
        if self._anchor is None:
            xlim, ylim = self._calculate_extents(xfactor=0.25, yfactor=0.05)
            self.axes.set_xlim(xlim)
            self.axes.set_ylim(ylim)

        # Refresh the tephigram plot isopleths.
        _refresh_isopleths(self.axes)

        # Show the plot legend.
        if "label" in kwargs:
            font_properties = FontProperties(size="x-small")
            plt.legend(
                loc="upper left",
                fancybox=True,
                shadow=True,
                prop=font_properties,
            )

        return profile

    def _status_bar(self, x_point, y_point):
        """Generate text for the interactive backend navigation status bar."""

        temperature, theta = transforms.convert_xy2Tt(x_point, y_point)
        pressure, _ = transforms.convert_Tt2pT(temperature, theta)
        xlim = self.axes.get_xlim()
        zoom = (xlim[1] - xlim[0]) / self.original_delta_xlim
        msg = "T:{:.2f}, theta:{:.2f}, phi:{:.2f} (zoom:{:.3f})"
        text = msg.format(
            float(temperature), float(theta), float(pressure), zoom
        )

        return text

    def _calculate_extents(self, xfactor=None, yfactor=None):
        min_x = min_y = 1e10
        max_x = max_y = -1e-10
        profiles = self._profiles
        transform = self.tephi_transform.transform

        if self._anchor is not None:
            profiles = [self._anchor]

        for profile in profiles:
            temperature = profile.temperature.reshape(-1, 1)
            theta = profile.theta.reshape(-1, 1)
            xy_points = transform(np.concatenate((temperature, theta), axis=1))
            x_points = xy_points[:, 0]
            y_points = xy_points[:, 1]
            min_x = np.min([min_x, np.min(x_points)])
            min_y = np.min([min_y, np.min(y_points)])
            max_x = np.max([max_x, np.max(x_points)])
            max_y = np.max([max_y, np.max(y_points)])

        if xfactor is not None:
            delta_x = max_x - min_x
            min_x, max_x = min_x - xfactor * delta_x, max_x + xfactor * delta_x

        if yfactor is not None:
            delta_y = max_y - min_y
            min_y, max_y = min_y - yfactor * delta_y, max_y + yfactor * delta_y

        return ([min_x, max_x], [min_y, max_y])
