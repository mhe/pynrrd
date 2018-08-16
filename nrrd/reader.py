# encoding: utf-8
import bz2
import os
import zlib
import re

from nrrd.parsers import *

# Reading and writing gzipped data directly gives problems when the uncompressed
# data is larger than 4GB (2^32). Therefore we'll read and write the data in
# chunks. How this affects speed and/or memory usage is something to be analyzed
# further. The following two values define the size of the chunks.
_READ_CHUNKSIZE = 2 ** 20

# TODO: Allow support for custom parsers
# TODO: Need to think of solution for fields that are acceptable with and without spaces?
_NRRD_FIELD_TYPE = {
    'dimension': 'int',
    'type': str,
    'sizes': lambda fieldValue: parse_number_list(fieldValue, dtype=int),
    'endian': str,
    'encoding': lambda fieldValue: str(fieldValue).lower(),
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
    'measurement frame': lambda fieldValue: parse_optional_matrix(fieldValue),
}

_NRRD_FIELD_PARSERS = {
    'dimension': int,
    'type': str,
    'sizes': lambda fieldValue: parse_number_list(fieldValue, dtype=int),
    'endian': str,
    'encoding': lambda fieldValue: str(fieldValue).lower(),
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
    'measurement frame': lambda fieldValue: parse_optional_matrix(fieldValue),
}

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
    elif field in ['type']:
        return 'datatype'
    elif field in ['endian', 'encoding', 'content', 'sample units', 'datafile', 'data file', 'space']:
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
    elif field in ['measurement frame']:  # TODO Not sure there is any such thing as int matrix in this case?
        return 'int matrix'
    elif field in ['space directions']:
        return 'double matrix'
    else:
        if custom_field_map and field in custom_field_map:
            return custom_field_map[field]

        # Default the type to string if unknown type
        return 'string'


def _determine_dtype(fields):
    """Determine the numpy dtype of the data."""
    # Check whether the required fields are there
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in fields:
            raise NrrdError('Nrrd header misses required field: "%s".' % field)

    # Process the data type
    np_typestring = _TYPEMAP_NRRD2NUMPY[fields['type']]
    # Endianness is not necessary for ASCII encoding type
    if np.dtype(np_typestring).itemsize > 1 and fields['encoding'] not in ['ascii', 'text', 'txt']:
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
    elif fields['encoding'] in ['ascii', 'text', 'txt']:
        datafilehandle.seek(byteskip, os.SEEK_CUR)
        data = np.fromfile(datafilehandle, dtype, sep=' ')
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


def read_header(nrrdfile, custom_field_map=None):
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
    # Collect number of bytes in the file header (for seeking below)
    header_size = 0

    # TODO Handle custom field map here
    # Convert the strings into functions, then add to _NRRD_FIELD_PARSERS
    field_parsers = _NRRD_FIELD_PARSERS
    for field, datatype in custom_field_map.items():
        if field in field_parsers:
            pass
        if datatype == 'int':
            pass
        elif datatype == 'double':
            pass
        elif datatype == 'string':
            pass
        elif datatype == 'int':
            pass
        elif datatype == 'double':
            pass
        elif datatype == 'string':
            pass
        elif datatype == 'int':
            pass
        elif datatype == 'double':
            pass
        elif datatype == 'string':
            pass
        elif datatype == 'int':
            pass
        elif datatype == 'double':
            pass
        elif datatype == 'string':
            pass
        pass

    it = iter(nrrdfile)
    magic_line = next(it)

    need_decode = False
    if hasattr(magic_line, 'decode'):
        need_decode = True
        magic_line = magic_line.decode('ascii', 'ignore')

    header_size += _validate_magic_line(magic_line)
    header = {}

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

        # TODO: Handle key/value pairs and fields the same way
        # TODO: Upon saving, if field is not recognized, then save as key/value pair (:=)

        # Read the field and value from the line, split using regex to search for := or : delimeter
        field, value = re.split(r':=?', line, 1)

        # Remove whitespace before and after
        field, value = field.strip(), value.strip()

        if field not in _NRRD_FIELD_PARSERS:
            raise NrrdError('Unexpected field in nrrd header: %s' % repr(field))
        elif field in header.keys():
            raise NrrdError('Duplicate header field: %s' % repr(field))

        header[field] = _NRRD_FIELD_PARSERS[field](value)

    # line reading was buffered; correct file pointer to just behind header:
    if hasattr(nrrdfile, 'seek'):
        nrrdfile.seek(header_size)

    return header


def read(filename, custom_field_map=None):
    """Read a nrrd file and return a tuple (data, header)."""
    with open(filename, 'rb') as filehandle:
        header = read_header(filehandle, custom_field_map)
        data = read_data(header, filehandle, filename)
        return data, header
