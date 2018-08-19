import bz2
import os
import zlib
from collections import OrderedDict
from datetime import datetime

from nrrd.errors import NRRDError
from nrrd.formatters import *
from nrrd.reader import _get_field_type

# Reading and writing gzipped data directly gives problems when the uncompressed
# data is larger than 4GB (2^32). Therefore we'll read and write the data in
# chunks. How this affects speed and/or memory usage is something to be analyzed
# further. The following two values define the size of the chunks.
_WRITE_CHUNKSIZE = 2 ** 20

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


def _format_field_value(value, field_type):
    if field_type == 'int':
        return format_number(value)
    elif field_type == 'double':
        return format_number(value)
    elif field_type == 'string':
        return str(value)
    elif field_type == 'int list':
        return format_number_list(value)
    elif field_type == 'double list':
        return format_number_list(value)
    elif field_type == 'string list':
        # TODO Handle cases where the user wants quotation marks around the items
        return ' '.join(value)
    elif field_type == 'int vector':
        return format_vector(value)
    elif field_type == 'double vector':
        return format_optional_vector(value)
    elif field_type == 'int matrix':
        return format_matrix(value)
    elif field_type == 'double matrix':
        return format_optional_matrix(value)
    else:
        raise NRRDError('Invalid field type given: %s' % field_type)


def write(filename, data, header={}, detached_header=False, custom_field_map=None):
    """Write the numpy data to a NRRD file. The NRRD header values to use are
    inferred from from the data. Additional options can be passed in the
    options dictionary. See the read() function for the structure of this
    dictionary.

    To set data samplings, use e.g. `options['spacings'] = [s1, s2, s3]` for
    3d data with sampling deltas `s1`, `s2`, and `s3` in each dimension.

    """

    # Infer a number of fields from the NumPy array and overwrite values in the header dictionary.
    # Get type string identifier from the NumPy datatype
    header['type'] = _TYPEMAP_NUMPY2NRRD[data.dtype.str[1:]]

    # If the datatype contains more than one byte and the encoding is not ASCII, then set the endian header value
    # based on the datatype's endianness. Otherwise, delete the endian field from the header if present
    if data.dtype.itemsize > 1 and header.get('encoding', '').lower() not in ['ascii', 'text', 'txt']:
        header['endian'] = _NUMPY2NRRD_ENDIAN_MAP[data.dtype.str[:1]]
    elif 'endian' in header:
        del header['endian']

    # If space is specified in the header, then space dimension can not. See
    # http://teem.sourceforge.net/nrrd/format.html#space
    if 'space' in header.keys() and 'space dimension' in header.keys():
        del header['space dimension']

    # Update the dimension and sizes fields in the header based on the data
    header['dimension'] = data.ndim
    header['sizes'] = list(data.shape)

    # The default encoding is 'gzip'
    if 'encoding' not in header:
        header['encoding'] = 'gzip'

    # A bit of magic in handling options here.
    # If *.nhdr filename provided, this overrides `detached_header=False`
    # If *.nrrd filename provided AND detached_header=True, separate header and data files written.
    # If detached_header=True and data file is present, then write the files separately
    # For all other cases, header & data written to same file.
    if filename.endswith('.nhdr'):
        detached_header = True

        if 'data file' not in header:
            # Get the base filename without the extension
            base_filename = os.path.splitext(filename)[0]

            # Get the appropriate data filename based on encoding, see here for information on the standard detached
            # filename: http://teem.sourceforge.net/nrrd/format.html#encoding
            if header['encoding'] == 'raw':
                data_filename = '%s.raw' % base_filename
            elif header['encoding'] in ['ASCII', 'ascii', 'text', 'txt']:
                data_filename = '%s.txt' % base_filename
            elif header['encoding'] in ['gzip', 'gz']:
                data_filename = '%s.raw.gz' % base_filename
            elif header['encoding'] in ['bzip2', 'bz2']:
                data_filename = '%s.raw.bz2' % base_filename
            else:
                raise NRRDError('Invalid encoding specification while writing NRRD file: %s' % header['encoding'])

            header['data file'] = data_filename
        else:
            data_filename = header['data file']
    elif filename.endswith('.nrrd') and detached_header:
        data_filename = filename
        header['data file'] = data_filename
        filename = '%s.nhdr' % os.path.splitext(filename)[0]
    else:
        # Write header & data as one file
        data_filename = filename
        detached_header = False

    with open(filename, 'wb') as fh:
        fh.write(b'NRRD0005\n')
        fh.write(b'# This NRRD file was generated by pynrrd\n')
        fh.write(b'# on ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S').encode('ascii') + b'(GMT).\n')
        fh.write(b'# Complete NRRD file format specification at:\n')
        fh.write(b'# http://teem.sourceforge.net/nrrd/format.html\n')

        # Copy the options since dictionaries are mutable when passed as an argument
        # Thus, to prevent changes to the actual options, a copy is made
        # Empty ordered_options list is made (will be converted into dictionary)
        local_options = header.copy()
        ordered_options = []

        # Loop through field order and add the key/value if present
        # Remove the key/value from the local options so that we know not to add it again
        for field in _NRRD_FIELD_ORDER:
            if field in local_options:
                ordered_options.append((field, local_options[field]))
                del local_options[field]

        # Leftover items are assumed to be the custom field/value options
        # So get current size and any items past this index will be a custom value
        custom_field_start_index = len(ordered_options)

        # Add the leftover items to the end of the list and convert the options into a dictionary
        ordered_options.extend(local_options.items())
        ordered_options = OrderedDict(ordered_options)

        for x, (field, value) in enumerate(ordered_options.items()):
            # Get the field_type based on field and then get corresponding
            # value as a str using _format_field_value
            field_type = _get_field_type(field, custom_field_map)
            value_str = _format_field_value(value, field_type)

            # Custom fields are written as key/value pairs with a := instead of : delimeter
            if x >= custom_field_start_index:
                fh.write(('%s:= %s\n' % (field, value_str)).encode('ascii'))
            else:
                fh.write(('%s: %s\n' % (field, value_str)).encode('ascii'))

        # Write the closing extra newline
        fh.write(b'\n')

        # If header & data in the same file is desired, write data in the file
        if not detached_header:
            _write_data(data, fh, header)

    # If detached header desired, write data to different file
    if detached_header:
        with open(data_filename, 'wb') as data_fh:
            _write_data(data, data_fh, header)


