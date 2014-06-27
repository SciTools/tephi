.. _tephi.transforms:

================
tephi.transforms
================


   
.. currentmodule:: tephi

.. automodule:: tephi.transforms

In this module:

 * :py:obj:`pressure_mixing_ratio_to_temperature`
 * :py:obj:`pressure_temperature_to_temperature_theta`
 * :py:obj:`pressure_theta_to_pressure_temperature`
 * :py:obj:`temperature_theta_to_pressure_temperature`
 * :py:obj:`temperature_theta_to_xy`
 * :py:obj:`xy_to_temperature_theta`
 * :py:obj:`TephiTransform`
 * :py:obj:`TephiTransformInverted`


----------

.. autofunction:: tephi.transforms.pressure_mixing_ratio_to_temperature

----------

.. autofunction:: tephi.transforms.pressure_temperature_to_temperature_theta

----------

.. autofunction:: tephi.transforms.pressure_theta_to_pressure_temperature

----------

.. autofunction:: tephi.transforms.temperature_theta_to_pressure_temperature

----------

.. autofunction:: tephi.transforms.temperature_theta_to_xy

----------

.. autofunction:: tephi.transforms.xy_to_temperature_theta

----------

Tephigram transformation to convert from temperature and
potential temperature to native plotting device coordinates.

..

    .. autoclass:: tephi.transforms.TephiTransform
        :members:
        :undoc-members:

----------

Tephigram inverse transformation to convert from native
plotting device coordinates to tephigram temperature and
potential temperature.

..

    .. autoclass:: tephi.transforms.TephiTransformInverted
        :members:
        :undoc-members:

