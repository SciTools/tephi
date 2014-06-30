.. tephigram_user_guide_plotting:

Tephigram plotting
==================

This section describes how to visualise one or more data sets as a tephigram.

.. testsetup::

   import os.path
   import tephi
   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dry_bulb = os.path.join(tephi.DATA_DIR, 'temps.txt')
   winds = os.path.join(tephi.DATA_DIR, 'barbs.txt')
   dews, temps = tephi.loadtxt(dew_point, dry_bulb)


Tephigram data
--------------

Throughout this user guide we will make use of three data sets to plot temperature profiles on a tephigram.

Currently, the tephigram module can only plot data from ascii text files. 
These files may contain pressure, temperature, wind speed and wind direction data sets.
Here pressure is measured in units of *millibars* or *hectopascals*, 
temperature is measured in units of *degrees celsius*,
wind speed is measured in *knots* and wind direction is measured in *degrees from north*.

Note that the data set must consist of one or more pressure and temperature paired values, 
and optionally one wind speed and wind direction pair for each pressure value. 
Thus any temperature value must be paired with a pressure value, 
and wind speed and wind direction pairs must be paired with a pressure value.

Data from the text files is loaded into one :func:`collections.namedtuple` instance per text file. 
Each column of data representing a given phenomenon in a text file is loaded into a single named tuple. 
The name of each tuple is set using a list of strings passed to the loader. 
If not specified, the names default to *(pressure, temperature)*.

For our example tephigram data sets we have a 2-dimensional *dew-point* data set:

    >>> print dews
    tephidata(
        pressure=array([ 1006.,   924.,   900.,   850.,   800.,   755.,   710.,   700.,
             600.,   500.,   470.,   459.,   400.,   300.,   250.], dtype=float32)
        temperature=array([ 26.39999962,  20.29999924,  19.79999924,  14.5       ,
            12.89999962,   8.30000019,  -5.        ,  -5.0999999 ,
           -11.19999981,  -8.30000019, -12.10000038, -12.5       ,
           -32.90000153, -46.        , -53.        ], dtype=float32))

And a 2-dimensional *dry-bulb* data set, with each named tuple printed individually:

   >>> print temps.pressure
   [ 1006.   924.   900.   850.   800.   755.   710.   700.   600.   500.
      470.   459.   400.   300.   250.   210.   200.   186.   178.   159.
      151.   150.   129.   117.   107.   100.    82.    80.    60.    54.
       50.]

   >>> print temps.temperature
   [ 30.  22.  21.  18.  16.  12.  12.  11.   4.  -4.  -7.  -7. -13. -29. -38.
    -47. -51. -56. -57. -63. -63. -64. -69. -77. -79. -77. -78. -78. -72. -71.
    -69.]

A convenience function, as introduced above, has been provided to assist with loading one or more text files of pressure, temperature, wind speed and wind direction data; see :func:`tephi.loadtxt`. 
Here it is used to load the third example data set that contains four columns of data, being *pressure*, *temperature*, *wind speed* and *wind direction*::

    >>> import os.path
    >>> import tephi
    >>> winds = os.path.join(tephi.DATA_DIR, 'barbs.txt')
    >>> columns = ('pressure', 'dewpoint', 'wind_speed', 'wind_direction')
    >>> barbs = tephi.loadtxt(winds, column_titles=columns)
    >>> barbs
    tephidata(
        pressure=array([ 1006.,   924.,   900.,   850.,   800.,   755.,   710.,   700.,
             600.,   500.,   470.,   459.,   400.,   300.,   250.], dtype=float32)
        dewpoint=array([ 26.39999962,  20.29999924,  19.79999924,  14.5       ,
            12.89999962,   8.30000019,  -5.        ,  -5.0999999 ,
           -11.19999981,  -8.30000019, -12.10000038, -12.5       ,
           -32.90000153, -46.        , -53.        ], dtype=float32)
        wind_speed=array([  0.,   1.,   5.,   5.,   7.,  10.,  12.,  15.,  25.,  35.,  40.,
            43.,  45.,  50.,  55.], dtype=float32)
        wind_direction=array([   0.,   15.,   25.,   30.,   60.,   90.,  105.,  120.,  180.,
            240.,  270.,  285.,  300.,  330.,  359.], dtype=float32))

.. note::
   WMO upper-level pressure, temperature, humidity, and wind reports *FM 35-IX Ext. TEMP*, *FM 36-IX Ext. TEMP SHIP*, *FM 37-IX Ext. TEMP DROP* and 
   *FM 38-IX Ext. MOBIL* are currently **not** supported.


Plotting tephigram data
-----------------------

.. note::
   Tephigram *subplots* are currently **not** supported.


Plotting a single data set
^^^^^^^^^^^^^^^^^^^^^^^^^^

The temperature profile of a single tephigram data set can easily be plotted.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tpg = tephi.Tephigram()
   tpg.plot(dews)
   plt.show()


Plotting multiple data sets
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Plotting more than one data set is achieved by over-plotting each data set individually onto the tephigram.

.. plot::
   :include-source:
   :align: center

    import matplotlib.pyplot as plt
    import os.path

    import tephi

    dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
    dry_bulb = os.path.join(tephi.DATA_DIR, 'temps.txt')
    column_titles = [('pressure', 'dewpoint'), ('pressure', 'temperature')]
    dew_data, temp_data = tephi.loadtxt(dew_point, dry_bulb, column_titles=column_titles)
    dews = zip(dew_data.pressure, dew_data.dewpoint)
    temps = zip(temp_data.pressure, temp_data.temperature)

    tpg = tephi.Tephigram()
    tpg.plot(dews)
    tpg.plot(temps)
    plt.show()

Note that, by default the tephigram will automatically center the plot so that all temperature profiles are visible, also see :ref:`plot-anchor`.


Customising a temperature profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All keyword arguments passed to :meth:`tephi.Tephigram.plot` are simply passed through to :func:`matplotlib.pyplot.plot`.

This transparency allows full control when plotting a temperature profile on the tephigram. 

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tpg = tephi.Tephigram()
   tpg.plot(dews, label='Dew-point temperature', color='blue', linewidth=2, linestyle='--', marker='s')
   plt.show()


Tephigram axis ticks
^^^^^^^^^^^^^^^^^^^^

By default the *isotherm* and *dry adiabat* axis ticks are automatically located and scaled based on the tephigram plot and zoom level, which may be changed interactively.

However, fixed axis tick locations can easily be configured for either axis if required.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tpg = tephi.Tephigram(isotherm_locator=tephi.Locator(10), dry_adiabat_locator=tephi.Locator(20))
   tpg.plot(dews)
   plt.show()

The above may also be achieved without using a :class:`tephi.Locator`::

   tpg = tephi.Tephigram(isotherm_locator=10, dry_adiabat_locator=20)


.. _plot-anchor:

Anchoring a plot
^^^^^^^^^^^^^^^^

By default, the tephigram will automatically center the plot around all temperature profiles. This behaviour may not be desirable
when comparing separate tephigram plots against one another.

To fix the extent of a plot, simply specify an :term:`anchor` point to the tephigram.

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   import os.path

   import tephi

   dew_point = os.path.join(tephi.DATA_DIR, 'dews.txt')
   dew_data = tephi.loadtxt(dew_point, column_titles=('pressure', 'dewpoint'))
   dews = zip(dew_data.pressure, dew_data.dewpoint)
   tpg = tephi.Tephigram(anchor=[(1000, 0), (300, 0)])
   tpg.plot(dews)
   plt.show()


