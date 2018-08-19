# encoding: utf-8
import bz2
import os
import re
import zlib
from collections import OrderedDict

from nrrd.parsers import *

# Reading and writing gzipped data directly gives problems when the uncompressed
# data is larger than 4GB (2^32). Therefore we'll read and write the data in
# chunks. How this affects speed and/or memory usage is something to be analyzed
# further. The following two values define the size of the chunks.
_READ_CHUNKSIZE = 2 ** 20

# TODO: Go through and reformat code

_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']

_TYPEMAP_NRRD2NUMPY = {
    'signed char': 'i1',
    'int8': 'i1',
    'int8_t': 'i1',
    'uchar': 'u1',
    'unsigned char': 'u1',
    'uint8': 'u1',
    'uint8_t': 'u1',
    'short': 'i2',
    'short int': 'i2',
    'signed short': 'i2',
    'signed short int': 'i2',
    'int16': 'i2',
    'int16_t': 'i2',
    'ushort': 'u2',
    'unsigned short': 'u2',
    'unsigned short int': 'u2',
    'uint16': 'u2',
    'uint16_t': 'u2',
    'int': 'i4',
    'signed int': 'i4',
    'int32': 'i4',
    'int32_t': 'i4',
    'uint': 'u4',
    'unsigned int': 'u4',
    'uint32': 'u4',
    'uint32_t': 'u4',
    'longlong': 'i8',
    'long long': 'i8',
    'long long int': 'i8',
    'signed long long': 'i8',
    'signed long long int': 'i8',
    'int64': 'i8',
    'int64_t': 'i8',
    'ulonglong': 'u8',
    'unsigned long long': 'u8',
    'unsigned long long int': 'u8',
    'uint64': 'u8',
    'uint64_t': 'u8',
    'float': 'f4',
    'double': 'f8',
    'block': 'V'
}


def _get_field_type(field, custom_field_map):
    if field in ['dimension', 'lineskip', 'line skip', 'byteskip', 'byte skip', 'space dimension']:
        return 'int'
    elif field in ['min', 'max', 'oldmin', 'old min', 'oldmax', 'old max']:
        return 'double'
    elif field in ['endian', 'encoding', 'content', 'sample units', 'datafile', 'data file', 'space', 'type']:
        return 'string'
    elif field in ['sizes']:
        return 'int list'
    elif field in ['spacings', 'thicknesses', 'axismins', 'axis mins', 'axismaxs', 'axis maxs']:
        return 'double list'
    elif field in ['kinds', 'labels', 'units', 'space units', 'centerings']:
        return 'string list'
    elif field in []:
        return 'int vector'
    elif field in ['space origin']:
        return 'double vector'
    elif field in ['measurement frame']:
        return 'int matrix'
    elif field in ['space directions']:
        return 'double matrix'
    else:
        if custom_field_map and field in custom_field_map:
            return custom_field_map[field]

        # Default the type to string if unknown type
        return 'string'


def _parse_field_value(value, field_type):
    if field_type == 'int':
        return int(value)
    elif field_type == 'double':
        return float(value)
    elif field_type == 'string':
        return str(value)
    elif field_type == 'int list':
        return parse_number_list(value, dtype=int)
    elif field_type == 'double list':
        return parse_number_list(value, dtype=float)
    elif field_type == 'string list':
        # TODO Handle cases where quotation marks are around the items
        return [str(x) for x in value.split()]
    elif field_type == 'int vector':
        return parse_vector(value, dtype=int)
    elif field_type == 'double vector':
        return parse_vector(value, dtype=float)
    elif field_type == 'int matrix':
        return parse_matrix(value, dtype=int)
    elif field_type == 'double matrix':
        # For matrices of double type, parse as an optional matrix to allow for rows of the matrix to be none
        # This is only valid for double matrices because the matrix is represented with NaN in the entire row
        # for none rows. NaN is only valid for floating point numbers
        return parse_optional_matrix(value)
    else:
        raise NRRDError('Invalid field type given: %s' % field_type)


