from typing import Literal

from nrrd._version import __version__
from nrrd.formatters import *
from nrrd.parsers import *
from nrrd.reader import read, read_data, read_header
from nrrd.types import NRRDFieldMap, NRRDFieldType, NRRDHeader
from nrrd.writer import write

SPACE_DIRECTIONS_TYPE: Literal['double matrix', 'double vector list'] = 'double matrix'
"""Datatype to use for 'space directions' field when reading/writing NRRD files

TODO Addison

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
