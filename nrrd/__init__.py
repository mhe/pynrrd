from typing import Literal

from nrrd._version import __version__
from nrrd.formatters import *
from nrrd.parsers import *
from nrrd.reader import read, read_data, read_header
from nrrd.types import NRRDFieldMap, NRRDFieldType, NRRDHeader
from nrrd.writer import write

# TODO Change to 'double vector list' in next major release
SPACE_DIRECTIONS_TYPE: Literal['double matrix', 'double vector list'] = 'double matrix'
"""Datatype to use for 'space directions' field when reading/writing NRRD files

TODO Addison
The 'space directions' field can be represented in two different ways: as a matrix or as a list of vectors.

The current default is to use a matrix, but it will be switched to a list of vectors in the next major release.

The space directions field is defined per-axis where any of the axis can be 'none'. A matrix gives the false impression the s

The default is to use a matrix, but it can be set to use a list of vectors by setting this variable to
:obj:`'double vector list'`. This is mostly useful for backwards compatibility with older versions of the `nrrd` library
which only supported the list of vectors representation.

Example:
    >>> nrrd.SPACE_DIRECTIONS_TYPE = 'double vector list'
    >>> nrrd.write('output.nrrd', data, {'space directions': [np.array([1.5, 0., 0.])]}, index_order='F')


When there are duplicated fields in a NRRD file header, pynrrd throws an error by default. Setting this field as
:obj:`True` will instead show a warning.

Example:
    Reading a NRRD file with duplicated header field 'space' with field set to :obj:`False`.

    >>> filedata, fileheader = nrrd.read('filename_duplicatedheader.nrrd')
    nrrd.errors.NRRDError: Duplicate header field: 'space'

    Set the field as :obj:`True` to receive a warning instead.

    >>> nrrd.reader.ALLOW_DUPLICATE_FIELD = True
    >>> filedata, fileheader = nrrd.read('filename_duplicatedheader.nrrd')
    UserWarning: Duplicate header field: 'space' warnings.warn(dup_message)
"""

__all__ = ['read', 'read_data', 'read_header', 'write', 'format_number_list', 'format_number', 'format_matrix',
           'format_optional_matrix', 'format_optional_vector', 'format_vector', 'format_vector_list',
           'format_optional_vector_list', 'parse_matrix', 'parse_number_auto_dtype', 'parse_number_list',
           'parse_optional_matrix',
           'parse_optional_vector', 'parse_vector', 'parse_vector_list', 'parse_optional_vector_list', 'NRRDFieldType',
           'NRRDFieldMap', 'NRRDHeader', 'SPACE_DIRECTIONS_TYPE', '__version__']
