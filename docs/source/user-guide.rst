User Guide
==========

.. currentmodule:: nrrd

About the NRRD file format
--------------------------
NRRD stands for **N**\ early **R**\ aw **R**\ aster **D**\ ata and is a file format designed for scientific visualization and image processing involving N-dimensional data. It is a simple and flexible file format with a header containing information about the data that can be read by simply opening the NRRD file in a text editor. Many other file formats such as PNG, JPG, DICOM cannot be read with a simple text editor! In addition, the raw data can be stored in a NRRD file in a number of commonly known formats such as ASCII, gzip, bzip or even raw. The header information and data itself can be stored in the same file or separately. Another feature of the NRRD file format is the support of custom key/value pairs in the header to allow storing of user information not defined in the NRRD specification.

The general structure of the NRRD file format is as follows::

    NRRD<NRRD file version>
    # Complete NRRD file format specification at:
    # http://teem.sourceforge.net/nrrd/format.html
    <field>: <value>
    <field>: <value>
    ...
    <field>: <value>
    <custom field>:=<value>
    <custom field>:=<value>
    ...
    <custom field>:=<value>
    # Comments are identified with a # symbol

    <data here if stored in same file, otherwise stored in detached file>

As with most file formats, the file begins with a magic line that uniquely identifies the file as a NRRD file. Along with the magic line is a version that identifies what revision of the NRRD specification is used. As of today, the latest NRRD version is 5. Line comments can be specified by starting the line with a # symbol. Following the magic line is the header which is written in ASCII with the structure :code:`<field>: <value>` or :code:`<field>:=<value>` in the case of a custom field. The header is finished reading once a blank line has been read. If the data is stored in the same file (based on whether the header contains a datafile field), then the data will follow the header.

More information on the NRRD file format can be found `here <http://teem.sourceforge.net/nrrd/index.html>`_.

Header datatypes
----------------
There are 10 possible datatypes that a value can have in the header. Below are the valid datatypes along with the datatype they are parsed into in Python and examples of the datatypes.

int
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: <i>
:NRRD Example: 12
:Python Datatype: :class:`int`
:Python Example: 12

double
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: <d>
:NRRD Example: 3.14
:Python Datatype: :class:`float`
:Python Example: 3.14

string
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: <s>
:NRRD Example: test
:Python Datatype: :class:`str`
:Python Example: 'test'

int list
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: <i> <i> ... <i>
:NRRD Example: 1 2 3 4
:Python Datatype: :class:`numpy.ndarray` (1D, dtype=int)
:Python Example: np.array([1, 2, 3, 4])

double list
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: <d> <d> ... <d>
:NRRD Example: 1.2 2.3 3.4 4.5
:Python Datatype: :class:`numpy.ndarray` (1D, dtype=float)
:Python Example: np.array([1.2, 2.3, 3.4, 4.5])

string list
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: <s> <s> ... <s>
:NRRD Example: this is space separated
:Python Datatype: :class:`list` of :class:`str`
:Python Example: ['this', 'is', 'string', 'separated']

quoted string list
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: "<s>" "<s>" ... "<s>"
:NRRD Example: "one item" "two items" "three" "four"
:Python Datatype: :class:`list` of :class:`str`
:Python Example: ['one item', 'two items', 'three', 'four']

int vector
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: (<i>,<i>,...,<i>)
:NRRD Example: (1,2,3,4)
:Python Datatype: (N,) :class:`numpy.ndarray` of :class:`int`
:Python Example: np.array([1, 2, 3, 4])

pynrrd will correctly handle vectors with or without spaces between the comma-delimiter. Saving the NRRD file back will remove all spaces between the comma-delimiters.

double vector
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: (<d>,<d>,...,<d>)
:NRRD Example: (1.2,2.3,3.4,4.5)
:Python Datatype: (N,) :class:`numpy.ndarray` of :class:`float`
:Python Example: np.array([1.2, 2.3, 3.4, 4.5])

pynrrd will correctly handle vectors with or without spaces between the comma-delimiter. Saving the NRRD file back will remove all spaces between the comma-delimiters.

int matrix
~~~~~~~~~~
:NRRD Syntax: (<i>,<i>,...,<i>) (<i>,<i>,...,<i>) ... (<i>,<i>,...,<i>)
:NRRD Example: (1,0,0) (0,1,0) (0,0,1)
:Python Datatype: (M,N) :class:`numpy.ndarray` of :class:`int`
:Python Example: np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

All rows of the matrix are required, unlike that of the `double matrix`_. If some of the rows need to be 'none', then use a `double matrix`_ instead. The reason is that empty rows (i.e. containing 'none') are represented as a row of NaN's, and NaN's are only available for floating point numbers.

double matrix
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: (<d>,<d>,...,<d>) (<d>,<d>,...,<d>) ... (<d>,<d>,...,<d>)
:NRRD Example: (2.54, 1.3, 0.0) (3.14, 0.3, 3.3) none (0.05, -12.3, -3.3)
:Python Datatype: (M,N) :class:`numpy.ndarray` of :class:`float`
:Python Example: np.array([[2.54, 1.3, 0.0], [3.14, 0.3, 3.3], [np.nan, np.nan, np.nan], [0.0, -12.3, -3.3]])

This datatype has the added feature where rows can be defined as empty by setting the vector as :code:`none`. In the NRRD specification, instead of the row, the :code:`none` keyword is used in it's place. This is represented in the Python NumPy array as a row of all NaN's. An example use case for this optional row matrix is for the 'space directions' field where one row may be empty because it is not a domain type.

