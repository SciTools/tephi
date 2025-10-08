.. tephigram_user_guide_customise:

Tephigram customisation
=======================

This section discusses how finer control of the tephigram isobars, saturated adiabats and humidity mixing ratio lines and text can be achieved.

.. testsetup::

   import tephi
   from pprint import pprint


Isobar control
--------------

Isobar lines
^^^^^^^^^^^^

The default behaviour of the tephigram *isobar line* is controlled by the :data:`tephi.constants.default["isobar_line"]`
dictionary:

   >>> print(tephi.constants.default["isobar_line"])
   {'color': 'blue', 'linewidth': 0.5, 'clip_on': True}

This is a dictionary of *key* and *value* pairs that are passed through as keyword arguments to :func:`matplotlib.pyplot.plot`.

Updating the ``tephi.constants.default["isobar_line"]`` dictionary will subsequently change the default behaviour of
how the tephigram isobar lines are plotted.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi
   from tephi.constants import default

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   default["isobar_line"].update({'color': 'purple', 'linewidth': 3, 'linestyle': '--'})
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   from tephi.constants import default
   default["isobar_line"] = {'color': 'blue', 'linewidth': 0.5, 'clip_on': True}


Isobar text
^^^^^^^^^^^

Similarly, the default behaviour of the tephigram *isobar text* is controlled by the
:data:`tephi.constants.default["isobar_text"]` dictionary:

   >>> pprint(tephi.constants.default["isobar_text"])
   {'clip_on': True, 'color': 'blue', 'ha': 'right', 'size': 8, 'va': 'bottom'}

This is a dictionary of *key* and *value* pairs that are passed through as keyword arguments to :func:`matplotlib.pyplot.text`.

Updating the ``tephi.constants.default["isobar_text"]`` dictionary will change the default behaviour of how the
tephigram isobar text is plotted.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi
   from tephi.constants import default

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   default["isobar_text"].update({'color': 'purple', 'size': 12})
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   from tephi.constants import default
   default["isobar_text"] = {'color': 'blue', 'va': 'bottom', 'ha': 'right', 'clip_on': True, 'size': 8}


Isobar frequency
^^^^^^^^^^^^^^^^

The values at which isobars lines can be created is controlled by the
:data:`tephi.common.default["isobar_ticks"]` value:

   >>> print(tephi.common.default["isobar_ticks"])
   [1050, 1000, 950, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 40, 30, 20, 10]

The *frequency* at which isobar lines are plotted on the tephigram is controlled by the
:data:`tephi.common.default["isobar_nbins"]` value:

   >>> print(tephi.common.default["isobar_nbins"])
   None

``nbins`` controls the maximum number of lines plotted at one time. It can either be an integer value, or a ``None``
value, which means that a line will be shown for every tick in :data:`tephi.common.default["isobar_ticks"]`.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi
   from tephi.common import default

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   default["isobar_ticks"] = [900, 875, 850]
   default["isobar_nbins"] = 2
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   from tephi.constants import default
   default["isobar_ticks"] = [1050, 1000, 950, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 40, 30, 20, 10]
   default["isobar_nbins"] = None


Isobar line extent
^^^^^^^^^^^^^^^^^^

The extent of each tephigram *isobar line* is controlled by the :data:`tephi.constants.default["isobar_min_theta"]` and
:data:`tephi.constants.default["isobar_max_theta"]` variables:

   >>> print(tephi.constants.default["isobar_min_theta"])
   0
   >>> print(tephi.constants.default["isobar_max_theta"])
   250

For example, to change the isobar line extent behaviour to be between 15 :sup:`o`\ C and 60 :sup:`o`\ C,

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi
   from tephi.constants import default

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   default["isobar_max_theta"] = 15
   default["isobar_max_theta"] = 60
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   from tephi.constants import default
   default["isobar_max_theta"] = 0
   default["isobar_max_theta"] = 250


Saturated adiabat control
-------------------------

Saturated adiabat lines
^^^^^^^^^^^^^^^^^^^^^^^

The default behaviour of the tephigram *pseudo saturated wet adiabat line* is controlled by the :data:`tephi.WET_ADIABAT_LINE` dictionary:

   >>> print(tephi.WET_ADIABAT_LINE)
   {'color': 'orange', 'linewidth': 0.5, 'clip_on': True}

This is a dictionary of *key* and *value* pairs that are passed through as keyword arguments to :func:`matplotlib.pyplot.plot`.

Updating the ``WET_ADIABAT_LINE`` dictionary will change the default behaviour of **all** saturated adiabat line plotting.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.WET_ADIABAT_LINE.update({'color': 'purple', 'linewidth': 3, 'linestyle': '--'})
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.WET_ADIABAT_LINE = {'color': 'orange', 'linewidth': 0.5, 'clip_on': True}


Saturated adiabat text
^^^^^^^^^^^^^^^^^^^^^^

The default behaviour of the tephigram *saturated adiabat text* is controlled by the :data:`tephi.WET_ADIABAT_TEXT` dictionary:

   >>> pprint(tephi.WET_ADIABAT_TEXT)
   {'clip_on': True, 'color': 'orange', 'ha': 'left', 'size': 8, 'va': 'bottom'}

This is a dictionary of *key* and *value* pairs that are passed through as keyword arguments to :func:`matplotlib.pyplot.text`.

Updating the ``WET_ADIABAT_TEXT`` dictionary will change the default behaviour of how the text of associated saturated adiabat lines are plotted.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.WET_ADIABAT_TEXT.update({'color': 'purple', 'size': 12})
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.WET_ADIABAT_TEXT = {'color': 'orange', 'va': 'bottom', 'ha': 'left', 'clip_on': True, 'size': 8}


