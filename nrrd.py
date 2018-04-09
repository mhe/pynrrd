#!/usr/bin/env python
# encoding: utf-8
"""
nrrd.py
An all-python (and numpy) implementation for reading and writing nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Copyright (c) 2011-2017 Maarten Everts and others. See LICENSE and AUTHORS.

"""

import bz2
import os
import zlib
from datetime import datetime

import numpy as np

# Reading and writing gzipped data directly gives problems when the uncompressed
# data is larger than 4GB (2^32). Therefore we'll read and write the data in
# chunks. How this affects speed and/or memory usage is something to be analyzed
# further. The following two values define the size of the chunks.
_READ_CHUNKSIZE = 2 ** 20
_WRITE_CHUNKSIZE = 2 ** 20


class NrrdError(Exception):
    """Exceptions for Nrrd class."""
    pass


def parse_vector(x, dtype=None):
    """Parse NRRD vector from string into Numpy array.

    Function parses NRRD vector from string into an 1D Numpy array.
    A NRRD vector is structured as follows:
        * (<Number 1>, <Number 2>, <Number 3>, ... <Number N>)

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD vector to convert to Numpy array
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be float, int or None. If dtype is None, then it
        will be automatically determined by checking any of the vector elements for fractional numbers. If found, then
        the vector will be converted to float datatype, otherwise the datatype will be int. Valid datatypes are float
        or int. Default is to automatically determine datatype.

    Returns
    -------
    vector : (N,) :class:`numpy.ndarray`
        Vector that is parsed from the :obj:`x` string
    """

    if x[0] != '(' or x[-1] != ')':
        raise NrrdError('Vector should be enclosed by parentheses.')

    # Always convert to float and then truncate to integer if desired
    # The reason why is parsing a floating point string to int will fail (i.e. int('25.1') will fail)
    vector = np.array([float(x) for x in x[1:-1].split(',')])

    # If using automatic datatype detection, then start by converting to float and determining if the number is whole
    # Truncate to integer if dtype is int also
    if dtype is None:
        vector_trunc = vector.astype(int)

        if np.all((vector - vector_trunc) == 0):
            vector = vector_trunc
    elif dtype == int:
        vector = vector.astype(int)
    elif dtype != float:
        raise NrrdError('dtype should be None for automatic type detection, float or int')

    return vector


def parse_optional_vector(x, dtype=None):
    """Parse optional NRRD vector from string into Numpy array.

    Function parses optional NRRD vector from string into an 1D Numpy array. This function works the same as
    :meth:`parse_vector` except if the :obj:`x` is 'none', the result will be None

    Thus, an optional NRRD vector is structured as one of the following:
        * (<Number 1>, <Number 2>, <Number 3>, ... <Number N>) OR
        * none

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD vector to convert to Numpy array
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be float, int or None. If dtype is None, then it
        will be automatically determined by checking any of the vector elements for fractional numbers. If found, then
        the vector will be converted to float datatype, otherwise the datatype will be int. Valid datatypes are float
        or int. Default is to automatically determine datatype.

    Returns
    -------
    vector : (N,) :class:`numpy.ndarray`
        Vector that is parsed from the :obj:`x` string OR None if :obj:`x` is 'none'
    """
    if x == 'none':
        return None
    else:
        return parse_vector(x, dtype)


def parse_matrix(x, dtype=None):
    """Parse NRRD matrix from string into Numpy array.

    Function parses NRRD matrix from string into an 2D Numpy array.
    A NRRD matrix is structured as follows:
        * (<Number 1>, <Number 2>, <Number 3>, ... <Number N>) (<Number 1>, <Number 2>, <Number 3>, ... <Number N>)

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD matrix to convert to Numpy array
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be float, int or None. If dtype is None, then it
        will be automatically determined by checking any of the matrix elements for fractional numbers. If found, then
        the matrix will be converted to float datatype, otherwise the datatype will be int. Valid datatypes are float
        or int. Default is to automatically determine datatype.

    Returns
    -------
    matrix : (M,N) :class:`numpy.ndarray`
        Matrix that is parsed from the :obj:`x` string
    """

    # Split input by spaces, convert each row into a vector and stack them vertically to get a matrix
    matrix = [parse_vector(x, dtype=float) for x in x.split()]

    # Get the size of each row vector and then remove duplicate sizes
    # There should be exactly one value in the matrix because all row sizes need to be the same
    if len(np.unique([len(x) for x in matrix])) != 1:
        raise NrrdError('Matrix should have same number of elements in each row')

    matrix = np.vstack(matrix)

    # If using automatic datatype detection, then start by converting to float and determining if the number is whole
    # Truncate to integer if dtype is int also
    if dtype is None:
        matrix_trunc = matrix.astype(int)

        if np.all((matrix - matrix_trunc) == 0):
            matrix = matrix_trunc
    elif dtype == int:
        matrix = matrix.astype(int)
    elif dtype != float:
        raise NrrdError('dtype should be None for automatic type detection, float or int')

    return matrix


