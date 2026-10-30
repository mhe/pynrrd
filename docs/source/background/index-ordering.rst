Index Ordering
==============

.. currentmodule:: nrrd

In NRRD, the header fields that describe the axes (`sizes`, `space directions`, etc.) are always specified in the order from fastest-varying to slowest-varying in the raw data. This is the same convention as Fortran (column-major) array indexing. For a typical 2D image where pixels along a scanline are stored contiguously, the first axis is the horizontal (column/x) axis, so `sizes` will be equal to `(# columns, # rows)`, i.e. `(width, height)`. For example, a 640x480 RGB image would have `sizes: 3 640 480`. This is also applicable to images of higher dimensions.

Both the reading and writing functions in pynrrd include an :obj:`index_order` parameter that is used to specify whether the returned data array should be in C-order ('C') or Fortran-order ('F').

Fortran-order is where the dimensions of the multi-dimensional data is ordered from fastest-varying to slowest-varying, i.e. in the same order as the header fields. So for a 3D set of data, the dimensions would be ordered `(x, y, z)`.

On the other hand, C-order is where the dimensions of the multi-dimensional data is ordered from slowest-varying to fastest-varying. So for a 3D set of data, the dimensions would be ordered `(z, y, x)`.

C-order is the index order used in Python and many Python libraries (e.g. NumPy, scikit-image, PIL, OpenCV). pynrrd recommends using C-order indexing to be consistent with the Python community. However, as of this time, the default indexing is Fortran-order to maintain backwards compatibility. In the future, the default index order will be switched to C-order.

.. note::

    Converting from one index order to the other is done via transposing the data.

.. note::

    All header fields are specified in Fortran order, per the NRRD specification, regardless of the index order. For example, a C-ordered array with shape (60, 800, 600) would have a sizes field of (600, 800, 60).
