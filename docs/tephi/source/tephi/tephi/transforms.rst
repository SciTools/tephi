.. _tephi.transforms:

================
tephi.transforms
================


   
.. currentmodule:: tephi

.. automodule:: tephi.transforms

In this module:

 * :py:obj:`convert_Tt2pT`
 * :py:obj:`convert_Tt2xy`
 * :py:obj:`convert_pT2Tt`
 * :py:obj:`convert_pt2pT`
 * :py:obj:`convert_pw2T`
 * :py:obj:`convert_xy2Tt`
 * :py:obj:`TephiTransform`
 * :py:obj:`TephiTransformInverted`


----------

.. autofunction:: tephi.transforms.convert_Tt2pT

----------

.. autofunction:: tephi.transforms.convert_Tt2xy

----------

.. autofunction:: tephi.transforms.convert_pT2Tt

----------

.. autofunction:: tephi.transforms.convert_pt2pT

----------

.. autofunction:: tephi.transforms.convert_pw2T

----------

.. autofunction:: tephi.transforms.convert_xy2Tt

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

