from __future__ import (absolute_import, division, print_function)

from collections import namedtuple
from collections.abc import Iterable
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as mpath
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from mpl_toolkits.axisartist import Subplot
from mpl_toolkits.axisartist.grid_helper_curvelinear \
    import GridHelperCurveLinear
import numpy as np

import tephi.artists as artists
# from tephi.constants import default
import tephi.isopleths as isopleths
import tephi.transforms as transforms

__version__ = "0.4.0.dev0"

# MODE is scope creep from the original PR, this should go in a seperate PR

# _MODE = namedtuple('Mode', 'name kwargs')
#
# _MODE_SPEC = [_MODE('default', dict(show=False)),
#               _MODE('temperature', dict(pointer=True)),
#               _MODE('potential temperature', dict(pointer=True)),
#               _MODE('relative humidity',
#                     dict(pointer=True, highlight=True, fmt='{humidity:.2f}%'))
#               ]
#
#
# def _motion_handler(event):
#     if event.inaxes and event.inaxes.name == 'tephigram':
#         print('motion ...')
#
#
# def _key_press_handler(event):
#     key = event.key
#     if key in ['m', 'M']:
#         if event.inaxes and event.inaxes.name == 'tephigram':
#             reverse = key == 'M'
#             event.inaxes.tephi['mode'].next(reverse=reverse)
#             event.inaxes.figure.canvas.draw()
#
#
# def _pick_handler(event):
#     axes = event.artist.get_axes()
#     profile = axes.tephi['profiles'].picker(event.artist)
#     profile.highlight()
#     plt.draw()
#
#
# class _MODE(object):
#     def __init__(self, axes, modes):
#         self.axes = axes
#         if not isinstance(modes, Iterable):
#             modes = [modes]
#         if len(modes) == 0:
#             msg = 'Define at least one mode of operation.'
#             raise ValueError(msg)
#         self.modes = modes
#         self._index = 0
#         if all([self.has_highlight(index) for index in range(len(modes))]):
#             msg = 'Define at least one non-highlight mode of operation.'
#             raise ValueError(msg)
#         size = default.get('mode_size', 9)
#         prop = dict(size=size, weight='normal', color='white')
#         loc = default.get('mode_loc', 3)
#         frameon = default.get('mode_frameon', False)
#         self._anchor = AnchoredText('', prop=prop, frameon=False, loc=loc)  # BLHC
#         text = self._anchor.txt.get_children()[0]
#         text.set_path_effects([mpath.withStroke(linewidth=3, foreground='black')])
#         self._anchor.patch.set_boxstyle('round, pad=0, rounding_size=0.2')
#         self._anchor.set_visible(False)
#         self.axes.add_artist(self._anchor)
#         self._cache = []
#
#     def __call__(self):
#         return self.modes[self._index].name
#
#     def _check(self, index, kwarg):
#         if index is None:
#             index = self._index
#         mode = self.modes[index]
#         kwargs = mode.kwargs if mode.kwargs is not None else {kwarg: False}
#         return kwargs.get(kwarg, False)
#
#     def _refresh(self, text=None):
#         title = self.modes[self._index].name.capitalize()
#         if text:
#             title = '{}: {}'.format(title, text)
#         self._anchor.txt.set_text(title)
#         self._anchor.set_visible(True)
#
#     def has_highlight(self, index=None):
#         return self._check(index, 'highlight')
#
#     def has_pointer(self, index=None):
#         return self._check(index, 'pointer')
#
#     def next(self, reverse=False):
#         profiles = self.axes.tephi['profiles']
#         highlighted = profiles.highlighted()
#         if self.has_highlight() or len(highlighted):
#             self._cache = highlighted
#
#         # Cycle to the next mode.
#         mcount = len(self.modes)
#         self._index += -1 if reverse else 1
#         if self._index == mcount:
#             self._index = 0
#         elif self._index < 0:
#             self._index = mcount - 1
#
#         mode = self.modes[self._index]
#         kwargs = mode.kwargs if mode.kwargs is not None else dict(show=True)
#         show = kwargs.get('show', True)
#         self._anchor.set_visible(show)
#
#         # Show the mode anchor text.
#         if show:
#             self._refresh()
#
#         state = False
#         if self.has_highlight():
#             if len(profiles) == 2:
#                 state = True
#             elif len(profiles.highlighted()) == 0 and len(self._cache):
#                 state = None
#                 for profile in self._cache:
#                     profile.highlight(True)
#
#         if state is not None:
#             for profile in profiles:
#                 profile.highlight(state)
#
#         return mode.name
#
#     def update(self, **kwargs):
#         text = None
#         if kwargs:
#             if 'msg' in kwargs:
#                 text = kwargs['msg']
#             else:
#                 mode = self.modes[self._index]
#                 mode_kwargs = mode.kwargs if mode.kwargs is not None else {}
#                 fmt = mode_kwargs.get('fmt')
#                 if fmt is not None and kwargs:
#                     text = fmt.format(**kwargs)
#         self._refresh(text)
#