def parse_optional_matrix(x):
    # Split input by spaces to get each row and convert into a vector. The row can be 'none', in which case it will
    # return None
    matrix = [parse_optional_vector(x, dtype=float) for x in x.split()]

    # Get the size of each row vector, 0 if None
    sizes = np.array([0 if x is None else len(x) for x in matrix])

    # Get sizes of each row vector removing duplicate sizes
    # Since each row vector should be same size, the unique sizes should return one value for the row size or it may
    # return a second one (0) if there are None vectors
    unique_sizes = np.unique(sizes)

    if len(unique_sizes) != 1 and (len(unique_sizes) != 2 or unique_sizes.min() != 0):
        raise NrrdError('Matrix should have same number of elements in each row')

    # Create a vector row of NaN's that matches same size of remaining vector rows
    # Stack the vector rows together to create matrix
    nan_row = np.full((unique_sizes.max()), np.nan)
    matrix = np.vstack([nan_row if x is None else x for x in matrix])

    return matrix


def parse_number_list(x, dtype=None):
    # Always convert to float and then perform truncation to integer if necessary
    number_list = np.array([float(x) for x in x.split()])

    if dtype is None:
        number_list_trunc = number_list.astype(int)

        if np.all((number_list - number_list_trunc) == 0):
            number_list = number_list_trunc
    elif dtype == int:
        number_list = number_list.astype(int)
    elif dtype != float:
        raise NrrdError('dtype should be None for automatic type detection, float or int')

    return number_list


def parse_number_auto_dtype(x):
    value = float(x)

    if value.is_integer():
        value = int(value)

    return value


def format_vector(x):
    return '(' + ','.join([format_number(y) for y in x]) + ')'


def format_optional_vector(x):
    # If vector is None or all elements are NaN, then return none
    # Otherwise format the vector as normal
    if x is None or np.all(np.isnan(x)):
        return 'none'
    else:
        return format_vector(x)


def format_matrix(x):
    return ' '.join([format_vector(y) for y in x])


def format_optional_matrix(x):
    return ' '.join([format_optional_vector(y) for y in x])


def format_number_list(x):
    return ' '.join([format_number(y) for y in x])


def format_number(x):
    if isinstance(x, float):
        # Helps prevent loss of precision as using str() in Python 2 only prints 12 digits of precision.
        # However, IEEE754-1985 standard says that 17 significant decimal digits is required to adequately represent a
        # floating point number.
        # The g option is used rather than f because g precision uses significant digits while f is just the number of
        # digits after the decimal. (NRRD C implementation uses g).
        value = '{:.17g}'.format(x)
    else:
        value = str(x)

    return value


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

_TYPEMAP_NUMPY2NRRD = {
    'i1': 'int8',
    'u1': 'uint8',
    'i2': 'int16',
    'u2': 'uint16',
    'i4': 'int32',
    'u4': 'uint32',
    'i8': 'int64',
    'u8': 'uint64',
    'f4': 'float',
    'f8': 'double',
    'V': 'block'
}

_NUMPY2NRRD_ENDIAN_MAP = {
    '<': 'little',
    'L': 'little',
    '>': 'big',
    'B': 'big'
}

