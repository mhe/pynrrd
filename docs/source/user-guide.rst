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
    <custom field>:= <value>
    <custom field>:= <value>
    ...
    <custom field>:= <value>
    # Comments are identified with a pound sign

    <data here if stored in same file, otherwise stored in detached file>

As with most file formats, the file begins with a magic line that uniquely identifies the file as a NRRD file. Along with the magic line is a version that identifies what revision of the NRRD specification is used. As of today, the latest NRRD version is 5. Line comments can be specified by starting the line with a # symbol. Following the magic line is the header which is written in ASCII with the structure <field>: <value> or <field>:= <value> in the case of a custom field. The header is finished reading once a blank line has been read. If the data is stored in the same file (based on whether the header contains a datafile field), then the data will follow the header.

More information on the NRRD file format can be found `here <http://teem.sourceforge.net/nrrd/index.html>`_.

Header datatypes
----------------
There are 10 possible datatypes that a value can have in the header. Below are the valid datatypes along with the datatype they are parsed into in Python and examples of the datatypes.

int
~~~~~~~~~~~~~
:NRRD Syntax: <i>
:NRRD Example: 12
:Python Datatype: :class:`int`
:Python Example: 12

double
~~~~~~~~~~~~~
:NRRD Syntax: <d>
:NRRD Example: 3.14
:Python Datatype: :class:`float`
:Python Example: 3.14

string
~~~~~~~~~~~~~
:NRRD Syntax: <s>
:NRRD Example: test
:Python Datatype: :class:`str`
:Python Example: 'test'

int list
~~~~~~~~~~~~~
:NRRD Syntax: <i> <i> ... <i>
:NRRD Example: 1 2 3 4
:Python Datatype: :class:`numpy.ndarray` (1D, dtype=int)
:Python Example: np.array([1, 2, 3, 4])

double list
~~~~~~~~~~~~~
:NRRD Syntax: <d> <d> ... <d>
:NRRD Example: 1.2 2.3 3.4 4.5
:Python Datatype: :class:`numpy.ndarray` (1D, dtype=float)
:Python Example: np.array([1.2, 2.3, 3.4, 4.5])

string list
~~~~~~~~~~~~~
:NRRD Syntax: <s> <s> ... <s>
:NRRD Example: this is space separated
:Python Datatype: :class:`list` of :class:`str`
:Python Example: ['this', 'is', 'string', 'separated']

A limitation to the string list is that any strings containing a space in them will be incorrectly separated. In the future, escaping the space could be a useful technique to prevent unwanted separation.

A few fields that are string lists in the NRRD specification are defined with a syntax where there are quotation marks around the strings along with the space delimeter (e.g. "<s>" "<s>" ... "<s>"). The fields that use this style are 'space units', 'units' and 'labels'. The quotation marks seem to be optional but currently they are not handled by the pynrrd library.

int vector
~~~~~~~~~~~~~
:NRRD Syntax: (<i>,<i>,...,<i>)
:NRRD Example: (1,2,3,4)
:Python Datatype: (N,) :class:`numpy.ndarray` of :class:`int`
:Python Example: np.array([1, 2, 3, 4])

The NRRD specification does not explicitly state that spaces are allowed in the comma delineated vector, such as (1, 2, 3, 4). However, the pynrrd library does correctly parse any vectors that contain spaces after the commas. When saving the NRRD file back, the spaces will be removed from the vector.

double vector
~~~~~~~~~~~~~
:NRRD Syntax: (<d>,<d>,...,<d>)
:NRRD Example: (1.2,2.3,3.4,4.5)
:Python Datatype: (N,) :class:`numpy.ndarray` of :class:`float`
:Python Example: np.array([1.2, 2.3, 3.4, 4.5])

The NRRD specification does not explicitly state that spaces are allowed in the comma delineated vector, such as (1, 2, 3, 4). However, the pynrrd library does correctly parse any vectors that contain spaces after the commas. When saving the NRRD file back, the spaces will be removed from the vector.

int matrix
~~~~~~~~~~
:NRRD Syntax: (<i>,<i>,...,<i>) (<i>,<i>,...,<i>) ... (<i>,<i>,...,<i>)
:NRRD Example: (1,0,0) (0,1,0) (0,0,1)
:Python Datatype: (M,N) :class:`numpy.ndarray` of :class:`int`
:Python Example: np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

All rows of the matrix are required, unlike that of the `double matrix`_. If some of the rows need to be 'none', then please use a `double matrix`_ instead. The reason is that empty rows (contain 'none') are represented as a row of NaN's and NaN's are only available for floating point numbers.