def _determine_datatype(fields):
    """Determine the numpy dtype of the data."""

    # Convert the NRRD type string identifier into a NumPy string identifier using a map
    np_typestring = _TYPEMAP_NRRD2NUMPY[fields['type']]

    # This is only added if the datatype has more than one byte and is not using ASCII encoding
    # Note: Endian is not required for ASCII encoding
    if np.dtype(np_typestring).itemsize > 1 and fields['encoding'] not in ['ASCII', 'ascii', 'text', 'txt']:
        if 'endian' not in fields:
            raise NRRDError('Header is missing required field: "endian".')
        elif fields['endian'] == 'big':
            np_typestring = '>' + np_typestring
        elif fields['endian'] == 'little':
            np_typestring = '<' + np_typestring

    return np.dtype(np_typestring)


def _validate_magic_line(line):
    """For NRRD files, the first four characters are always "NRRD", and
    remaining characters give information about the file format version

    >>> _validate_magic_line('NRRD0005')
    8
    >>> _validate_magic_line('NRRD0006')
    Traceback (most recent call last):
        ...
    NrrdError: NRRD file version too new for this library.
    >>> _validate_magic_line('NRRD')
    Traceback (most recent call last):
        ...
    NrrdError: Invalid NRRD magic line: NRRD
    """

    if not line.startswith('NRRD'):
        raise NRRDError('Invalid NRRD magic line. Is this an NRRD file?')

    try:
        version = int(line[4:])
        if version > 5:
            raise NRRDError('Unsupported NRRD file version (version: %i). This library only supports v%i and below.'
                            % (version, 5))
    except ValueError:
        raise NRRDError('Invalid NRRD magic line: %s' % (line,))

    return len(line)


def read_header(file, custom_field_map=None):
    """Parse the fields in the NRRD header

    nrrdfile can be any object which supports the iterator protocol and
    returns a string each time its next() method is called — file objects and
    list objects are both suitable. If nrrdfile is a file object, it must be
    opened with the ‘b’ flag on platforms where that makes a difference
    (e.g. Windows)

    >>> read_header(("NRRD0005", "type: float", "dimension: 3"))
    {u'type': 'float', u'dimension': 3, u'keyvaluepairs': {}}
    >>> read_header(("NRRD0005", "my extra info:=my : colon-separated : values"))
    {u'keyvaluepairs': {u'my extra info': u'my : colon-separated : values'}}

    Option custom field map can be specified for custom key/value pairs that should be parsed into a specific datatype.
    The field map is a dictionary with the key being the field name and the value being a string identifying the
    datatype. Valid datatype strings are:
     Datatype        Example Syntax in NRRD File
    -------------------------------------------
    int             5
    double          2.5
    string          testing
    int list        1 2 3 4 5
    double list     1.2 2.0 3.1 4.7 5.0
    string list     first second third
    int vector      (1,0,0)
    double vector   (3.14,3.14,6.28)
    int matrix      (1,0,0) (0,1,0) (0,0,1)
    double matrix   (1.2,0.3,0) (0,1.5,0) (0,-0.55,1.6)
    """

    # If the file is a filename rather than the file handle, then open the file and call this function again with the
    # file handle. Since read function uses a filename, it is easy to think read_header is the same syntax.
    if isinstance(file, str) and file.count('\n') == 0:
        with open(file, 'rb') as fh:
            header = read_header(fh, custom_field_map)
            return header

    # Collect number of bytes in the file header (for seeking below)
    header_size = 0

    # Get iterator for the file and extract the first line, the magic line
    it = iter(file)
    magic_line = next(it)

    # Depending on what type file is, decoding may or may not be necessary. Decode if necessary, otherwise skip.
    need_decode = False
    if hasattr(magic_line, 'decode'):
        need_decode = True
        magic_line = magic_line.decode('ascii', 'ignore')

    # Validate the magic line and increment header size by size of the line
    header_size += _validate_magic_line(magic_line)

    # Create empty header
    # This is an OrderedDict rather than an ordinary dict because an OrderedDict will keep it's order that key/values
    # are added for when looping back through it. The added benefit of this is that saving the header will save the
    # fields in the same order.
    header = OrderedDict()

    # Loop through each line
    for line in it:
        header_size += len(line)
        if need_decode:
            line = line.decode('ascii', 'ignore')

        # Trailing whitespace ignored per the NRRD spec
        line = line.rstrip()

        # Skip comments starting with # (no leading whitespace is allowed)
        # Or, stop reading the header once a blank line is encountered. This separates header from data.
        if line.startswith('#'):
            continue
        elif line == '':
            break

        # Read the field and value from the line, split using regex to search for := or : delimiter
        field, value = re.split(r':=?', line, 1)

        # Remove whitespace before and after the field and value
        field, value = field.strip(), value.strip()

        # Check if the field has been added already
        if field in header.keys():
            raise NRRDError('Duplicate header field: %s' % repr(field))

        # Get the datatype of the field based on it's field name and custom field map
        field_type = _get_field_type(field, custom_field_map)

        # Parse the field value using the datatype retrieved
        # Place it in the header dictionary
        header[field] = _parse_field_value(value, field_type)

    # Reading the file line by line is buffered and so the header is not in the correct position for reading data if
    # the file contains the data in it as well. The solution is to set the file pointer to just behind the header.
    if hasattr(file, 'seek'):
        file.seek(header_size)

    return header


