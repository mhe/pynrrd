import bz2
import zlib
from datetime import datetime
from collections import OrderedDict

from nrrd.errors import NrrdError
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
        raise NrrdError('Invalid field type given: %s' % field_type)


def _write_data(data, filehandle, options):
    # Now write data directly
    rawdata = data.tostring(order='F')
    if options['encoding'] == 'raw':
        filehandle.write(rawdata)
    elif options['encoding'].lower() in ['ascii', 'text', 'txt']:
        # savetxt only works for 1D and 2D arrays, so reshape any > 2 dim arrays into one long 1D array
        if data.ndim > 2:
            np.savetxt(filehandle, data.ravel(order='F'), '%.17g')
        else:
            np.savetxt(filehandle, data.T, '%.17g')
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

# TODO Change options to header, makes more sense
def write(filename, data, options={}, detached_header=False, custom_field_map=None):
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
    # Do not add endianness if encoding is ASCII
    if data.dtype.itemsize > 1 and options.get('encoding', '').lower() not in ['ascii', 'text', 'txt']:
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

        # Copy the options since dictionaries are mutable when passed as an argument
        # Thus, to prevent changes to the actual options, a copy is made
        # Empty ordered_options list is made (will be converted into dictionary)
        local_options = options.copy()
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
                filehandle.write(('%s:= %s\n' % (field, value_str)).encode('ascii'))
            else:
                filehandle.write(('%s: %s\n' % (field, value_str)).encode('ascii'))

        # Write the closing extra newline
        filehandle.write(b'\n')

        # If a single file desired, write data
        if not detached_header:
            _write_data(data, filehandle, options)

    # If detached header desired, write data to different file
    if detached_header:
        with open(datafilename, 'wb') as datafilehandle:
            _write_data(data, datafilehandle, options)