_NRRD_FIELD_PARSERS = {
    'dimension': int,
    'type': str,
    'sizes': lambda fieldValue: parse_number_list(fieldValue, dtype=int),
    'endian': str,
    'encoding': str,
    'min': float,
    'max': float,
    'oldmin': float,
    'old min': float,
    'oldmax': float,
    'old max': float,
    'lineskip': int,
    'line skip': int,
    'byteskip': int,
    'byte skip': int,
    'content': str,
    'sample units': str,
    'datafile': str,
    'data file': str,
    'spacings': lambda fieldValue: parse_number_list(fieldValue, dtype=float),
    'thicknesses': lambda fieldValue: parse_number_list(fieldValue, dtype=float),
    'axis mins': lambda fieldValue: parse_number_list(fieldValue, dtype=float),
    'axismins': lambda fieldValue: parse_number_list(fieldValue, dtype=float),
    'axis maxs': lambda fieldValue: parse_number_list(fieldValue, dtype=float),
    'axismaxs': lambda fieldValue: parse_number_list(fieldValue, dtype=float),
    'centerings': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'labels': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'units': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'kinds': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'space': str,
    'space dimension': int,
    'space units': lambda fieldValue: [str(x) for x in fieldValue.split()],
    'space origin': lambda fieldValue: parse_vector(fieldValue, dtype=float),
    'space directions': lambda fieldValue: parse_optional_matrix(fieldValue),
    'measurement frame': lambda fieldValue: parse_optional_matrix(fieldValue, dtype=int),
}

_NRRD_FIELD_FORMATTERS = {
    'dimension': format_number,
    'type': str,
    'sizes': format_number_list,
    'endian': str,
    'encoding': str,
    'min': format_number,
    'max': format_number,
    'oldmin': format_number,
    'old min': format_number,
    'oldmax': format_number,
    'old max': format_number,
    'lineskip': format_number,
    'line skip': format_number,
    'byteskip': format_number,
    'byte skip': format_number,
    'content': str,
    'sample units': str,
    'datafile': str,
    'data file': str,
    'spacings': format_number_list,
    'thicknesses': format_number_list,
    'axis mins': format_number_list,
    'axismins': format_number_list,
    'axis maxs': format_number_list,
    'axismaxs': format_number_list,
    'centerings': lambda fieldValue: ' '.join(fieldValue),
    'labels': lambda fieldValue: ' '.join(fieldValue),
    'units': lambda fieldValue: ' '.join(fieldValue),
    'kinds': lambda fieldValue: ' '.join(fieldValue),
    'space': str,
    'space dimension': format_number,
    'space units': format_number_list,
    'space origin': format_vector,
    'space directions': format_optional_matrix,
    'measurement frame': format_optional_matrix,
}

_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']

# The supported field values
_NRRD_FIELD_ORDER = [
    'type',
    'dimension',
    'space dimension',
    'space',
    'sizes',
    'space directions',
    'kinds',
    'endian',
    'encoding',
    'min',
    'max',
    'oldmin',
    'old min',
    'oldmax',
    'old max',
    'content',
    'sample units',
    'spacings',
    'thicknesses',
    'axis mins',
    'axismins',
    'axis maxs',
    'axismaxs',
    'centerings',
    'labels',
    'units',
    'space units',
    'space origin',
    'measurement frame',
    'data file']


def _determine_dtype(fields):
    """Determine the numpy dtype of the data."""
    # Check whether the required fields are there
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in fields:
            raise NrrdError('Nrrd header misses required field: "%s".' % (field))

    # Process the data type
    np_typestring = _TYPEMAP_NRRD2NUMPY[fields['type']]
    if np.dtype(np_typestring).itemsize > 1:
        if 'endian' not in fields:
            raise NrrdError('Nrrd header misses required field: "endian".')
        if fields['endian'] == 'big':
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
        raise NrrdError('Missing magic "NRRD" word. Is this an NRRD file?')
    try:
        if int(line[4:]) > 5:
            raise NrrdError('NRRD file version too new for this library.')
    except ValueError:
        raise NrrdError('Invalid NRRD magic line: %s' % (line,))
    return len(line)


