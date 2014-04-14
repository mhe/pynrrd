#!/usr/bin/env python
# encoding: utf-8
"""
nrrd.py
An all-python (and numpy) implementation for reading and writing nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Copyright (c) 2011 Maarten Everts and David Hammond. See LICENSE.

"""

import numpy as np
import gzip
import bz2
import os.path
from datetime import datetime

class NrrdError(Exception):
    """Exceptions for Nrrd class."""
    pass

def _nrrd_read_header_lines(nrrdfile):
    """Read header lines from a .nrrd/.nhdr file."""
    line = nrrdfile.readline()
    if line[:-2] != 'NRRD000':
        raise NrrdError('Missing magic "NRRD" word, is this an NRRD file?')
    if line[-2] > '5':
        raise NrrdError('NRRD file version too new for this library.')
    headerlines = []
    while line != '\n' and line != '':
        headerlines.append(line)
        line = nrrdfile.readline()
    return headerlines

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

def parse_nrrdvector(inp):
    """Parse a vector from a nrrd header, return a list."""
    assert inp[0] == '(', "Vector should be enclosed by parenthesis."
    assert inp[-1] == ')', "Vector should be enclosed by parenthesis."
    return [float(x) for x in inp[1:-1].split(',')]

def parse_optional_nrrdvector(inp):
    """Parse a vector from a nrrd header that can also be none."""
    if (inp == "none"):
        return inp
    else:
        return parse_nrrdvector(inp)

_NRRD_FIELD_PARSERS = {
    'dimension': int,
    'type': str,
    'sizes': lambda fieldValue: [int(x) for x in fieldValue.split(' ')],
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
    'spacings': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'thicknesses': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axis mins': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axismins': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axis maxs': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axismaxs': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'centerings': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'labels': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'units': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'kinds': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'space': str,
    'space dimension': int,
    'space units': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'space origin': parse_nrrdvector,
    'space directions': lambda fieldValue:
                        [parse_optional_nrrdvector(x) for x in fieldValue.split(' ')],
    'measurement frame': lambda fieldValue:
                        [parse_nrrdvector(x) for x in fieldValue.split(' ')],
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
    'measurement frame']


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


def read_data(fields, filehandle, filename=None):
    """Read the actual data into a numpy structure."""
    data = np.zeros(0)
    # Determine the data type from the fields
    dtype = _determine_dtype(fields)
    # determine byte skip, line skip, and data file (there are two ways to write them)
    lineskip = fields.get('lineskip', fields.get('line skip', 0))
    byteskip = fields.get('byteskip', fields.get('byteskip', 0))
    datafile = fields.get("datafile", fields.get("data file", None))
    datafilehandle = filehandle
    if datafile is not None:
        # If the datafile path is absolute, don't muck with it. Otherwise
        # treat the path as relative to the directory in which the detached
        # header is in
        if os.path.isabs(datafile):
            datafilename = datafile
        else:
            datafilename = os.path.join(os.path.dirname(filename), datafile)
        datafilehandle = open(datafilename,'rb')
    totalbytes = dtype.itemsize *\
                    np.array(fields['sizes']).prod()
    if fields['encoding'] == 'raw':
        if byteskip == -1:
            datafilehandle.seek(-totalbytes, 2)
        else:
            for _ in range(lineskip):
                datafilehandle.readline()
            datafilehandle.read(byteskip)
        data = np.fromfile(datafilehandle, dtype)
    elif fields['encoding'] == 'gzip' or\
         fields['encoding'] == 'gz':
        gzipfile = gzip.GzipFile(fileobj=datafilehandle)
        # Again, unfortunately, np.fromfile does not support
        # reading from a gzip stream, so we'll do it like this.
        # I have no idea what the performance implications are.
        data = np.fromstring(gzipfile.read(), dtype)
    elif fields['encoding'] == 'bzip2' or\
         fields['encoding'] == 'bz2':
        bz2file = bz2.BZ2File(fileobj=datafilehandle)
        # Again, unfortunately, np.fromfile does not support
        # reading from a gzip stream, so we'll do it like this.
        # I have no idea what the performance implications are.
        data = np.fromstring(bz2file.read(), dtype)
    else:
        raise NrrdError('Unsupported encoding: "%s"' % fields['encoding'])
    # dkh : eliminated need to reverse order of dimensions. nrrd's
    # data layout is same as what numpy calls 'Fortran' order,
    shape_tmp = list(fields['sizes'])
    data = np.reshape(data, tuple(shape_tmp), order='F')
    return data

def _validate_magic_line(line):
    """For NRRD files, the first four characters are always "NRRD", and
    remaining characters give information about the file format version
    """
    if not line.startswith('NRRD'):
        raise NrrdError('Missing magic "NRRD" word. Is this an NRRD file?')
    try:
        if int(line[4:]) > 5:
            raise NrrdError('NRRD file version too new for this library.')
    except Value:
        raise NrrdError('Invalid NRRD magic line: %s' % (line,))
    return len(line)

