.. tephigram_user_guide_customise:

Tephigram customisation
=======================

This section discusses how finer control of the tephigram isobars, saturated adiabats and humidity mixing ratio lines and text can be achieved.

.. testsetup::

   import tephi
   from pprint import pprint

There are two main methods to customise tephigram lines: default values, and individual values. Default values apply to
ALL axes by default, whereas individual values affect only the axes you change them on.

The default values of barbs, isobars, mixing ratios, isopleths and wet adiabats are stored in the
``constants.default`` dictionary. Changing these values will change the default behaviour of the tephigram.

Individual values can only be changed for the three adjustable isopleths (isobars, humidity mixing ratios, and wet
adiabats.

Barbs
-----
Barb defaults can be altered via the ``constants.default`` dictionary.

.. code:: python

    from tephi.constants import default

    default["barbs_gutter"]
    default["barbs_length"]
    default["barbs_linewidth"]
    default["barbs_zorder"]

Isopleths
---------

Defaults
^^^^^^^^

    >>> from tephi.constants import default

    >>> default["isobar_line"]
    >>> default["isobar_nbins"]
    >>> default["isobar_text"]
    >>> default["isobar_ticks"]

    >>> default["mixing_ratio_line"]
    >>> default["mixing_ratio_nbins"]
    >>> default["mixing_ratio_text"]
    >>> default["mixing_ratio_ticks"]

    >>> default["wet_adiabat_line"]
    >>> default["wet_adiabat_nbins"]
    >>> default["wet_adiabat_text"]
    >>> default["wet_adiabat_ticks"]

You can also change the default min and max axis measurement for each isopleth. These change
depending on the isopleth.

    >>> default["isobar_min_theta"]
    >>> default["isobar_max_theta"]

    >>> default["mixing_ratio_min_pressure"]
    >>> default["mixing_ratio_max_pressure"]

    >>> default["wet_adiabat_min_temperature"]
    >>> default["wet_adiabat_max_pressure"]


Individual
^^^^^^^^^^

If you wish to change the behaviour of the three additional gridlines (isobars, wet adiabats, humidity mixing ratios)
for a specific axes, you can edit the gridline artist properties.

.. code:: python

    from tephi import TephiAxes

    tephigram = TephiAxes()
    tephigram.add_isobars()
    tephigram.isobar

    from tephi import TephiAxes

    tephigram = TephiAxes()
    tephigram.add_wet_adiabats()
    tephigram.wet_adiabat

    from tephi import TephiAxes

    tephigram = TephiAxes()
    tephigram.add_mixing_ratios()
    tephigram.mixing_ratio

.. note::
    Currently, the only directly editable values are nbins, ticks, and the max\_ and min\_ values for the respective
    isopleth. Other values can be changed through the ``_kwargs`` dictionary, although this should be improved
    in the future.
    >>> tephigram.isobar._kwargs["line"]["color"] = "green"