def read_data(header, fh, filename=None):
    """Read the NRRD data from a file object into a numpy structure.

    File handle is is assumed to point to the first byte of the data. That is,
    in case of an attached header, assumed to point to the first byte after the
    '\n\n' line.
    """

    # Check that the required fields are in the header
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in header:
            raise NRRDError('Header is missing required field: "%s".' % field)

    if header['dimension'] != len(header['sizes']):
        raise NRRDError('Number of elements in sizes does not match dimension')

    # Determine the data type from the header
    dtype = _determine_datatype(header)

    # determine byte skip, line skip, and data file (there are two ways to write them)
    lineskip = header.get('lineskip', header.get('line skip', 0))
    byteskip = header.get('byteskip', header.get('byte skip', 0))
    datafile = header.get('datafile', header.get('data file', None))
    datafilehandle = fh
    if datafile is not None:
        # If the datafile path is absolute, don't muck with it. Otherwise
        # treat the path as relative to the directory in which the detached
        # header is in
        if os.path.isabs(datafile):
            datafilename = datafile
        else:
            datafilename = os.path.join(os.path.dirname(filename), datafile)
        datafilehandle = open(datafilename, 'rb')

    num_pixels = np.array(header['sizes']).prod()
    # Seek to start of data based on lineskip/byteskip. byteskip == -1 is
    # only valid for raw encoding and overrides any lineskip
    if header['encoding'] == 'raw' and byteskip == -1:
        datafilehandle.seek(-dtype.itemsize * num_pixels, 2)
    else:
        for _ in range(lineskip):
            datafilehandle.readline()

    if header['encoding'] == 'raw':
        datafilehandle.seek(byteskip, os.SEEK_CUR)
        data = np.fromfile(datafilehandle, dtype)
    elif header['encoding'] in ['ASCII', 'ascii', 'text', 'txt']:
        datafilehandle.seek(byteskip, os.SEEK_CUR)
        data = np.fromfile(datafilehandle, dtype, sep=' ')
    else:
        # Probably the data is compressed then
        if header['encoding'] == 'gzip' or \
                header['encoding'] == 'gz':
            decompobj = zlib.decompressobj(zlib.MAX_WBITS | 16)
        elif header['encoding'] == 'bzip2' or \
                header['encoding'] == 'bz2':
            decompobj = bz2.BZ2Decompressor()
        else:
            raise NRRDError('Unsupported encoding: "%s"' % header['encoding'])

        decompressed_data = b''
        while True:
            chunk = datafilehandle.read(_READ_CHUNKSIZE)
            if not chunk:
                break
            decompressed_data += decompobj.decompress(chunk)
        # byteskip applies to the _decompressed_ byte stream
        data = np.frombuffer(decompressed_data[byteskip:], dtype)

    if datafilehandle:
        datafilehandle.close()

    if num_pixels != data.size:
        raise NRRDError('ERROR: {0}-{1}={2}'.format(num_pixels, data.size, num_pixels - data.size))

    # dkh : eliminated need to reverse order of dimensions. NRRD's
    # data layout is same as what numpy calls 'Fortran' order,
    shape_tmp = list(header['sizes'])
    data = np.reshape(data, tuple(shape_tmp), order='F')
    return data


def read(filename, custom_field_map=None):
    """Read a NRRD file and return a tuple (data, header)."""
    with open(filename, 'rb') as fh:
        header = read_header(fh, custom_field_map)
        data = read_data(header, fh, filename)
        return data, header