def read_data(fields, filehandle, filename=None):
    """Read the NRRD data from a file object into a numpy structure.

    File handle is is assumed to point to the first byte of the data. That is,
    in case of an attached header, assumed to point to the first byte after the
    '\n\n' line.
    """
    data = np.zeros(0)
    # Determine the data type from the fields
    dtype = _determine_dtype(fields)
    # determine byte skip, line skip, and data file (there are two ways to write them)
    lineskip = fields.get('lineskip', fields.get('line skip', 0))
    byteskip = fields.get('byteskip', fields.get('byte skip', 0))
    datafile = fields.get('datafile', fields.get('data file', None))
    datafilehandle = filehandle
    if datafile is not None:
        # If the datafile path is absolute, don't muck with it. Otherwise
        # treat the path as relative to the directory in which the detached
        # header is in
        if os.path.isabs(datafile):
            datafilename = datafile
        else:
            datafilename = os.path.join(os.path.dirname(filename), datafile)
        datafilehandle = open(datafilename, 'rb')

    num_pixels = np.array(fields['sizes']).prod()
    # Seek to start of data based on lineskip/byteskip. byteskip == -1 is
    # only valid for raw encoding and overrides any lineskip
    if fields['encoding'] == 'raw' and byteskip == -1:
        datafilehandle.seek(-dtype.itemsize * num_pixels, 2)
    else:
        for _ in range(lineskip):
            datafilehandle.readline()

    if fields['encoding'] == 'raw':
        datafilehandle.seek(byteskip, os.SEEK_CUR)
        data = np.fromfile(datafilehandle, dtype)
    else:
        # Probably the data is compressed then
        if fields['encoding'] == 'gzip' or \
                fields['encoding'] == 'gz':
            decompobj = zlib.decompressobj(zlib.MAX_WBITS | 16)
        elif fields['encoding'] == 'bzip2' or \
                fields['encoding'] == 'bz2':
            decompobj = bz2.BZ2Decompressor()
        else:
            raise NrrdError('Unsupported encoding: "%s"' % fields['encoding'])

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
        raise NrrdError('ERROR: {0}-{1}={2}'.format(num_pixels, data.size, num_pixels - data.size))

    # dkh : eliminated need to reverse order of dimensions. nrrd's
    # data layout is same as what numpy calls 'Fortran' order,
    shape_tmp = list(fields['sizes'])
    data = np.reshape(data, tuple(shape_tmp), order='F')
    return data


def read_header(nrrdfile):
    """Parse the fields in the nrrd header

    nrrdfile can be any object which supports the iterator protocol and
    returns a string each time its next() method is called — file objects and
    list objects are both suitable. If nrrdfile is a file object, it must be
    opened with the ‘b’ flag on platforms where that makes a difference
    (e.g. Windows)

    >>> read_header(("NRRD0005", "type: float", "dimension: 3"))
    {u'type': 'float', u'dimension': 3, u'keyvaluepairs': {}}
    >>> read_header(("NRRD0005", "my extra info:=my : colon-separated : values"))
    {u'keyvaluepairs': {u'my extra info': u'my : colon-separated : values'}}
    """
    # Collect number of bytes in the file header (for seeking below)
    header_size = 0

    it = iter(nrrdfile)
    magic_line = next(it)

    need_decode = False
    if hasattr(magic_line, 'decode'):
        need_decode = True
        magic_line = magic_line.decode('ascii', 'ignore')

    header_size += _validate_magic_line(magic_line)

    header = {u'keyvaluepairs': {}}
    for raw_line in it:
        header_size += len(raw_line)
        if need_decode:
            raw_line = raw_line.decode('ascii', 'ignore')

        # Trailing whitespace ignored per the NRRD spec
        line = raw_line.rstrip()

        # Comments start with '#', no leading whitespace allowed
        if line.startswith('#'):
            continue
        # Single blank line separates the header from the data
        if line == '':
            break

        # Handle the <key>:=<value> lines first since <value> may contain a
        # ': ' which messes up the <field>: <desc> parsing
        key_value = line.split(':=', 1)
        if len(key_value) is 2:
            key, value = key_value
            # TODO: escape \\ and \n ??
            # value.replace(r'\\\\', r'\\').replace(r'\n', '\n')
            header[u'keyvaluepairs'][key] = value
            continue

        # Handle the "<field>: <desc>" lines.
        field_desc = line.split(': ', 1)
        if len(field_desc) is 2:
            field, desc = field_desc
            # Preceeding and suffixing white space should be ignored.
            field = field.rstrip().lstrip()
            desc = desc.rstrip().lstrip()
            if field not in _NRRD_FIELD_PARSERS:
                raise NrrdError('Unexpected field in nrrd header: %s' % repr(field))
            if field in header.keys():
                raise NrrdError('Duplicate header field: %s' % repr(field))
            header[field] = _NRRD_FIELD_PARSERS[field](desc)
            continue

        # Should not reach here
        raise NrrdError('Invalid header line: %s' % repr(line))

    # line reading was buffered; correct file pointer to just behind header:
    if hasattr(nrrdfile, 'seek'):
        nrrdfile.seek(header_size)

    return header


