Getting Started
===============

.. currentmodule:: nrrd

Dependencies
------------

TODO Put requirements here instead?

In v1.0+, Python 3.7 or above is required for this module. If you need this library for an older version of Python, please install a the v0.x release instead.

* `Numpy <https://numpy.org/>`_
* nptyping
* typing_extensions

Installation
------------

Install via pip and PyPi repository (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: bash

    pip install pynrrd

Reading NRRD files
------------------
There are three functions that are used to read NRRD files: :meth:`read`, :meth:`read_header`, and :meth:`read_data`. :meth:`read` is a convenience function that opens the specified filepath and calls :meth:`read_header` and :meth:`read_data` in succession to return the NRRD header and data.

Reading NRRD files using :meth:`read` or :meth:`read_data` will by default return arrays being indexed in Fortran-order, i.e array elements are accessed by `data[x, y, z]`. This differs from the C-order where array elements are accessed by `data[z, y, x]`, which is the more common order in Python and libraries (e.g. NumPy, scikit-image, PIL, OpenCV). The :obj:`index_order` parameter can be used to specify which index ordering should be used on the returned array ('C' or 'F'). The :obj:`index_order` parameter needs to be consistent with the parameter of same name in :meth:`write`.

The :meth:`read` and :meth:`read_header` methods accept an optional parameter :obj:`custom_field_map` for parsing custom field types not listed in `Supported Fields`_ of the header. It is a :class:`dict` where the key is the custom field name and the value is a string identifying datatype for the custom field. See `Header datatypes`_ for a list of supported datatypes.

The :meth:`read_data` will typically be called in conjunction with :meth:`read_header` because header information is required in order to read the data. The function returns a :class:`numpy.ndarray` of the data saved in the given NRRD file.

Some NRRD files, while prohibited by specification, may contain duplicated header fields causing an exception to be raised. Changing :data:`nrrd.reader.ALLOW_DUPLICATE_FIELD` to :obj:`True` will show a warning instead of an error while trying to read the file.

Writing NRRD files
------------------
Writing to NRRD files can be done with the function :meth:`write`. The :obj:`filename` parameter specifies either an absolute or relative filename to write the NRRD file to. If the :obj:`filename` extension is .nhdr, then :obj:`detached_header` will be set to true automatically. If :obj:`detached_header` is :obj:`True` and :obj:`filename` extension is .nrrd, then the header file will have the same path and base name as :obj:`filename` but with an extension of .nhdr. In all other cases, the header and data are saved in the same file.

The :obj:`data` parameter is a :class:`numpy.ndarray` of data to be saved. :obj:`header` is an optional parameter of type :class:`dict` containing the field/values to be saved to the NRRD file.

Writing NRRD files will by default index the :obj:`data` array in Fortran-order where array elements are accessed by `data[x, y, z]`. This differs from C-order where array elements are accessed by `data[z, y, x]`, which is the more common order in Python and libraries (e.g. NumPy, scikit-image, PIL, OpenCV). The :obj:`index_order` parameter can be used to specify which index ordering should be used for the given :obj:`data` array ('C' or 'F').

.. note::

    The following fields are automatically generated based on the :obj:`data` parameter ignoring these values in the :obj:`header`: 'type', 'endian', 'dimension', 'sizes'.

.. note::

    The default encoding field used if not specified in :obj:`header` is 'gzip'.

.. note::

    The :obj:`index_order` parameter must be consistent with the index order specified in :meth:`read`. Reading an NRRD file in C-order and then writing as Fortran-order or vice versa will result in the data being transposed in the NRRD file.

Index Ordering
--------------
NRRD stores the image elements in `row-major ordering <https://en.wikipedia.org/wiki/Row-_and_column-major_order>`_ where the row can be seen as the fastest-varying axis. The header fields of NRRD that describes the axes are always specified in the order from fastest-varying to slowest-varying, i.e., `sizes` will be equal to `(# rows, # columns)`. This is also applicable to images of higher dimensions.

Both the reading and writing functions in pynrrd include an :obj:`index_order` parameter that is used to specify whether the returned data array should be in C-order ('C') or Fortran-order ('F').

Fortran-order is where the dimensions of the multi-dimensional data is ordered from fastest-varying to slowest-varying, i.e. in the same order as the header fields. So for a 3D set of data, the dimensions would be ordered `(x, y, z)`.

On the other hand, C-order is where the dimensions of the multi-dimensional data is ordered from slowest-varying to fastest-varying. So for a 3D set of data, the dimensions would be ordered `(z, y, x)`.

C-order is the index order used in Python and many Python libraries (e.g. NumPy, scikit-image, PIL, OpenCV). pynrrd recommends using C-order indexing to be consistent with the Python community. However, as of this time, the default indexing is Fortran-order to maintain backwards compatibility. In the future, the default index order will be switched to C-order.

.. note::

    Converting from one index order to the other is done via transposing the data.

.. note::

    All header fields are specified in Fortran order, per the NRRD specification, regardless of the index order. For example, a C-ordered array with shape (60, 800, 600) would have a sizes field of (600, 800, 60).

Example reading and writing NRRD files with C-order indexing
------------------------------------------------------------
.. code-block:: python

    import numpy as np
    import nrrd

    # Treat this data array as a 3D volume using C-order indexing
    # This means we have a volume with a shape of 600x800x70 (x by y by z)
    data = np.zeros((70, 800, 600))
    # Save the NRRD object with the correct index order
    nrrd.write('output.nrrd', data, index_order='C')

    # Read the NRRD file with C-order indexing
    # Note: We can specify either index order here, this is just a preference unlike in nrrd.write where
    # it MUST be set based on the data setup
    data, header = nrrd.read('output.nrrd', index_order='C')

    # The data shape is exactly the same shape as what we wrote
    print(data.shape)
    >>> (70, 800, 600)

    # But the shape saved in the header is in Fortran-order
    print(header['sizes'])
    >>> [600 800  70]

    # Read the NRRD file with Fortran-order indexing now
    data, header = nrrd.read('output.nrrd', index_order='F')

    # The data shape is exactly the same shape as what we wrote
    # The data shape is now in Fortran order, or transposed from what we wrote
    print(data.shape)
    >>> (600, 800, 70)
    print(header['sizes'])
    >>> [600 800  70]
