# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the BSD license.
# See LICENSE in the root of the repository for full licensing details.
"""
Tests the tephigram plotting capability provided by tephi.

"""
import matplotlib

# Import tephi test package first so that some things can be initialised
# before importing anything else.
import tephi.tests as tests

import numpy as np
import pytest

import tephi
from tephi import TephiAxes


def _load_result(filename):
    with np.load(tephi.tests.get_result_path(filename)) as f:
        result = f["arr_0"]
    return result


_expected_dews = _load_result("dews.npz")
_expected_temps = _load_result("temps.npz")
_expected_barbs = _load_result("barbs.npz")

# make the default size for this session 8x8in
matplotlib.rcParams['figure.figsize'] = (8, 8)

class TestTephigramLoadTxt(tests.TephiTest):
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.filename_dews = tephi.tests.get_data_path("dews.txt")
        self.filename_temps = tephi.tests.get_data_path("temps.txt")
        self.filename_barbs = tephi.tests.get_data_path("barbs.txt")
        self.filename_comma = tephi.tests.get_data_path("comma_sep.txt")

    def test_is_not_file(self):
        with pytest.raises(OSError):
            tephi.loadtxt("wibble")

    def test_load_data_no_column_names(self):
        dews = tephi.loadtxt(self.filename_dews)
        assert dews._fields == ("pressure", "temperature")
        self.assertArrayEqual(dews.pressure, _expected_dews[0])
        self.assertArrayEqual(dews, _expected_dews)

    def test_load_data_with_column_names(self):
        # Column titles test all valid namedtuple characters (alphanumeric, _).
        columns = ("pressure", "dewpoint2", "wind_speed", "WindDirection")
        barbs = tephi.loadtxt(self.filename_barbs, column_titles=columns)
        assert barbs._fields == columns
        self.assertArrayEqual(barbs.wind_speed, _expected_barbs[2])
        self.assertArrayEqual(barbs, _expected_barbs)

    def test_load_multiple_files_same_column_names(self):
        columns = ("foo", "bar")
        dews, temps = tephi.loadtxt(
            self.filename_dews, self.filename_temps, column_titles=columns
        )
        assert dews._fields == columns
        assert temps._fields == columns

    def test_load_data_too_many_column_iterables(self):
        columns = [
            ("pressure", "dewpoint"),
            ("pressure", "wind_speed", "wind_direction"),
        ]
        with pytest.raises(ValueError):
            tephi.loadtxt(self.filename_dews, column_titles=columns)

    def test_number_of_columns_and_titles_not_equal(self):
        columns = ("pressure", "dewpoint", "wind_speed")
        with pytest.raises(TypeError):
            tephi.loadtxt(self.filename_barbs, column_titles=columns)

    def test_invalid_column_titles(self):
        columns = ("pres-sure", "dew+point", 5)
        with pytest.raises(ValueError):
            tephi.loadtxt(self.filename_dews, column_titles=columns)

    def test_non_iterable_column_title(self):
        # For the case of column titles, strings are considered non-iterable.
        columns = "pressure"
        with pytest.raises(TypeError):
            tephi.loadtxt(self.filename_dews, column_titles=columns)

    def test_delimiter(self):
        columns = ("pressure", "temperature", "wind_direction", "wind_speed")
        data = tephi.loadtxt(
            self.filename_comma, column_titles=columns, delimiter=","
        )
        assert data.pressure.shape == (2,)

    def test_dtype(self):
        dews = tephi.loadtxt(self.filename_dews, dtype="i4")
        assert dews.pressure[0].dtype == np.int32
        assert dews.temperature[0].dtype == np.int32

@pytest.mark.graphical
@pytest.mark.usefixtures("close_plot", "nodeid")
class TestTephigramPlot(tests.GraphicsTest):
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.dews = _expected_dews.T
        self.temps = _expected_temps.T

        self.tephigram = TephiAxes()

    def test_plot_dews(self, nodeid):
        self.tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_temps(self, nodeid):
        self.tephigram.plot(self.temps)
        self.check_graphic(nodeid)

    def test_plot_dews_temps(self, nodeid):
        self.tephigram.plot(self.dews)
        self.tephigram.plot(self.temps)
        self.check_graphic(nodeid)

    def test_plot_dews_label(self, nodeid):
        self.tephigram.plot(self.dews, label="Dew-point temperature")
        self.check_graphic(nodeid)

    def test_plot_temps_label(self, nodeid):
        self.tephigram.plot(self.temps, label="Dry-bulb temperature")
        self.check_graphic(nodeid)

    def test_plot_dews_custom(self, nodeid):
        self.tephigram.plot(
            self.dews,
            label="Dew-point temperature",
            linewidth=2,
            color="blue",
            marker="s",
        )
        self.check_graphic(nodeid)

    def test_plot_temps_custom(self, nodeid):
        self.tephigram.plot(
            self.temps,
            label="Dry-bulb temperature",
            linewidth=2,
            color="red",
            marker="o",
        )
        self.check_graphic(nodeid)

    def test_plot_dews_temps_custom(self, nodeid):
        self.tephigram.plot(
            self.dews,
            label="Dew-point temperature",
            linewidth=2,
            color="blue",
            marker="s",
        )
        self.tephigram.plot(
            self.temps,
            label="Dry-bulb temperature",
            linewidth=2,
            color="red",
            marker="o",
        )
        self.check_graphic(nodeid)