def read(filename):
    """Read a nrrd file and return a tuple (data, header)."""
    with open(filename, 'rb') as filehandle:
        header = read_header(filehandle)
        data = read_data(header, filehandle, filename)
        return (data, header)


def _write_data(data, filehandle, options):
    # Now write data directly
    rawdata = data.tostring(order='F')
    if options['encoding'] == 'raw':
        filehandle.write(rawdata)
    else:
        if options['encoding'] == 'gzip':
            comp_obj = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        elif options['encoding'] == 'bzip2':
            comp_obj = bz2.BZ2Compressor()
        else:
            raise NrrdError('Unsupported encoding: "%s"' % options['encoding'])

        # write data in chunks
        start_index = 0
        while start_index < len(rawdata):
            end_index = start_index + _WRITE_CHUNKSIZE
            if end_index > len(rawdata):
                end_index = len(rawdata)
            filehandle.write(comp_obj.compress(rawdata[start_index:end_index]))
            start_index = end_index
        filehandle.write(comp_obj.flush())
        filehandle.flush()


def write(filename, data, options={}, detached_header=False):
    """Write the numpy data to a nrrd file. The nrrd header values to use are
    inferred from from the data. Additional options can be passed in the
    options dictionary. See the read() function for the structure of this
    dictionary.

    To set data samplings, use e.g. `options['spacings'] = [s1, s2, s3]` for
    3d data with sampling deltas `s1`, `s2`, and `s3` in each dimension.

    """
    # Infer a number of fields from the ndarray and ignore values
    # in the options dictionary.
    options['type'] = _TYPEMAP_NUMPY2NRRD[data.dtype.str[1:]]
    if data.dtype.itemsize > 1:
        options['endian'] = _NUMPY2NRRD_ENDIAN_MAP[data.dtype.str[:1]]
    # if 'space' is specified 'space dimension' can not. See
    # http://teem.sourceforge.net/nrrd/format.html#space
    if 'space' in options.keys() and 'space dimension' in options.keys():
        del options['space dimension']
    options['dimension'] = data.ndim
    options['sizes'] = list(data.shape)

    # The default encoding is 'gzip'
    if 'encoding' not in options:
        options['encoding'] = 'gzip'

    # A bit of magic in handling options here.
    # If *.nhdr filename provided, this overrides `detached_header=False`
    # If *.nrrd filename provided AND detached_header=True, separate header
    #   and data files written.
    # For all other cases, header & data written to same file.
    if filename[-5:] == '.nhdr':
        detached_header = True
        if 'data file' not in options:
            datafilename = filename[:-4] + str('raw')
            if options['encoding'] == 'gzip':
                datafilename += '.gz'
            options['data file'] = datafilename
        else:
            datafilename = options['data file']
    elif filename[-5:] == '.nrrd' and detached_header:
        datafilename = filename
        filename = filename[:-4] + str('nhdr')
    else:
        # Write header & data as one file
        datafilename = filename

    with open(filename, 'wb') as filehandle:
        filehandle.write(b'NRRD0005\n')
        filehandle.write(b'# This NRRD file was generated by pynrrd\n')
        filehandle.write(b'# on ' +
                         datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').encode('ascii') +
                         b'(GMT).\n')
        filehandle.write(b'# Complete NRRD file format specification at:\n')
        filehandle.write(b'# http://teem.sourceforge.net/nrrd/format.html\n')

        # Write the fields in order, this ignores fields not in
        # _NRRD_FIELD_ORDER
        for field in _NRRD_FIELD_ORDER:
            if field in options:
                outline = (field + ': ' +
                           _NRRD_FIELD_FORMATTERS[field](options[field]) +
                           '\n').encode('ascii')
                filehandle.write(outline)
        d = options.get('keyvaluepairs', {})
        for (key, value) in sorted(d.items(), key=lambda t: t[0]):
            outline = (str(key) + ':=' + str(value) + '\n').encode('ascii')
            filehandle.write(outline)

        # Write the closing extra newline
        filehandle.write(b'\n')

        # If a single file desired, write data
        if not detached_header:
            _write_data(data, filehandle, options)

    # If detached header desired, write data to different file
    if detached_header:
        with open(datafilename, 'wb') as datafilehandle:
            _write_data(data, datafilehandle, options)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