double matrix
~~~~~~~~~~~~~
:NRRD Syntax: (<d>,<d>,...,<d>) (<d>,<d>,...,<d>) ... (<d>,<d>,...,<d>)
:NRRD Example: (2.54, 1.3, 0.0) (3.14, 0.3, 3.3) none (0.05, -12.3, -3.3)
:Python Datatype: (M,N) :class:`numpy.ndarray` of :class:`float`
:Python Example: np.array([[2.54, 1.3, 0.0], [3.14, 0.3, 3.3], [np.nan, np.nan, np.nan], [0.0, -12.3, -3.3]])

This datatype has the additional feature where certain rows can be defined as empty or none. In the NRRD specification, instead of the row, the 'none' keyword is used in it's place. This is represented in the Python NumPy array as a row of all NaN's (NaN's are only defined for floating point numbers). An example use case for this optional row matrix is for the 'space directions' field where one row may be empty because it is not a domain type. 

Supported Fields
----------------
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
labels_                   `string list`_
units_                    `string list`_
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
`space units`_            `string list`_
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
There are three functions that are used to read NRRD files: :meth:`read`, :meth:`read_header` and :meth:`read_data`. :meth:`read` is a convenience function that opens the file located at :obj:`filename` and calls :meth:`read_header` and :meth:`read_data` in succession and returns the data and header.

Reading NRRD files using :meth:`read` or :meth:`read_data` will by default return arrays being indexed in Fortran order, i.e array elements are accessed by `data[x,y,z]`. This differs to the C-order, i.e. `data[z,y,x]`, which is more common in numpy. The :obj:`index_order` parameter can be used to specify which index ordering should be used on the returned array ('C' or 'F'). The :obj:`index_order` parameter needs to be consistent with the parameter of same name in :meth:`write`.

The :meth:`read` and :meth:`read_header` methods accept an optional parameter :obj:`custom_field_map` for parsing custom field types not listed in `Supported Fields`_ of the header. It is a :class:`dict` where the key is the custom field name and the value is a string identifying datatype for the custom field. See `Header datatypes`_ for a list of supported datatypes.

The :obj:`file` parameter of :meth:`read_header` accepts a filename or a string iterator object to read the header from. If a filename is specified, then the file will be opened and closed after the header is read from it. If not specifying a filename, the :obj:`file` parameter can be any sort of iterator that returns a string each time :meth:`next` is called. The two common objects that meet these requirements are file objects and a list of strings. The :meth:`read_header` function returns a :class:`dict` with the field and parsed values as keys and values to the dictionary.

The :meth:`read_data` will not typically be used besides within the :meth:`read` function because the header is a required parameter (:obj:`header`) to this function. The remaining two parameters :obj:`fh` and :obj:`filename` are optional depending on the parameters but it never hurts to specify both. The file handle (:obj:`fh`) is necessary if the header contains the NRRD data as well (AKA it is not a detached file). However, if the NRRD data is detached from the header, then the :obj:`filename` parameter is required to obtain the absolute path to the data file. The :meth:`read_data` function returns a :class:`numpy.ndarray` of the data.

Some NRRD files, while prohibited by specification, may contain duplicated reader fields preventing the proper reading of the file. Changing :data:`nrrd.reader.ALLOW_DUPLICATE_FIELD` to :obj:`True` will show a warning instead of an error while trying to read the file.

Writing NRRD files
------------------
Writing to NRRD files can be done with the single function :meth:`write`. The :obj:`filename` parameter to the function specifies the absolute or relative filename to write the NRRD file. If the :obj:`filename` extension is .nhdr, then the :obj:`detached_header` parameter is set to true automatically. If the :obj:`detached_header` parameter is set to :obj:`True` and the :obj:`filename` ends in .nrrd, then the header file will have the same path and base name as the :obj:`filename` but with an extension of .nhdr. In all other cases, the header and data are saved in the same file.

The :obj:`data` parameter is a :class:`numpy.ndarray` of data to be saved. :obj:`header` is an optional parameter of type :class:`dict` containing the field/values to be saved to the NRRD file. :obj:`index_order` specifies the index order of the array :obj:`data`, this should be consistent with the argument of the same name in :meth:`read`.

.. note::

    The following fields are automatically generated based on the :obj:`data` parameter ignoring these values in the :obj:`header`: 'type', 'endian', 'dimension', 'sizes'.

.. note::

    The default encoding field used if not specified in :obj:`header` is 'gzip'.

.. note::

    The :obj:`index_order` parameter must be consistent with the index order specified in :meth:`read`. Reading an NRRD file in C-order and then writing as Fortran-order or vice versa will result in the data being transposed in the NRRD file.
