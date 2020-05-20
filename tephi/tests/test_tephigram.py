# Copyright Tephi contributors
#
# This file is part of Tephi and is released under the LGPL license.
# See COPYING and COPYING.LESSER in the root of the repository for full
# licensing details.
"""
Tests the tephigram plotting capability provided by tephi.

"""
# Import tephi test package first so that some things can be initialised
# before importing anything else.
import tephi.tests as tests

import unittest

import numpy as np

import tephi
from tephi import Tephigram


def _load_result(filename):
    with np.load(tephi.tests.get_result_path(filename)) as f:
        result = f["arr_0"]
    return result


_expected_dews = _load_result("dews.npz")
_expected_temps = _load_result("temps.npz")
_expected_barbs = _load_result("barbs.npz")


class TestTephigramLoadTxt(tests.TephiTest):
    def setUp(self):
        self.filename_dews = tephi.tests.get_data_path("dews.txt")
        self.filename_temps = tephi.tests.get_data_path("temps.txt")
        self.filename_barbs = tephi.tests.get_data_path("barbs.txt")
        self.filename_comma = tephi.tests.get_data_path("comma_sep.txt")

    def test_is_not_file(self):
        with self.assertRaises(OSError):
            tephi.loadtxt("wibble")

    def test_load_data_no_column_names(self):
        dews = tephi.loadtxt(self.filename_dews)
        self.assertEqual(dews._fields, ("pressure", "temperature"))
        self.assertArrayEqual(dews.pressure, _expected_dews[0])
        self.assertArrayEqual(dews, _expected_dews)

    def test_load_data_with_column_names(self):
        # Column titles test all valid namedtuple characters (alphanumeric, _).
        columns = ("pressure", "dewpoint2", "wind_speed", "WindDirection")
        barbs = tephi.loadtxt(self.filename_barbs, column_titles=columns)
        self.assertEqual(barbs._fields, columns)
        self.assertArrayEqual(barbs.wind_speed, _expected_barbs[2])
        self.assertArrayEqual(barbs, _expected_barbs)

    def test_load_multiple_files_same_column_names(self):
        columns = ("foo", "bar")
        dews, temps = tephi.loadtxt(
            self.filename_dews, self.filename_temps, column_titles=columns
        )
        self.assertEqual(dews._fields, columns)
        self.assertEqual(temps._fields, columns)

    def test_load_data_too_many_column_iterables(self):
        columns = [
            ("pressure", "dewpoint"),
            ("pressure", "wind_speed", "wind_direction"),
        ]
        with self.assertRaises(ValueError):
            tephi.loadtxt(self.filename_dews, column_titles=columns)

    def test_number_of_columns_and_titles_not_equal(self):
        columns = ("pressure", "dewpoint", "wind_speed")
        with self.assertRaises(TypeError):
            tephi.loadtxt(self.filename_barbs, column_titles=columns)

    def test_invalid_column_titles(self):
        columns = ("pres-sure", "dew+point", 5)
        with self.assertRaises(ValueError):
            tephi.loadtxt(self.filename_dews, column_titles=columns)

    def test_non_iterable_column_title(self):
        # For the case of column titles, strings are considered non-iterable.
        columns = "pressure"
        with self.assertRaises(TypeError):
            tephi.loadtxt(self.filename_dews, column_titles=columns)

    def test_delimiter(self):
        columns = ("pressure", "temperature", "wind_direction", "wind_speed")
        data = tephi.loadtxt(
            self.filename_comma, column_titles=columns, delimiter=","
        )
        self.assertEqual(data.pressure.shape, (2,))

    def test_dtype(self):
        dews = tephi.loadtxt(self.filename_dews, dtype="i4")
        self.assertIsInstance(dews.pressure[0], np.int32)
        self.assertIsInstance(dews.temperature[0], np.int32)


