import matplotlib.artist
import numpy as np
from scipy.interpolate import interp1d
from shapely.geometry import LineString, Polygon
from shapely.prepared import prep

from .constants import default
from .isopleths import Isobar, WetAdiabat, HumidityMixingRatio
from .transforms import convert_xy2Tt, convert_Tt2pT


class IsoplethArtist(matplotlib.artist.Artist):
    def __init__(self):
        super(IsoplethArtist, self).__init__()
        self._isopleths = None

    def _locator(self, x0, x1, y0, y1):
        temperature, theta = convert_xy2Tt([x0, x0, x1, x1], [y0, y1, y1, y0])
        bbox = prep(Polygon(zip(temperature, theta)))
        mask = [bbox.intersects(item.geometry) for item in self._isopleths]
        mask = np.asarray(mask)

        if self.nbins:
            indices = np.where(mask)[0]
            if indices.size:
                if self.nbins < indices.size:
                    mask[:] = False
                    upint = indices.size + self.nbins - 1
                    # this is an ugly solution, I'm sure there must be better ones
                    mask[indices[:: upint // self.nbins + 1]] = True

        return mask


class IsobarArtist(IsoplethArtist):
    def __init__(
        self,
        ticks=None,
        line=None,
        text=None,
        min_theta=None,
        max_theta=None,
        nbins=None,
    ):
        super(IsobarArtist, self).__init__()
        if ticks is None:
            ticks = default.get("isobar_ticks")
        self.ticks = ticks
        self._kwargs = {}
        if line is None:
            line = default.get("isobar_line")
        self._kwargs["line"] = line
        if text is None:
            text = default.get("isobar_text")
        self._kwargs["text"] = text
        if min_theta is None:
            min_theta = default.get("isobar_min_theta")
        self.min_theta = min_theta
        if max_theta is None:
            max_theta = default.get("isobar_max_theta")
        self.max_theta = max_theta
        if nbins is None:
            nbins = default.get("isobar_nbins")
        elif nbins < 2 or isinstance(nbins, str):
            nbins = None
        self.nbins = nbins

    @matplotlib.artist.allow_rasterization
    def draw(
        self, renderer, line=None, text=None, min_theta=None, max_theta=None
    ):
        if not self.get_visible():
            return
        axes = self.axes
        draw_kwargs = dict(self._kwargs["line"])
        if line is not None:
            draw_kwargs.update(line)
        text_kwargs = dict(self._kwargs["text"])
        if text is not None:
            text_kwargs.update(text)
        if min_theta is None:
            min_theta = self.min_theta
        if max_theta is None:
            max_theta = self.max_theta

        if self._isopleths is None:
            isobars = []
            for tick in self.ticks:
                isobars.append(Isobar(axes, tick, min_theta, max_theta))
            self._isopleths = np.asarray(isobars)

        (x0, x1), (y0, y1) = axes.get_xlim(), axes.get_ylim()
        mask = self._locator(x0, x1, y0, y1)

        mx = x0 + axes.viewLim.width * 0.5
        temperature, theta = convert_xy2Tt([mx, mx], [y0, y1])
        text_line = LineString(zip(temperature, theta))

        temperature, theta = convert_xy2Tt([mx] * 50, np.linspace(y0, y1, 50))
        pressure, _ = convert_Tt2pT(temperature, theta)
        func = interp1d(pressure, theta, bounds_error=False)

        for isobar in self._isopleths[mask]:
            isobar.draw(renderer, **draw_kwargs)
            point = text_line.intersection(isobar.geometry)
            if point:
                isobar.refresh(
                    point.x, point.y, renderer=renderer, **text_kwargs
                )
            else:
                if func(isobar.data) < isobar.extent.theta.lower:
                    T = isobar.points.temperature[isobar.index.theta.lower]
                    t = isobar.extent.theta.lower
                else:
                    T = isobar.points.temperature[isobar.index.theta.upper]
                    t = isobar.extent.theta.upper
                isobar.refresh(T, t, renderer=renderer, **text_kwargs)


class WetAdiabatArtist(IsoplethArtist):
    def __init__(
        self,
        ticks=None,
        line=None,
        text=None,
        min_temperature=None,
        max_pressure=None,
        nbins=None,
    ):
        super(WetAdiabatArtist, self).__init__()
        if ticks is None:
            ticks = default.get("wet_adiabat_ticks")
        self.ticks = sorted(ticks)
        self._kwargs = {}
        if line is None:
            line = default.get("wet_adiabat_line")
        self._kwargs["line"] = line
        if text is None:
            text = default.get("wet_adiabat_text")
        self._kwargs["text"] = text
        if min_temperature is None:
            min_temperature = default.get("wet_adiabat_min_temperature")
        self.min_temperature = min_temperature
        if max_pressure is None:
            max_pressure = default.get("wet_adiabat_max_pressure")
        self.max_pressure = max_pressure
        if nbins is None:
            nbins = default.get("wet_adiabat_nbins")
        if nbins is None or (nbins < 2 or isinstance(nbins, str)):
            nbins = None
        self.nbins = nbins

    @matplotlib.artist.allow_rasterization
    def draw(
        self,
        renderer,
        line=None,
        text=None,
        min_temperature=None,
        max_pressure=None,
    ):
        if not self.get_visible():
            return
        axes = self.axes
        draw_kwargs = dict(self._kwargs["line"])
        if line is not None:
            draw_kwargs.update(line)
        text_kwargs = dict(self._kwargs["text"])
        if text is not None:
            text_kwargs.update(text)
        if min_temperature is None:
            min_temperature = self.min_temperature
        if max_pressure is None:
            max_pressure = self.max_pressure

        if self._isopleths is None:
            adiabats = []
            for tick in self.ticks:
                adiabats.append(
                    WetAdiabat(axes, tick, min_temperature, max_pressure)
                )
            self._isopleths = np.asarray(adiabats)

        (x0, x1), (y0, y1) = axes.get_xlim(), axes.get_ylim()
        mask = self._locator(x0, x1, y0, y1)

        mx = x0 + axes.viewLim.width * 0.5
        my = y0 + axes.viewLim.height * 0.5
        temperature, theta = convert_xy2Tt([x0, mx, x1], [y0, my, y1])
        text_line = LineString(zip(temperature, theta))
        mT = temperature[1]
        snap = None

        for adiabat in self._isopleths[mask]:
            adiabat.draw(renderer, **draw_kwargs)
            point = text_line.intersection(adiabat.geometry)
            if point:
                adiabat.refresh(
                    point.x, point.y, renderer=renderer, **text_kwargs
                )
            else:
                upper = abs(adiabat.extent.temperature.upper - mT)
                lower = abs(adiabat.extent.temperature.lower - mT)
                if snap == "upper" or upper < lower:
                    T = adiabat.extent.temperature.upper
                    t = adiabat.points.theta[adiabat.index.temperature.upper]
                    snap = "upper"
                else:
                    T = adiabat.extent.temperature.lower
                    t = adiabat.points.theta[adiabat.index.temperature.lower]
                    snap = "lower"
                adiabat.refresh(T, t, renderer=renderer, **text_kwargs)


class HumidityMixingRatioArtist(IsoplethArtist):
    def __init__(
        self,
        ticks=None,
        line=None,
        text=None,
        min_pressure=None,
        max_pressure=None,
        nbins=None,
    ):
        super(HumidityMixingRatioArtist, self).__init__()
        if ticks is None:
            ticks = default.get("mixing_ratio_ticks")
        self.ticks = ticks
        self._kwargs = {}
        if line is None:
            line = default.get("mixing_ratio_line")
        self._kwargs["line"] = line
        if text is None:
            text = default.get("mixing_ratio_text")
        self._kwargs["text"] = text
        if min_pressure is None:
            min_pressure = default.get("mixing_ratio_min_pressure")
        self.min_pressure = min_pressure
        if max_pressure is None:
            max_pressure = default.get("mixing_ratio_max_pressure")
        self.max_pressure = max_pressure
        if nbins is None:
            nbins = default.get("mixing_ratio_nbins")
        if nbins is None or (nbins < 2 or isinstance(nbins, str)):
            nbins = None
        self.nbins = nbins

    @matplotlib.artist.allow_rasterization
    def draw(
        self,
        renderer,
        line=None,
        text=None,
        min_pressure=None,
        max_pressure=None,
    ):
        if not self.get_visible():
            return
        axes = self.axes
        draw_kwargs = dict(self._kwargs["line"])
        if line is not None:
            draw_kwargs.update(line)
        text_kwargs = dict(self._kwargs["text"])
        if text is not None:
            text_kwargs.update(text)
        if min_pressure is None:
            min_pressure = self.min_pressure
        if max_pressure is None:
            max_pressure = self.max_pressure

        if self._isopleths is None:
            ratios = []
            for tick in self.ticks:
                ratios.append(
                    HumidityMixingRatio(axes, tick, min_pressure, max_pressure)
                )
            self._isopleths = np.asarray(ratios)

        (x0, x1), (y0, y1) = axes.get_xlim(), axes.get_ylim()
        mask = self._locator(x0, x1, y0, y1)

        mx = x0 + axes.viewLim.width * 0.5
        my = y0 + axes.viewLim.height * 0.5
        temperature, theta = convert_xy2Tt([x0, mx, x1], [y1, my, y0])
        text_line = LineString(zip(temperature, theta))
        mt = theta[1]
        snap = None

        for ratio in self._isopleths[mask]:
            ratio.draw(renderer, **draw_kwargs)
            point = text_line.intersection(ratio.geometry)
            if point:
                ratio.refresh(
                    point.x, point.y, renderer=renderer, **text_kwargs
                )
            else:
                upper = abs(ratio.extent.theta.upper - mt)
                lower = abs(ratio.extent.theta.lower - mt)
                if snap == "upper" or upper < lower:
                    T = ratio.points.temperature[ratio.index.theta.upper]
                    t = ratio.extent.theta.upper
                    snap = "upper"
                else:
                    T = ratio.points.temperature[ratio.index.theta.lower]
                    t = ratio.extent.theta.lower
                    snap = "lower"
                ratio.refresh(T, t, renderer=renderer, **text_kwargs)