def _write_data(data, fh, header):
    if header['encoding'] == 'raw':
        # Convert the data into a string
        raw_data = data.tostring(order='F')

        # Write the raw data directly to the file
        fh.write(raw_data)
    elif header['encoding'].lower() in ['ascii', 'text', 'txt']:
        # savetxt only works for 1D and 2D arrays, so reshape any > 2 dim arrays into one long 1D array
        if data.ndim > 2:
            np.savetxt(fh, data.ravel(order='F'), '%.17g')
        else:
            np.savetxt(fh, data.T, '%.17g')
    else:
        # Convert the data into a string
        raw_data = data.tostring(order='F')

        # Construct the compressor object based on encoding
        if header['encoding'] in ['gzip', 'gz']:
            compressobj = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        elif header['encoding'] in ['bzip2', 'bz2']:
            compressobj = bz2.BZ2Compressor()
        else:
            raise NRRDError('Unsupported encoding: "%s"' % header['encoding'])

        # Write the data in chunks (see _WRITE_CHUNKSIZE declaration for more information why)
        start_index = 0

        # Loop through the data and write it by chunk
        while start_index < len(raw_data):
            # End index is start index plus the chunk size
            end_index = start_index + _WRITE_CHUNKSIZE

            # If the end index is past the data size, then clamp it to the data size
            if end_index > len(raw_data):
                end_index = len(raw_data)

            # Write the compressed data
            fh.write(compressobj.compress(raw_data[start_index:end_index]))

            start_index = end_index

        # Finish writing the data
        fh.write(compressobj.flush())
        fh.flush()
