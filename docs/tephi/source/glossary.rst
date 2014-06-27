.. tephigram_user_guide_glossary:

========
Glossary
========

.. glossary::
   :sorted:

   Anchor
      A sequence of two (pressure, temperature) pairs that specify the bottom left-hand corner and the
      top right-hand corner of the plot. The pressure data points must be in units of mb or hPa, and the 
      temperature data points must be in units of :sup:`o`\ C. 

   Dry adiabat
      A line of constant potential temperature, measured in units of :sup:`o`\ C. The zeroth dry adiabat line
      is an axis of the tephigram, see :ref:`intro-dry-adiabat`.

   Humidity mixing ratio
      A line of constant saturation mixing ratio with respect to a plane water surface, measured in g kg\ :sup:`-1`\ , see :ref:`intro-humidity-mixing-ratio`.

   Isobar
      A line of constant pressure, measured in millibars or hectopascals, see :ref:`intro-isobar`.

   Isotherm
      A line of constant temperature, measured in :sup:`o`\ C. The zeroth isotherm line is an axis of the tephigram,
      see :ref:`intro-isotherm`.
  
   Line specification
      A sequence of one or more tuple pairs containing a :term:`line step` value and a :term:`zoom level` value.
      Used to control the frequency at which the tephigram plots :term:`isobar` lines, :term:`humidity mixing ratio` lines,
      and :term:`saturated adiabat` lines. Note that, specifying a :term:`zoom level` of ``None`` forces the associated
      lines **always** to be visible. 

   Line step
      The first value in the tuple pair of a :term:`line specification`. An integer that denotes N\ :sup:`th`\  step multiples.
      i.e. a line step of ``25`` denotes all lines that are a multiple of 25, or every 25\ :sup:`th`\  item from an
      enumerated list of values.
 
   Pseudo saturated wet adiabat
      A line of constant equivalent potential temperature for saturated air parcels, measured in units of :sup:`o`\ C, see :ref:`intro-saturated-adiabat`.

   Saturated adiabat
      See :term:`pseudo saturated wet adiabat`.

   Zoom level
      An *inverted* zoom level fraction that is a ratio of current tephigram plot display width over the original plot display width.
