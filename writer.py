import bz2
import zlib
from datetime import datetime

from errors import NrrdError
from formatters import *

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
