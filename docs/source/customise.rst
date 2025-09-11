.. tephigram_user_guide_customise:

Tephigram customisation
=======================

This section discusses how finer control of the tephigram isobars, saturated adiabats and humidity mixing ratio lines and text can be achieved.

.. testsetup::

   import tephi
   from pprint import pprint


Defaults
--------

The default values of barbs, isobars, mixing ratios, isopleths and wet adiabats are stored in the
`constants.defaults` dictionary. Changing these values will change the default behaviour of the tephigram.

barbs_gutter
barbs_length
barbs_linewidth
barbs_zorder

isobar_line
isobar_min_theta
isobar_max_theta
isobar_nbins
isobar_text
isobar_ticks

isopleth_picker
isopleth_zorder

mixing_ratio_line
mixing_ratio_text
mixing_ratio_min_pressure
mixing_ratio_max_pressure
mixing_ratio_nbins
mixing_ratio_ticks

wet_adiabat_line
wet_adiabat_min_temperature
wet_adiabat_max_pressure
wet_adiabat_nbins
wet_adiabat_text
wet_adiabat_ticks

Individual
----------

If you wish to change the behaviour of the three additional gridlines (isobars, wet adiabats, humidity mixing ratios)
for a specific axes, you can edit the gridline artist properties. Currently, you can only change some of these
values.