class _FormatterTheta(object):
    """
    Dry adiabats potential temperature axis tick formatter.

    """

    def __call__(self, direction, factor, values):
        return [r'$\theta={}$'.format(value) for value in values]


class _FormatterIsotherm(object):
    """
    Isotherms temperature axis tick formatter.

    """

    def __call__(self, direction, factor, values):
        return [r'$T={}$'.format(value) for value in values]


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
            (array([-50, -40, -30, -20, -10,   0,  10,  20]), 8, 1)

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
        start = (int(start) / step) * step
        stop = (int(stop) / step) * step
        ticks = np.arange(start, stop + step, step)
        return ticks, len(ticks), 1


class TephiAxes(Subplot):
    name = u'tephigram'

    def __init__(self, *args, **kwargs):
        # Validate the subplot arguments.
        if len(args) == 0:
            args = (1, 1, 1)
        elif len(args) == 1 and isinstance(args[0], int):
            args = tuple([int(c) for c in str(args[0])])
            if len(args) != 3:
                msg = 'Integer subplot specification must be a ' \
                      'three digit number. Not {}.'.format(len(args))
                raise ValueError(msg)
        else:
            msg = 'Invalid arguments: ' + ', '.join(['{}' for _ in len(args)])
            raise ValueError(msg.format(*args))

        # Process the kwargs.
        figure = kwargs.get('figure')
        isotherm_locator = kwargs.get('isotherm_locator')
        dry_adiabat_locator = kwargs.get('dry_adiabat_locator')
        anchor = None
        if 'anchor' in kwargs:
            anchor = kwargs.pop('anchor')

        # Get the figure.
        if figure is None:
            figure = plt.gcf()

        # Configure the locators.
        locator_isotherm = isotherm_locator
        if locator_isotherm and not isinstance(locator_isotherm, Locator):
            if not isinstance(locator_isotherm, int):
                raise ValueError('Invalid isotherm locator.')
            locator_isotherm = Locator(locator_isotherm)
        locator_theta = dry_adiabat_locator
        if locator_theta and not isinstance(locator_theta, Locator):
            if not isinstance(locator_theta, int):
                raise ValueError('Invalid dry adiabat locator.')

        from mpl_toolkits.axisartist.grid_finder import MaxNLocator
        locator_isotherm = MaxNLocator(nbins=20, steps=[10], integer=True)
        locator_theta = MaxNLocator(nbins=20, steps=[10], integer=True)

        gridder = GridHelperCurveLinear(transforms.TephiTransform(),
                                        tick_formatter1=_FormatterIsotherm(),
                                        grid_locator1=locator_isotherm,
                                        tick_formatter2=_FormatterTheta(),
                                        grid_locator2=locator_theta)
        super(TephiAxes, self).__init__(figure, *args, grid_helper=gridder, **kwargs)

        # The tephigram cache.
        transform = transforms.TephiTransform() + self.transData
        self.tephi = dict(anchor=anchor,
                          figure=figure.add_subplot(self),
                          mode=_MODE(self, _MODE_SPEC),
                          profiles=isopleths.ProfileList(),
                          transform=transform)

        # Create each axis.
        self.axis['isotherm'] = self.new_floating_axis(1, 0)
        self.axis['theta'] = self.new_floating_axis(0, 0)
        self.axis['left'].get_helper().nth_coord_ticks = 0
        self.axis['left'].toggle(all=True)
        self.axis['bottom'].get_helper().nth_coord_ticks = 1
        self.axis['bottom'].toggle(all=True)
        self.axis['top'].get_helper().nth_coord_ticks = 0
        self.axis['top'].toggle(all=False)  # Turned-off
        self.axis['right'].get_helper().nth_coord_ticks = 1
        self.axis['right'].toggle(all=True)
        self.gridlines.set_linestyle('solid')

        # Configure each axis.
        axis = self.axis['left']
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va('baseline')
        axis.major_ticklabels.set_rotation(135)
        axis = self.axis['right']
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_va('baseline')
        axis.major_ticklabels.set_rotation(-135)
        self.axis['top'].major_ticklabels.set_fontsize(10)
        axis = self.axis['bottom']
        axis.major_ticklabels.set_fontsize(10)
        axis.major_ticklabels.set_ha('left')
        axis.major_ticklabels.set_va('bottom')
        axis.major_ticklabels.set_rotation(-45)

        # Isotherms: lines of constant temperature (degC).
        axis = self.axis['isotherm']
        axis.set_axis_direction('right')
        axis.set_axislabel_direction('-')
        axis.major_ticklabels.set_rotation(90)
        axis.major_ticklabels.set_fontsize(8)
        axis.major_ticklabels.set_va('bottom')
        axis.major_ticklabels.set_color('grey')
        axis.major_ticklabels.set_visible(False)  # Turned-off
        axis.major_ticklabels.set_clip_box(self.bbox)

        # Dry adiabats: lines of constant potential temperature (degC).
        axis = self.axis['theta']
        axis.set_axis_direction('right')
        axis.set_axislabel_direction('+')
        axis.major_ticklabels.set_fontsize(8)
        axis.major_ticklabels.set_va('bottom')
        axis.major_ticklabels.set_color('grey')
        axis.major_ticklabels.set_visible(False)  # Turned-off
        axis.major_ticklabels.set_clip_box(self.bbox)
        axis.line.set_linewidth(3)
        axis.line.set_linestyle('--')

        # Lock down the aspect ratio.
        self.set_aspect('equal')
        self.grid(True)

        # Initialise the text formatter for the navigation status bar.
        self.format_coord = self._status_bar

        # Center the plot around the anchor extent.
        if anchor is not None:
            anchor = np.asarray(anchor)
            if anchor.shape != (2, 2):
                msg = 'Invalid anchor, expecting [(BLHC-T, BLHC-t),' \
                      '(TRHC-T, TRHC-t)]'
                raise ValueError(msg)
            xlim, ylim = transforms.convert_Tt2xy(anchor[:, 0], anchor[:, 1])
            self.set_xlim(xlim)
            self.set_ylim(ylim)
            self.tephi['anchor'] = xlim, ylim

        # Initialise the tephigram plot event handlers.
        #        plt.connect('motion_notify_event', _motion_handler)
        plt.connect('pick_event', _pick_handler)
        plt.connect('key_press_event', _key_press_handler)

        # Initialiase the hodograph.
        self.hodograph = isopleths.Hodograph(self)

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
        self.tephi['profiles'].append(profile)

        # Center the tephigram plot around all the profiles.
        if self.tephi['anchor'] is None:
            xlim, ylim = self._calculate_extents(xfactor=.25, yfactor=.05)
            self.set_xlim(xlim)
            self.set_ylim(ylim)

        # Show the plot legend.
        if 'label' in kwargs:
            font_properties = FontProperties(size='x-small')
            plt.legend(loc='upper right', fancybox=True, shadow=True,
                       prop=font_properties)

        return profile

    def add_isobars(self, ticks=None, line=None, text=None, min_theta=None,
                    max_theta=None, nbins=None):
        artist = artists.IsobarArtist(ticks=ticks, line=line, text=text,
                                      min_theta=min_theta, max_theta=max_theta,
                                      nbins=nbins)
        self.add_artist(artist)

    def add_wet_adiabats(self, ticks=None, line=None, text=None,
                         min_temperature=None, max_pressure=None, nbins=None):
        artist = artists.WetAdiabatArtist(ticks=ticks, line=line, text=text,
                                          min_temperature=min_temperature,
                                          max_pressure=max_pressure,
                                          nbins=nbins)
        self.add_artist(artist)

    def add_humidity_mixing_ratios(self, ticks=None, line=None, text=None,
                                   min_pressure=None, max_pressure=None,
                                   nbins=None):
        artist = artists.HumidityMixingRatioArtist(ticks=ticks, line=line,
                                                   text=text,
                                                   min_pressure=min_pressure,
                                                   max_pressure=max_pressure,
                                                   nbins=nbins)
        self.add_artist(artist)

    def _status_bar(self, x_point, y_point):
        """
        Generate text for the interactive backend navigation status bar.

        """
        temperature, theta = transforms.convert_xy2Tt(x_point, y_point)
        pressure, _ = transforms.convert_Tt2pT(temperature, theta)
        text = u'T={:.2f}\u00b0C, \u03b8={:.2f}\u00b0C, p={:.2f}hPa'
        return text.format(float(temperature), float(theta), float(pressure))

    def _calculate_extents(self, xfactor=None, yfactor=None):
        min_x = min_y = np.inf
        max_x = max_y = -np.inf

        if self.tephi['anchor'] is not None:
            xlim, ylim = self.tephi['anchor']
        else:
            for profile in self.tephi['profiles']:
                temperature = profile.points.temperature
                theta = profile.points.theta
                x_points, y_points = transforms.convert_Tt2xy(temperature,
                                                              theta)
                min_x, min_y = (np.min([min_x, np.min(x_points)]),
                                np.min([min_y, np.min(y_points)]))
                max_x, max_y = (np.max([max_x, np.max(x_points)]),
                                np.max([max_y, np.max(y_points)]))

            if xfactor is not None:
                delta_x = max_x - min_x
                min_x, max_x = ((min_x - xfactor * delta_x),
                                (max_x + xfactor * delta_x))

            if yfactor is not None:
                delta_y = max_y - min_y
                min_y, max_y = ((min_y - yfactor * delta_y),
                                (max_y + yfactor * delta_y))

            xlim, ylim = (min_x, max_x), (min_y, max_y)

        return xlim, ylim