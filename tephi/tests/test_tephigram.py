"""
Tests the Met Office tephigram plotting capability.

"""
# Import Monty test package first so that some things can be initialised
# before importing anything else.
import monty.tests as tests

import cPickle

import matplotlib.pyplot as plt
import numpy as np

import monty
import monty.tephigram as tephigram
from monty.tephigram import Tephigram


def _load_result(filename):
    with open(monty.tests.get_result_path(('tephigram', filename))) as f:
        result = cPickle.load(f)
    return result


_expected_dews = _load_result('dews.pkl')
_expected_temps = _load_result('temps.pkl')
_expected_barbs = _load_result('barbs.pkl')


class TestTephigramLoadTxt(tests.MontyTest):
    def setUp(self):
        self.filename_dews = monty.tests.get_data_path(('tephigram',
                                                        'dews.txt'))
        self.filename_temps = monty.tests.get_data_path(('tephigram',
                                                         'temps.txt'))
        self.filename_barbs = monty.tests.get_data_path(('tephigram',
                                                         'barbs.txt'))
        self.filename_comma = monty.tests.get_data_path(('tephigram',
                                                         'comma_sep.txt'))
        self.filename_miss = monty.tests.get_data_path(('tephigram',
                                                        'missing_values.txt'))

    def test_is_not_file(self):
        with self.assertRaises(OSError):
            tephigram.loadtxt('wibble')

    def test_load_data_no_column_names(self):
        dews = tephigram.loadtxt(self.filename_dews)
        self.assertEqual(dews._fields, ('pressure', 'temperature'))
        self.assertArrayEqual(dews.pressure, _expected_dews[0])
        self.assertArrayEqual(dews, _expected_dews)

    def test_load_data_with_column_names(self):
        # Column titles test all valid namedtuple characters (alphanumeric, _).
        columns = ('pressure', 'dewpoint2', 'wind_speed', 'WindDirection')
        barbs = tephigram.loadtxt(self.filename_barbs, column_titles=columns)
        self.assertEqual(barbs._fields, columns)
        self.assertArrayEqual(barbs.wind_speed, _expected_barbs[2])
        self.assertArrayEqual(barbs, _expected_barbs)

    def test_load_multiple_files_same_column_names(self):
        columns = ('foo', 'bar')
        dews, temps = tephigram.loadtxt(self.filename_dews,
                                        self.filename_temps,
                                        column_titles=columns)
        self.assertEqual(dews._fields, columns)
        self.assertEqual(temps._fields, columns)

    def test_load_data_too_many_column_iterables(self):
        columns = [('pressure', 'dewpoint'),
                   ('pressure', 'wind_speed', 'wind_direction')]
        with self.assertRaises(ValueError):
            dews = tephigram.loadtxt(self.filename_dews, column_titles=columns)

    def test_number_of_columns_and_titles_not_equal(self):
        columns = ('pressure', 'dewpoint', 'wind_speed')
        with self.assertRaises(TypeError):
            barbs = tephigram.loadtxt(self.filename_barbs,
                                      column_titles=columns)

    def test_invalid_column_titles(self):
        columns = ('pres-sure', 'dew+point', 5)
        with self.assertRaises(ValueError):
            dews = tephigram.loadtxt(self.filename_dews,
                                     column_titles=columns)

    def test_non_iterable_column_title(self):
        # For the case of column titles, strings are considered non-iterable.
        columns = 'pressure'
        with self.assertRaises(TypeError):
            dews = tephigram.loadtxt(self.filename_dews,
                                     column_titles=columns)

    def test_delimiter(self):
        columns = ('pressure', 'temperature', 'wind_direction', 'wind_speed')
        data = tephigram.loadtxt(self.filename_comma, column_titles=columns,
                                 delimiter=',')
        self.assertEqual(data.pressure.shape, (2,))

    def test_dtype(self):
        dews = tephigram.loadtxt(self.filename_dews, dtype='i4')
        self.assertIsInstance(dews.pressure[0], np.int32)
        self.assertIsInstance(dews.temperature[0], np.int32)