Saturated adiabat line frequency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *frequency* at which saturated adiabat lines are plotted on the tephigram is controlled by the :data:`tephi.WET_ADIABAT_SPEC` list:

   >>> print(tephi.WET_ADIABAT_SPEC)
   [(1, 0.05), (2, 0.15), (4, 1.5)]

This :term:`line specification` is a sequence of one or more tuple pairs that contain a saturated adiabat temperature :term:`line step` and a
:term:`zoom level`.

For example, ``(2, 0.15)`` states that all saturated adiabat lines that are a multiple of ``2`` :sup:`o`\ C will be plotted i.e. visible,
when the :term:`zoom level` is at or below ``0.15``.

The *overall range* of saturated adiabat levels that may be plotted is controlled by the :data:`tephi.MIN_WET_ADIABAT` and
:data:`tephi.MAX_WET_ADIABAT` variables:

   >>> print(tephi.MIN_WET_ADIABAT)
   1
   >>> print(tephi.MAX_WET_ADIABAT)
   60

Note that, it is possible to set a *fixed* saturated adiabat temperature :term:`line step` for a tephigram plot by setting the
associated :term:`zoom level` to ``None``.

For example, to **always** show saturated adiabat lines that are a multiple of 5 :sup:`o`\ C, irrespective of the :term:`zoom level`,

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.WET_ADIABAT_SPEC = [(5, None)]
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.WET_ADIABAT_SPEC = [(1, 0.05), (2, 0.15), (4, 1.5)]

It is also possible to control which *individual* saturated adiabat lines should be *fixed* via the :data:`tephi.WET_ADIABAT_FIXED` variable:

   >>> print(tephi.WET_ADIABAT_FIXED)
   None

By default, no saturated adiabat lines are fixed. To force saturated adiabat lines with a temperature of ``15`` :sup:`o`\ C and ``17`` :sup:`o`\ C
always to be plotted,

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.WET_ADIABAT_FIXED = [15, 17]
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.WET_ADIABAT_FIXED = None


Humidity mixing ratio control
-----------------------------

Humidity mixing ratio lines
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default behaviour of the tephigram *humidity mixing ratio line* is controlled by the :data:`tephi.MIXING_RATIO_LINE` dictionary:

   >>> print(tephi.MIXING_RATIO_LINE)
   {'color': 'green', 'linewidth': 0.5, 'clip_on': True}

This is a dictionary of *key* and *value* pairs that are passed through as keyword arguments to :func:`matplotlib.pyplot.plot`.

Updating the ``MIXING_RATIO_LINE`` dictionary will change the default behaviour of **all** humidity mixing ratio line plotting.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.MIXING_RATIO_LINE.update({'color': 'purple', 'linewidth': 3, 'linestyle': '--'})
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.MIXING_RATIO_LINE = {'color': 'green', 'linewidth': 0.5, 'clip_on': True}


Humidity mixing ratio text
^^^^^^^^^^^^^^^^^^^^^^^^^^

The default behaviour of the tephigram *humidity mixing ratio text* is controlled by the :data:`tephi.MIXING_RATIO_TEXT` dictionary:

   >>> pprint(tephi.MIXING_RATIO_TEXT)
   {'clip_on': True, 'color': 'green', 'ha': 'right', 'size': 8, 'va': 'bottom'}

This is a dictionary of *key* and *value* pairs that are passed through as keyword arguments to :func:`matplotlib.pyplot.text`.

Updating the ``MIXING_RATIO_TEXT`` dictionary will change the default behaviour of how the text of associated humidity mixing ratio lines are plotted.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.MIXING_RATIO_TEXT.update({'color': 'purple', 'size': 12})
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.MIXING_RATIO_TEXT = {'color': 'green', 'va': 'bottom', 'ha': 'right', 'clip_on': True, 'size': 8}


Humidity mixing ratio line frequency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *frequency* at which humidity mixing ratio lines are plotted on the tephigram is controlled by the :data:`tephi.MIXING_RATIO_SPEC` list:

   >>> print(tephi.MIXING_RATIO_SPEC)
   [(1, 0.05), (2, 0.18), (4, 0.3), (8, 1.5)]

This :term:`line specification` is a sequence of one or more tuple pairs that contain a humidity mixing ratio :term:`line step` and a
:term:`zoom level`.

For example, ``(4, 0.3)`` states that every *fourth* humidity mixing ratio line will be plotted i.e. visible, when the :term:`zoom level`
is at or below ``0.3``.

The *overall range* of humidity mixing ratio levels that may be plotted is controlled by the :data:`tephi.MIXING_RATIOS` list:

   >>> print(tephi.MIXING_RATIOS)
   [0.001, 0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0, 44.0, 48.0, 52.0, 56.0, 60.0, 68.0, 80.0]

Note that, it is possible to control which *individual* humidity mixing ratio lines should be *fixed* i.e. **always** visible, via the :data:`tephi.MIXING_RATIO_FIXED` variable:

   >>> print(tephi.MIXING_RATIO_FIXED)
   None

By default, no humidity mixing ratio lines are fixed. To force humidity mixing ratio lines ``4.0`` g kg\ :sup:`-1`\  and ``6.0`` g kg\ :sup:`-1`\
always to be plotted independent of the :term:`zoom level`,

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tephi.MIXING_RATIO_FIXED = [4.0, 6.0]
   tpg = tephi.TephiAxes()
   tpg.plot(dews)
   plt.show()

.. plot::

   import tephi
   tephi.MIXING_RATIO_FIXED = None
