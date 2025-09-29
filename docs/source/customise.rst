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
``constants.defaults`` dictionary. Changing these values will change the default behaviour of the tephigram.

Individual values can only be changed for the three adjustable isopleths (isobars, humidity mixing ratios, and wet
adiabats.

Barbs
-----
Barb defaults can be altered via the ``constants.defaults`` dictionary.

from tephi.constants import defaults
defaults["barbs_gutter"]
defaults["barbs_length"]
defaults["barbs_linewidth"]
defaults["barbs_zorder"]

Isopleths
---------

Defaults
^^^^^^^^
.. note::
    "<isopleth>" can be replaced by any of "isobar", "mixing_ratio" and "wet_adiabat", to change the
    respective isopleth defaults.

from tephi.constants import defaults
defaults["<isopleth>_line"]
defaults["<isopleth>_nbins"]
defaults["<isopleth>_text"]
defaults["<isopleth>_ticks"]
defaults["<isopleth>_min_<axis_measurement>"]
defaults["<isopleth>_max_<axis_measurement>"]

Individual
^^^^^^^^^^

If you wish to change the behaviour of the three additional gridlines (isobars, wet adiabats, humidity mixing ratios)
for a specific axes, you can edit the gridline artist properties.

tephigram = TephiAxes()
tephigram.add_<isopleth>()
tephigram.<isopleth>

.. note::
    Currently, the only directly editable values are nbins, ticks, and the max\_ and min\_ values for the respective.
    isopleth. Other values can be changed through the ``_kwarg`` dictionary, although this should be improved
    in the future.
