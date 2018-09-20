# encoding: utf-8
import bz2
import os
import re
import zlib
import warnings
from collections import OrderedDict

from nrrd.parsers import *

# Reading and writing gzipped data directly gives problems when the uncompressed
# data is larger than 4GB (2^32). Therefore we'll read and write the data in
# chunks. How this affects speed and/or memory usage is something to be analyzed
# further. The following two values define the size of the chunks.
_READ_CHUNKSIZE = 2 ** 20

_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']

# Duplicated fields are prohibited by the spec, but do occur in the wild.
# Set True to allow duplicate fields, with a warning.
ALLOW_DUPLICATE_FIELD = False

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
    """Read contents of header and parse values from :obj:`file`

    :obj:`file` can be a filename indicating where the NRRD header is located or a string iterator object. If a
    filename is specified, then the file will be opened and closed after the header is read from it. If not specifying
    a filename, the :obj:`file` parameter can be any sort of iterator that returns a string each time :meth:`next` is
    called. The two common objects that meet these requirements are file objects and a list of strings. When
    :obj:`file` is a file object, it must be opened with the binary flag ('b') on platforms where that makes a
    difference, such as Windows.

    See :ref:`user-guide:Reading NRRD files` for more information on reading NRRD files.

    Parameters
    ----------
    file : :class:`str` or string iterator
        Filename, file object or string iterator object to read NRRD header from
    custom_field_map : :class:`dict` (:class:`str`, :class:`str`), optional
        Dictionary used for parsing custom field types where the key is the custom field name and the value is a
        string identifying datatype for the custom field.

    Returns
    -------
    header : :class:`dict` (:class:`str`, :obj:`Object`)
        Dictionary containing the header fields and their corresponding parsed value

    See Also
    --------
    :meth:`read`, :meth:`read_data`
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
            dup_message = "Duplicate header field: '%s'" % str(field)

            if not ALLOW_DUPLICATE_FIELD:
                raise NRRDError(dup_message)

            warnings.warn(dup_message)

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


def read_data(header, fh=None, filename=None):
    """Read data from file into :class:`numpy.ndarray`

    The two parameters :obj:`fh` and :obj:`filename` are optional depending on the parameters but it never hurts to
    specify both. The file handle (:obj:`fh`) is necessary if the header is attached with the NRRD data. However, if
    the NRRD data is detached from the header, then the :obj:`filename` parameter is required to obtain the absolute
    path to the data file.

    See :ref:`user-guide:Reading NRRD files` for more information on reading NRRD files.

    Parameters
    ----------
    header : :class:`dict` (:class:`str`, :obj:`Object`)
        Parsed fields/values obtained from :meth:`read_header` function
    fh : file-object, optional
        File object pointing to first byte of data. Only necessary if data is attached to header.
    filename : :class:`str`, optional
        Filename of the header file. Only necessary if data is detached from the header. This is used to get the
        absolute data path.

    Returns
    -------
    data : :class:`numpy.ndarray`
        Data read from NRRD file

    See Also
    --------
    :meth:`read`, :meth:`read_header`
    """

    # Check that the required fields are in the header
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in header:
            raise NRRDError('Header is missing required field: "%s".' % field)

    if header['dimension'] != len(header['sizes']):
        raise NRRDError('Number of elements in sizes does not match dimension')

    # Determine the data type from the header
    dtype = _determine_datatype(header)

    # Determine the byte skip, line skip and the data file
    # These all can be written with or without the space according to the NRRD spec, so we check them both
    line_skip = header.get('lineskip', header.get('line skip', 0))
    byte_skip = header.get('byteskip', header.get('byte skip', 0))
    data_filename = header.get('datafile', header.get('data file', None))

    # If the data file is separate from the header file, then open the data file to read from that instead
    if data_filename is not None:
        # If the pathname is relative, then append the current directory from the filename
        if not os.path.isabs(data_filename):
            if filename is None:
                raise NRRDError('Filename parameter must be specified when a relative data file path is given')

            data_filename = os.path.join(os.path.dirname(filename), data_filename)

        # Override the fh parameter with the data filename
        fh = open(data_filename, 'rb')

    # Get the total number of data points by multiplying the size of each dimension together
    total_data_points = header['sizes'].prod()

    # If encoding is raw and byte skip is -1, then seek backwards to the data
    # Otherwise skip the number of lines requested
    if header['encoding'] == 'raw' and byte_skip == -1:
        fh.seek(-dtype.itemsize * total_data_points, 2)
    else:
        for _ in range(line_skip):
            fh.readline()

    # If a compression encoding is used, then byte skip AFTER decompressing
    if header['encoding'] == 'raw':
        # Skip the requested number of bytes and then parse the data using NumPy
        fh.seek(byte_skip, os.SEEK_CUR)
        data = np.fromfile(fh, dtype)
    elif header['encoding'] in ['ASCII', 'ascii', 'text', 'txt']:
        # Skip the requested number of bytes and then parse the data using NumPy
        fh.seek(byte_skip, os.SEEK_CUR)
        data = np.fromfile(fh, dtype, sep=' ')
    else:
        # Handle compressed data now
        # Construct the decompression object based on encoding
        if header['encoding'] in ['gzip', 'gz']:
            decompobj = zlib.decompressobj(zlib.MAX_WBITS | 16)
        elif header['encoding'] in ['bzip2', 'bz2']:
            decompobj = bz2.BZ2Decompressor()
        else:
            raise NRRDError('Unsupported encoding: "%s"' % header['encoding'])

        # Loop through the file and read a chunk at a time (see _READ_CHUNKSIZE why it is read in chunks)
        decompressed_data = b''
        while True:
            chunk = fh.read(_READ_CHUNKSIZE)

            # If chunk is None, then file is at end, break out of loop
            if not chunk:
                break

            # Decompress the data and add it to the decompressed data
            decompressed_data += decompobj.decompress(chunk)

        # Byte skip is applied AFTER the decompression. Skip first x bytes of the decompressed data and parse it using
        # NumPy
        data = np.fromstring(decompressed_data[byte_skip:], dtype)

    # Close the file
    # Even if opened using with keyword, closing it does not hurt
    fh.close()

    if total_data_points != data.size:
        raise NRRDError('Size of the data does not equal the product of all the dimensions: {0}-{1}={2}'
                        .format(total_data_points, data.size, total_data_points - data.size))

    # Eliminate need to reverse order of dimensions. NRRD's data layout is the same as what Numpy calls 'Fortran'
    # order, where the first index is the one that changes fastest and last index changes slowest
    data = np.reshape(data, tuple(header['sizes']), order='F')

    return data


def read(filename, custom_field_map=None):
    """Read a NRRD file and return the header and data

    See :ref:`user-guide:Reading NRRD files` for more information on reading NRRD files.

    Parameters
    ----------
    filename : :class:`str`
        Filename of the NRRD file
    custom_field_map : :class:`dict` (:class:`str`, :class:`str`), optional
        Dictionary used for parsing custom field types where the key is the custom field name and the value is a
        string identifying datatype for the custom field.

    Returns
    -------
    data : :class:`numpy.ndarray`
        Data read from NRRD file
    header : :class:`dict` (:class:`str`, :obj:`Object`)
        Dictionary containing the header fields and their corresponding parsed value

    See Also
    --------
    :meth:`write`, :meth:`read_header`, :meth:`read_data`
    """

    """Read a NRRD file and return a tuple (data, header)."""

    with open(filename, 'rb') as fh:
        header = read_header(fh, custom_field_map)
        data = read_data(header, fh, filename)

        return data, header