@pytest.mark.graphical
@pytest.mark.usefixtures("close_plot", "nodeid")
class TestTephigramAxes(tests.GraphicsTest):
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.dews = _expected_dews.T
        self.temps = _expected_temps.T

    def test_plot_dews_locator_isotherm_numeric(self, nodeid):
        tephigram = TephiAxes(isotherm_locator=30)
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_dews_locator_isotherm_object(self, nodeid):
        tephigram = TephiAxes(isotherm_locator=tephi.Locator(10))
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_dews_locator_adiabat_numeric(self, nodeid):
        tephigram = TephiAxes(dry_adiabat_locator=10)
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_dews_locator_adiabat_object(self, nodeid):
        tephigram = TephiAxes(dry_adiabat_locator=tephi.Locator(10))
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_dews_locator_numeric(self, nodeid):
        tephigram = TephiAxes(isotherm_locator=10, dry_adiabat_locator=10)
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_dews_locator_object(self, nodeid):
        locator = tephi.Locator(10)
        tephigram = TephiAxes(
            isotherm_locator=locator, dry_adiabat_locator=locator
        )
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_plot_xylim(self, nodeid):
        tephigram = TephiAxes(xylim=[(0, 0), (40, 200)])
        tephigram.plot(self.dews)
        self.check_graphic(nodeid)

    def test_add_wet_adiabats(self, nodeid):
        # the xylim is needed so that the isopleths actually appear
        tephigram = TephiAxes(xylim=[(0, 0), (40, 70)])

        tephigram.add_wet_adiabats()
        self.check_graphic(nodeid)

    def test_add_humidity_mixing_ratios(self, nodeid):
        # the xylim is needed so that the isopleths actually appear
        tephigram = TephiAxes(xylim=[(0, 0), (40, 70)])

        tephigram.add_mixing_ratios()
        self.check_graphic(nodeid)

    def test_add_isobars(self, nodeid):
        # the xylim is needed so that the isopleths actually appear
        tephigram = TephiAxes(xylim=[(0, 0), (40, 70)])

        tephigram.add_isobars()
        self.check_graphic(nodeid)

@pytest.mark.graphical
@pytest.mark.usefixtures("close_plot", "nodeid")
class TestTephigramBarbs(tests.GraphicsTest):
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.dews = _expected_dews.T
        self.temps = _expected_temps.T
        magnitude = np.hstack(([0], np.arange(20) * 5 + 2, [102]))
        self.barbs = [(m, 45, 1000 - i * 35) for i, m in enumerate(magnitude)]
        self.tephigram = TephiAxes()

    def test_rotate(self, nodeid):
        profile = self.tephigram.plot(self.temps)
        profile.barbs(
            [
                (0, 0, 900),
                (1, 30, 850),
                (5, 60, 800),
                (10, 90, 750),
                (15, 120, 700),
                (20, 150, 650),
                (25, 180, 600),
                (30, 210, 550),
                (35, 240, 500),
                (40, 270, 450),
                (45, 300, 400),
                (50, 330, 350),
                (55, 360, 300),
            ],
            zorder=10,
        )
        self.check_graphic(nodeid)

    def test_barbs(self, nodeid):
        profile = self.tephigram.plot(self.temps)
        profile.barbs(self.barbs, zorder=10)
        self.check_graphic(nodeid)

    def test_barbs_from_file(self, nodeid):
        dews = _expected_barbs.T[:, :2]
        barbs = np.column_stack(
            (_expected_barbs[2], _expected_barbs[3], _expected_barbs[0])
        )
        profile = self.tephigram.plot(dews)
        profile.barbs(barbs, zorder=200)
        self.check_graphic(nodeid)

    def test_gutter(self, nodeid):
        profile = self.tephigram.plot(self.temps)
        profile.barbs(self.barbs, gutter=0.5, zorder=10)
        self.check_graphic(nodeid)

    def test_length(self, nodeid):
        profile = self.tephigram.plot(self.temps)
        profile.barbs(self.barbs, gutter=0.9, length=10, zorder=10)
        self.check_graphic(nodeid)

    def test_color(self, nodeid):
        profile = self.tephigram.plot(self.temps)
        profile.barbs(self.barbs, color="green", zorder=10)
        self.check_graphic(nodeid)

    def test_pivot(self, nodeid):
        tprofile = self.tephigram.plot(self.temps)
        tprofile.barbs(self.barbs, gutter=0.2, pivot="tip", length=8)
        dprofile = self.tephigram.plot(self.dews)
        dprofile.barbs(self.barbs, gutter=0.3, pivot="middle", length=8)
        self.check_graphic(nodeid)

class TestSubplots(tests.GraphicsTest):
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.dews = _expected_dews.T
        self.temps = _expected_temps.T

    def test_subplot(self, nodeid):
        tephi_one = TephiAxes(133)
        tephi_two = TephiAxes((1,3,1))

        tephi_one.plot(self.temps)
        tephi_one.plot(self.dews)
        tephi_two.plot(self.dews)

        self.check_graphic(nodeid)