class TestTephigramPlot(tests.GraphicsTest):
    def setUp(self):
        self.dews = _expected_dews.T
        self.temps = _expected_temps.T

    def test_plot_dews(self):
        tpg = Tephigram()
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_temps(self):
        tpg = Tephigram()
        tpg.plot(self.temps)
        self.check_graphic()

    def test_plot_dews_temps(self):
        tpg = Tephigram()
        tpg.plot(self.dews)
        tpg.plot(self.temps)
        self.check_graphic()

    def test_plot_dews_label(self):
        tpg = Tephigram()
        tpg.plot(self.dews, label="Dew-point temperature")
        self.check_graphic()

    def test_plot_temps_label(self):
        tpg = Tephigram()
        tpg.plot(self.temps, label="Dry-bulb temperature")
        self.check_graphic()

    def test_plot_dews_custom(self):
        tpg = Tephigram()
        tpg.plot(
            self.dews,
            label="Dew-point temperature",
            linewidth=2,
            color="blue",
            marker="s",
        )
        self.check_graphic()

    def test_plot_temps_custom(self):
        tpg = Tephigram()
        tpg.plot(
            self.temps,
            label="Dry-bulb temperature",
            linewidth=2,
            color="red",
            marker="o",
        )
        self.check_graphic()

    def test_plot_dews_temps_custom(self):
        tpg = Tephigram()
        tpg.plot(
            self.dews,
            label="Dew-point temperature",
            linewidth=2,
            color="blue",
            marker="s",
        )
        tpg.plot(
            self.temps,
            label="Dry-bulb temperature",
            linewidth=2,
            color="red",
            marker="o",
        )
        self.check_graphic()

    def test_plot_dews_locator_isotherm_numeric(self):
        tpg = Tephigram(isotherm_locator=10)
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_isotherm_object(self):
        tpg = Tephigram(isotherm_locator=tephi.Locator(10))
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_adiabat_numeric(self):
        tpg = Tephigram(dry_adiabat_locator=10)
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_adiabat_object(self):
        tpg = Tephigram(dry_adiabat_locator=tephi.Locator(10))
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_numeric(self):
        tpg = Tephigram(isotherm_locator=10, dry_adiabat_locator=10)
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_object(self):
        locator = tephi.Locator(10)
        tpg = Tephigram(isotherm_locator=locator, dry_adiabat_locator=locator)
        tpg.plot(self.dews)
        self.check_graphic()

    def test_plot_anchor(self):
        tpg = Tephigram(anchor=[(1000, 0), (300, 0)])
        tpg.plot(self.dews)
        self.check_graphic()


class TestTephigramBarbs(tests.GraphicsTest):
    def setUp(self):
        self.dews = _expected_dews.T
        self.temps = _expected_temps.T
        magnitude = np.hstack(([0], np.arange(20) * 5 + 2, [102]))
        self.barbs = [(m, 45, 1000 - i * 35) for i, m in enumerate(magnitude)]

    def test_rotate(self):
        tpg = Tephigram()
        profile = tpg.plot(self.temps)
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
        self.check_graphic()

    def test_barbs(self):
        tpg = Tephigram()
        profile = tpg.plot(self.temps)
        profile.barbs(self.barbs, zorder=10)
        self.check_graphic()

    def test_barbs_from_file(self):
        tpg = Tephigram()
        dews = _expected_barbs.T[:, :2]
        barbs = np.column_stack(
            (_expected_barbs[2], _expected_barbs[3], _expected_barbs[0])
        )
        profile = tpg.plot(dews)
        profile.barbs(barbs, zorder=10)
        self.check_graphic()

    def test_gutter(self):
        tpg = Tephigram()
        profile = tpg.plot(self.temps)
        profile.barbs(self.barbs, gutter=0.5, zorder=10)
        self.check_graphic()

    def test_length(self):
        tpg = Tephigram()
        profile = tpg.plot(self.temps)
        profile.barbs(self.barbs, gutter=0.9, length=10, zorder=10)
        self.check_graphic()

    def test_color(self):
        tpg = Tephigram()
        profile = tpg.plot(self.temps)
        profile.barbs(self.barbs, color="green", zorder=10)
        self.check_graphic()

    def test_pivot(self):
        tpg = Tephigram()
        tprofile = tpg.plot(self.temps)
        tprofile.barbs(self.barbs, gutter=0.2, pivot="tip", length=8)
        dprofile = tpg.plot(self.dews)
        dprofile.barbs(self.barbs, gutter=0.3, pivot="middle", length=8)
        self.check_graphic()


if __name__ == "__main__":
    unittest.main()