Supported Fields
----------------
A list of supported fields, according to the NRRD specification, and its corresponding datatype can be seen below. Each field has a link to the NRRD specification providing a detailed description of the field.

========================  ================
Field                     NRRD Datatype
========================  ================
dimension_                `int`_
type_                     `string`_
sizes_                    `int list`_
endian_                   `string`_
encoding_                 `string`_
`datafile or data file`_  `string`_
`lineskip or line skip`_  `int`_
`byteskip or byte skip`_  `int`_
content_                  `string`_
kinds_                    `string list`_
labels_                   `quoted string list`_
units_                    `quoted string list`_
min_                      `double`_
max_                      `double`_
spacings_                 `double list`_
thicknesses_              `double list`_
centerings_               `string list`_
`oldmin or old min`_      `double`_
`oldmax or old max`_      `double`_
`axismins or axis mins`_  `double list`_
`axismaxs or axis maxs`_  `double list`_
`sample units`_           `string`_
space_                    `string`_
`space dimension`_        `int`_
`space units`_            `quoted string list`_
`space directions`_       `double matrix`_
`space origin`_           `double vector`_
`measurement frame`_      `int matrix`_
========================  ================

.. _dimension: http://teem.sourceforge.net/nrrd/format.html#dimension
.. _type: http://teem.sourceforge.net/nrrd/format.html#type
.. _sizes: http://teem.sourceforge.net/nrrd/format.html#sizes
.. _endian: http://teem.sourceforge.net/nrrd/format.html#endian
.. _encoding: http://teem.sourceforge.net/nrrd/format.html#encoding
.. _datafile or data file: http://teem.sourceforge.net/nrrd/format.html#datafile
.. _lineskip or line skip: http://teem.sourceforge.net/nrrd/format.html#lineskip
.. _byteskip or byte skip: http://teem.sourceforge.net/nrrd/format.html#byteskip
.. _content: http://teem.sourceforge.net/nrrd/format.html#content
.. _kinds: http://teem.sourceforge.net/nrrd/format.html#kinds
.. _labels: http://teem.sourceforge.net/nrrd/format.html#labels
.. _units: http://teem.sourceforge.net/nrrd/format.html#units
.. _min: http://teem.sourceforge.net/nrrd/format.html#min
.. _max: http://teem.sourceforge.net/nrrd/format.html#max
.. _spacings: http://teem.sourceforge.net/nrrd/format.html#spacings
.. _thicknesses: http://teem.sourceforge.net/nrrd/format.html#thicknesses
.. _centerings: http://teem.sourceforge.net/nrrd/format.html#centers
.. _oldmin or old min: http://teem.sourceforge.net/nrrd/format.html#oldmin
.. _oldmax or old max: http://teem.sourceforge.net/nrrd/format.html#oldmax
.. _axismins or axis mins: http://teem.sourceforge.net/nrrd/format.html#axismins
.. _axismaxs or axis maxs: http://teem.sourceforge.net/nrrd/format.html#axismaxs
.. _sample units: http://teem.sourceforge.net/nrrd/format.html#sampleunits
.. _space: http://teem.sourceforge.net/nrrd/format.html#space
.. _space dimension: http://teem.sourceforge.net/nrrd/format.html#spacedimension
.. _space units: http://teem.sourceforge.net/nrrd/format.html#spaceunits
.. _space directions: http://teem.sourceforge.net/nrrd/format.html#spacedirections
.. _space origin: http://teem.sourceforge.net/nrrd/format.html#spaceorigin
.. _measurement frame: http://teem.sourceforge.net/nrrd/format.html#measurementframe

Reading NRRD files
------------------
There are three functions that are used to read NRRD files: :meth:`read`, :meth:`read_header`, and :meth:`read_data`. :meth:`read` is a convenience function that opens the specified filepath and calls :meth:`read_header` and :meth:`read_data` in succession to return the NRRD header and data.

Reading NRRD files using :meth:`read` or :meth:`read_data` will by default return arrays being indexed in Fortran-order, i.e array elements are accessed by `data[x, y, z]`. This differs from the C-order where array elements are accessed by `data[z, y, x]`, which is the more common order in Python and libraries (e.g. NumPy, scikit-image, PIL, OpenCV). The :obj:`index_order` parameter can be used to specify which index ordering should be used on the returned array ('C' or 'F'). The :obj:`index_order` parameter needs to be consistent with the parameter of same name in :meth:`write`.

The :meth:`read` and :meth:`read_header` methods accept an optional parameter :obj:`custom_field_map` for parsing custom field types not listed in `Supported Fields`_ of the header. It is a :class:`dict` where the key is the custom field name and the value is a string identifying datatype for the custom field. See `Header datatypes`_ for a list of supported datatypes.

The :meth:`read_data` will typically be called in conjunction with :meth:`read_header` because header information is required in order to read the data. The function returns a :class:`numpy.ndarray` of the data saved in the given NRRD file.

Some NRRD files, while prohibited by specification, may contain duplicated header fields causing an exception to be raised. Changing :data:`nrrd.reader.ALLOW_DUPLICATE_FIELD` to :obj:`True` will show a warning instead of an error while trying to read the file.

Writing NRRD files
------------------
Writing to NRRD files can be done with the function :meth:`write`. The :obj:`filename` parameter to the function specifies the absolute or relative filename to write the NRRD file. If the :obj:`filename` extension is .nhdr, then the :obj:`detached_header` parameter is set to true automatically. If the :obj:`detached_header` parameter is set to :obj:`True` and the :obj:`filename` ends in .nrrd, then the header file will have the same path and base name as the :obj:`filename` but with an extension of .nhdr. In all other cases, the header and data are saved in the same file.

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