def read_header(nrrdfile):
    """Parse the fields in the nrrd header

    nrrdfile can be any object which supports the iterator protocol and
    returns a string each time its next() method is called — file objects and
    list objects are both suitable. If csvfile is a file object, it must be
    opened with the ‘b’ flag on platforms where that makes a difference
    (e.g. Windows)

    >>> read_header(("NRRD0005", "type: float", "dimension: 3"))
    {'type': 'float', 'dimension': 3, 'keyvaluepairs': {}}
    >>> read_header(("NRRD0005", "my extra info:=my : colon-separated : values"))
    {'keyvaluepairs': {'my extra info': 'my : colon-separated : values'}}
    """
    # Collect number of bytes in the file header (for seeking below)
    headerSize = 0

    it = iter(nrrdfile)

    headerSize += _validate_magic_line(it.next())

    header = { 'keyvaluepairs': {} }
    for raw_line in it:
        headerSize += len(raw_line)

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
            header['keyvaluepairs'][key] = value
            continue

        # Handle the "<field>: <desc>" lines.
        field_desc = line.split(': ', 1)
        if len(field_desc) is 2:
            field, desc = field_desc
            if field not in _NRRD_FIELD_PARSERS:
                raise NrrdError('Unexpected field in nrrd header: "%s".' % field)
            if field in header.keys():
                raise NrrdError('Duplicate header field: "%s"' % field)
            header[field] = _NRRD_FIELD_PARSERS[field](desc)
            continue

        # Should not reach here
        raise NrrdError('Invalid header line: "%s"' % line)

    # line reading was buffered; correct file pointer to just behind header:
    nrrdfile.seek(headerSize)

    return header


def read(filename):
    """Read a nrrd file and return a tuple (data, header)."""
    with open(filename,'rb') as filehandle:
        header = read_header(filehandle)
        data = read_data(header, filehandle, filename)
        return (data, header)


def _format_nrrd_list(fieldValue) :
    return ' '.join([str(x) for x in fieldValue])


def _format_nrrdvector(v) :
    return '(' + ','.join([str(x) for x in v]) + ')'


def _format_optional_nrrdvector(v):
    if (v == 'none') :
        return 'none'
    else :
        return _format_nrrdvector(v)

_NRRD_FIELD_FORMATTERS = {
    'dimension': str,
    'type': str,
    'sizes': _format_nrrd_list,
    'endian': str,
    'encoding': str,
    'min': str,
    'max': str,
    'oldmin': str,
    'old min': str,
    'oldmax': str,
    'old max': str,
    'lineskip': str,
    'line skip': str,
    'byteskip': str,
    'byte skip': str,
    'content': str,
    'sample units': str,
    'datafile': str,
    'data file': str,
    'spacings': _format_nrrd_list,
    'thicknesses': _format_nrrd_list,
    'axis mins': _format_nrrd_list,
    'axismins': _format_nrrd_list,
    'axis maxs': _format_nrrd_list,
    'axismaxs': _format_nrrd_list,
    'centerings': _format_nrrd_list,
    'labels': _format_nrrd_list,
    'units': _format_nrrd_list,
    'kinds': _format_nrrd_list,
    'space': str,
    'space dimension': str,
    'space units': _format_nrrd_list,
    'space origin': _format_nrrdvector,
    'space directions': lambda fieldValue: ' '.join([_format_optional_nrrdvector(x) for x in fieldValue]),
    'measurement frame': lambda fieldValue: ' '.join([_format_optional_nrrdvector(x) for x in fieldValue]),
}


def _write_data(data, filehandle, options):
    # Now write data directly
    rawdata = data.tostring(order = 'F')
    if options['encoding'] == 'raw':
        filehandle.write(rawdata)
    elif options['encoding'] == 'gzip':
        gzfileobj = gzip.GzipFile(fileobj = filehandle)
        gzfileobj.write(rawdata)
        gzfileobj.close()
    elif options['encoding'] == 'bz2':
        bz2fileobj = bz2.BZ2File(fileobj = filehandle)
        bz2fileobj.write(rawdata)
        bz2fileobj.close()
    else:
        raise NrrdError('Unsupported encoding: "%s"' % options['encoding'])


def write(filename, data, options={}, separate_header=False):
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
    options['dimension'] = data.ndim
    options['sizes'] = list(data.shape)

    # The default encoding is 'gzip'
    if 'encoding' not in options:
        options['encoding'] = 'gzip'

    # A bit of magic in handling options here.
    # If *.nhdr filename provided, this overrides `separate_header=False`
    # If *.nrrd filename provided AND separate_header=True, separate files
    #   written.
    # For all other cases, header & data written to same file.
    if filename[-5:] == '.nhdr':
        separate_header = True
        datafilename = filename[:-4] + str('nrrd')
    elif filename[-5:] == '.nrrd' and separate_header:
        datafilename = filename
        filename = filename[:-4] + str('nhdr')
    else:
        # Write header & data as one file
        datafilename = filename

    with open(filename,'wb') as filehandle:
        filehandle.write('NRRD0004\n')
        filehandle.write('# This NRRD file was generated by pynrrd\n')
        filehandle.write('# on ' +
                         datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') +
                         '(GMT).\n')
        filehandle.write('# Complete NRRD file format specification at:\n');
        filehandle.write('# http://teem.sourceforge.net/nrrd/format.html\n');

        # Write the fields in order, this ignores fields not in _NRRD_FIELD_ORDER
        for field in _NRRD_FIELD_ORDER:
            if options.has_key(field):
                outline = (field + ': ' +
                           _NRRD_FIELD_FORMATTERS[field](options[field]) +
                           '\n')
                filehandle.write(outline)
        for (k,v) in options.get('keyvaluepairs', {}).items():
            outline = k + ':=' + v + '\n'
            filehandle.write(outline)

        if separate_header:
            # Write line skip & relative file location info to header
            outline = ('data file: ' + os.path.basename(datafilename) + '\n')
            filehandle.write(outline)
            filehandle.write('line skip: 0')

        # Write the closing extra newline
        filehandle.write('\n')

        # If a single file desired, write data
        if not separate_header:
            _write_data(data, filehandle, options)

    # If separate header desired, write data to different file
    if separate_header:
        with open(datafilename, 'wb') as datafilehandle:
            _write_data(data, datafilehandle, options)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
