from typing_extensions import Literal

from nrrd._version import __version__
from nrrd.formatters import *
from nrrd.parsers import *
from nrrd.reader import read, read_data, read_header
from nrrd.types import NRRDFieldMap, NRRDFieldType, NRRDHeader
from nrrd.writer import write

# TODO Change to 'double vector list' in next major release
SPACE_DIRECTIONS_TYPE: Literal['double matrix', 'double vector list'] = 'double matrix'
"""Datatype to use for 'space directions' field when reading/writing NRRD files

The 'space directions' field can be represented in two different ways: as a matrix or as a list of vectors. Per the
NRRD specification, the 'space directions' field is a per-axis definition that represents the direction and spacing of
each axis. Non-spatial axes are represented as 'none'.

The current default is to return a matrix, where each non-spatial axis is represented as a row of `NaN` in the matrix.
In the next major release, this default option will change to return a list of optional vectors, where each non
spatial axis is represented as `None`.

Example:
    Reading a NRRD file with space directions type set to 'double matrix' (the default).

    >>> nrrd.SPACE_DIRECTIONS_TYPE = 'double matrix'
    >>> data, header = nrrd.read('file.nrrd')
    >>> print(header['space directions'])
    [[1.5 0.  0. ]
     [0.  1.5 0. ]
     [0.  0.  1. ]
     [nan nan nan]]

    Reading a NRRD file with space directions type set to 'double vector list'.

    >>> nrrd.SPACE_DIRECTIONS_TYPE = 'double vector list'
    >>> data, header = nrrd.read('file.nrrd')
    >>> print(header['space directions'])
    [array([1.5, 0. , 0. ]), array([0. , 1.5, 0. ]), array([0., 0., 1.]), None]
"""

__all__ = ['read', 'read_data', 'read_header', 'write', 'format_number_list', 'format_number', 'format_matrix',
           'format_optional_matrix', 'format_optional_vector', 'format_vector', 'format_vector_list',
           'format_optional_vector_list', 'parse_matrix', 'parse_number_auto_dtype', 'parse_number_list',
           'parse_optional_matrix',
           'parse_optional_vector', 'parse_vector', 'parse_vector_list', 'parse_optional_vector_list', 'NRRDFieldType',
           'NRRDFieldMap', 'NRRDHeader', 'SPACE_DIRECTIONS_TYPE', '__version__']
