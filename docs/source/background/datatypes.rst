Header datatypes
================

.. currentmodule:: nrrd

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
:Python Example: ['this', 'is', 'space', 'separated']

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

int vector list
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: (<i>,<i>,...,<i>) (<i>,<i>,...,<i>) ... (<i>,<i>,...,<i>)
:NRRD Example: (1,0,0) (0,1,0) none (0,0,1)
:Python Datatype: :class:`list` of (N,) :class:`numpy.ndarray` of :class:`int`
:Python Example: [np.array([1, 0, 0]), np.array([0, 1, 0]), None, np.array([0, 0, 1])]

This datatype is similar to `int matrix`_ except instead of returning a (M,N) :class:`numpy.ndarray`, it returns a list of (N,) :class:`numpy.ndarray`. Each row is optional and designated by :code:`none` in the NRRD specification and represented as :obj:`None` in this library.

double vector list
~~~~~~~~~~~~~~~~~~
:NRRD Syntax: (<d>,<d>,...,<d>) (<d>,<d>,...,<d>) ... (<d>,<d>,...,<d>)
:NRRD Example: (2.54, 1.3, 0.0) (3.14, 0.3, 3.3) none (0.05, -12.3, -3.3)
:Python Datatype: :class:`list` of (N,) :class:`numpy.ndarray` of :class:`float`
:Python Example: [np.array([2.54, 1.3, 0.0]), np.array([3.14, 0.3, 3.3]), None, np.array([0.0, -12.3, -3.3])]

This datatype is similar to `double matrix`_ except instead of returning a (M,N) :class:`numpy.ndarray`, it returns a list of (N,) :class:`numpy.ndarray`. Each row is optional and designated by :code:`none` in the NRRD specification and represented as :obj:`None` in this library.