class TestTephigramPlot(tests.GraphicsTest):
    def setUp(self):
        dew_data = _expected_dews
        self.dews = zip(dew_data[0], dew_data[1])
        temp_data = _expected_temps
        self.temps = zip(temp_data[0], temp_data[1])

    def test_plot_dews(self):
        tephi = Tephigram()
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_temps(self):
        tephi = Tephigram()
        tephi.plot(self.temps)
        self.check_graphic()

    def test_plot_dews_temps(self):
        tephi = Tephigram()
        tephi.plot(self.dews)
        tephi.plot(self.temps)
        self.check_graphic()

    def test_plot_dews_brand(self):
        tephi = Tephigram()
        tephi.plot(self.dews)
        monty.brand(plt.gcf())
        self.check_graphic()

    def test_plot_temps_brand(self):
        tephi = Tephigram()
        tephi.plot(self.temps)
        monty.brand(plt.gcf())
        self.check_graphic()

    def test_plot_dews_temps_brand(self):
        tephi = Tephigram()
        tephi.plot(self.dews)
        tephi.plot(self.temps)
        fig = plt.gcf()
        monty.brand(fig)
        fig.suptitle('Christmas Island 29 April 1958 01Z', y = 0.9, fontsize=18)
        self.check_graphic()

    def test_plot_dews_label(self):
        tephi = Tephigram()
        tephi.plot(self.dews, label='Dew-point temperature')
        self.check_graphic()

    def test_plot_temps_label(self):
        tephi = Tephigram()
        tephi.plot(self.temps, label='Dry-bulb temperature')
        self.check_graphic()

    def test_plot_dews_custom(self):
        tephi = Tephigram()
        tephi.plot(self.dews, label='Dew-point temperature', linewidth=2, color='blue', marker='s')
        self.check_graphic()

    def test_plot_temps_custom(self):
        tephi = Tephigram()
        tephi.plot(self.temps, label='Dry-bulb emperature', linewidth=2, color='red', marker='o')
        self.check_graphic()

    def test_plot_dews_temps_custom(self):
        tephi = Tephigram()
        tephi.plot(self.dews, label='Dew-point temperature', linewidth=2, color='blue', marker='s')
        tephi.plot(self.temps, label='Dry-bulb emperature', linewidth=2, color='red', marker='o')
        self.check_graphic()

    def test_plot_dews_locator_isotherm_numeric(self):
        tephi = Tephigram(isotherm_locator=10)
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_isotherm_object(self):
        tephi = Tephigram(isotherm_locator=tephigram.Locator(10))
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_adiabat_numeric(self):
        tephi = Tephigram(dry_adiabat_locator=10)
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_adiabat_object(self):
        tephi = Tephigram(dry_adiabat_locator=tephigram.Locator(10))
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_numeric(self):
        tephi = Tephigram(isotherm_locator=10, dry_adiabat_locator=10)
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_dews_locator_object(self):
        locator = tephigram.Locator(10)
        tephi = Tephigram(isotherm_locator=locator, dry_adiabat_locator=locator)
        tephi.plot(self.dews)
        self.check_graphic()

    def test_plot_anchor(self):
        tephi = Tephigram(anchor=[(1000, 0), (300, 0)])
        tephi.plot(self.dews)
        self.check_graphic()


class TestTephigramBarbs(tests.GraphicsTest):
    def setUp(self):
        self.dews = zip(_expected_dews[0], _expected_dews[1])
        temp_data = _expected_temps
        self.temps = zip(_expected_temps[0], _expected_temps[1])
        magnitude = np.hstack(([0], np.arange(20) * 5 + 2, [102]))
        self.barbs = [(m, 45, 1000 - i*35) for i, m in enumerate(magnitude)]

    def test_rotate(self):
        tephi = Tephigram()
        profile = tephi.plot(self.temps)
        profile.barbs([(0, 0, 900),
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
                       (55, 360, 300)], zorder=10)
        self.check_graphic()

    def test_barbs(self):
        tephi = Tephigram()
        profile = tephi.plot(self.temps)
        profile.barbs(self.barbs, zorder=10)
        self.check_graphic()

    def test_barbs_from_file(self):
        tephi = Tephigram()
        dews = zip(_expected_barbs[0], _expected_barbs[1])
        barbs = zip(_expected_barbs[2], _expected_barbs[3], _expected_barbs[0])
        profile = tephi.plot(dews)
        profile.barbs(barbs, zorder=10)
        self.check_graphic()

    def test_gutter(self):
        tephi = Tephigram()
        profile = tephi.plot(self.temps)
        profile.barbs(self.barbs, gutter=0.5, zorder=10)
        self.check_graphic()

    def test_length(self):
        tephi = Tephigram()
        profile = tephi.plot(self.temps)
        profile.barbs(self.barbs, gutter=0.9, length=10, zorder=10)
        self.check_graphic()

    def test_color(self):
        tephi = Tephigram()
        profile = tephi.plot(self.temps)
        profile.barbs(self.barbs, color='green', zorder=10)
        self.check_graphic()

    def test_pivot(self):
        tephi = Tephigram()
        tprofile = tephi.plot(self.temps)
        tprofile.barbs(self.barbs, gutter=0.2, pivot='tip', length=8)
        dprofile = tephi.plot(self.dews)
        dprofile.barbs(self.barbs, gutter=0.3, pivot='middle', length=8)
        self.check_graphic()


if __name__ == '__main__':
    tests.main()
