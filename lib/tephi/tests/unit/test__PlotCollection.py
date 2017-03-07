# (C) British Crown Copyright 2014 - 2017, Met Office
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
Unit tests for the `tephi._PlotCollection` class.

"""
from __future__ import (absolute_import, division, print_function)

import unittest

import mock

from tephi import _PlotCollection


class Test__spec_singleton(unittest.TestCase):
    def setUp(self):
        self.axes = mock.sentinel.axes
        self.func = mock.sentinel.func
        self.kwargs = mock.sentinel.kwargs
        self.zoom = mock.sentinel.zoom
        self.step = 1
        self.spec = [(self.step, self.zoom)]
        self.stop = 10
        self.istop = range(10)
        self.expected = [self.axes, self.func, self.kwargs, self.step,
                         self.zoom]

    @mock.patch('tephi._PlotGroup')
    def test(self, mocker):
        pc = _PlotCollection(self.axes, self.spec, self.stop, self.func,
                             self.kwargs)
        self.assertEqual(len(pc.groups), 1)
        self.assertEqual(mocker.call_count, 1)
        args, kwargs = mocker.call_args
        item = set(range(self.step, self.step+self.stop, self.step))
        self.expected.append(item)
        self.assertEqual(args, tuple(self.expected))

    @mock.patch('tephi._PlotGroup')
    def test_minimum_clip(self, mocker):
        minimum = 5
        pc = _PlotCollection(self.axes, self.spec, self.stop, self.func,
                             self.kwargs, minimum=minimum)
        self.assertEqual(len(pc.groups), 1)
        self.assertEqual(mocker.call_count, 1)
        args, kwargs = mocker.call_args
        item = set(range(minimum, self.step+self.stop, self.step))
        self.expected.append(item)
        self.assertEqual(args, tuple(self.expected))

    @mock.patch('tephi._PlotGroup')
    def test_minimum(self, mocker):
        minimum = -5
        pc = _PlotCollection(self.axes, self.spec, self.stop, self.func,
                             self.kwargs, minimum=minimum)
        self.assertEqual(len(pc.groups), 1)
        self.assertEqual(mocker.call_count, 1)
        args, kwargs = mocker.call_args
        item = set(range(minimum, self.step+self.stop, self.step))
        self.expected.append(item)
        self.assertEqual(args, tuple(self.expected))

    @mock.patch('tephi._PlotGroup')
    def test_minimum_bad(self, mocker):
        minimum = self.stop+1
        emsg = ('Minimum value of {} exceeds maximum '
                'threshold {}'.format(minimum, self.stop))
        with self.assertRaisesRegexp(ValueError, emsg):
            _PlotCollection(self.axes, self.spec, self.stop, self.func,
                            self.kwargs, minimum=minimum)

    @mock.patch('tephi._PlotGroup')
    def test_iterable(self, mocker):
        pc = _PlotCollection(self.axes, self.spec, self.istop, self.func,
                             self.kwargs)
        self.assertEqual(len(pc.groups), 1)
        self.assertEqual(mocker.call_count, 1)
        args, kwargs = mocker.call_args
        item = set(self.istop)
        self.expected.append(item)
        self.assertEqual(args, tuple(self.expected))

    @mock.patch('tephi._PlotGroup')
    def test_iterable_minimum_clip(self, mocker):
        minimum = 7
        pc = _PlotCollection(self.axes, self.spec, self.istop, self.func,
                             self.kwargs, minimum=minimum)
        self.assertEqual(len(pc.groups), 1)
        self.assertEqual(mocker.call_count, 1)
        args, kwargs = mocker.call_args
        item = set(self.istop[minimum:])
        self.expected.append(item)
        self.assertEqual(args, tuple(self.expected))

    @mock.patch('tephi._PlotGroup')
    def test_iterable_minimum_bad(self, mocker):
        minimum = self.istop[-1]+1
        emsg = 'Minimum value of {} exceeds all other values'.format(minimum)
        with self.assertRaisesRegexp(ValueError, emsg):
            _PlotCollection(self.axes, self.spec, self.istop, self.func,
                            self.kwargs, minimum=minimum)


if __name__ == '__main__':
    unittest.main()
