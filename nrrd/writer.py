import bz2
import os
import zlib
from collections import OrderedDict
from datetime import datetime

from nrrd.errors import NRRDError
from nrrd.formatters import *
from nrrd.reader import _get_field_type

# Older versions of Python had issues when uncompressed data was larger than 4GB (2^32). This should be fixed in latest
# version of Python 2.7 and all versions of Python 3. The fix for this issue is to read the data in smaller chunks. The
# chunk size is set to be small here at 1MB since performance did not vary much based on the chunk size. A smaller chunk
# size has the benefit of using less RAM at once.
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


def write(filename, data, header=None, detached_header=False, relative_data_path=True, custom_field_map=None,
          compression_level=9, index_order='F'):
    """Write :class:`numpy.ndarray` to NRRD file

    The :obj:`filename` parameter specifies the absolute or relative filename to write the NRRD file to. If the
    :obj:`filename` extension is .nhdr, then the :obj:`detached_header` parameter is set to true automatically. If the
    :obj:`detached_header` parameter is set to :obj:`True` and the :obj:`filename` ends in .nrrd, then the header file
    will have the same path and base name as the :obj:`filename` but with an extension of .nhdr. In all other cases,
    the header and data are saved in the same file.

    :obj:`header` is an optional parameter containing the fields and values to be added to the NRRD header.

    .. note::
            The following fields are automatically generated based on the :obj:`data` parameter ignoring these values
            in the :obj:`header`: 'type', 'endian', 'dimension', 'sizes'. In addition, the generated fields will be
            added to the given :obj:`header`. Thus, one can check the generated fields by viewing the passed
            :obj:`header`.

    .. note::
            The default encoding field used if not specified in :obj:`header` is 'gzip'.

    .. note::
            The :obj:`index_order` parameter must be consistent with the index order specified in :meth:`read`.
            Reading an NRRD file in C-order and then writing as Fortran-order or vice versa will result in the data
            being transposed in the NRRD file.

    See :ref:`user-guide:Writing NRRD files` for more information on writing NRRD files.

    Parameters
    ----------
    filename : :class:`str`
        Filename of the NRRD file
    data : :class:`numpy.ndarray`
        Data to save to the NRRD file
    detached_header : :obj:`bool`, optional
        Whether the header and data should be saved in separate files. Defaults to :obj:`False`
    relative_data_path : :class:`bool`
        Whether the data filename in detached header is saved with a relative path or absolute path.
        This parameter is ignored if there is no detached header. Defaults to :obj:`True`
    custom_field_map : :class:`dict` (:class:`str`, :class:`str`), optional
        Dictionary used for parsing custom field types where the key is the custom field name and the value is a
        string identifying datatype for the custom field.
    compression_level : :class:`int`
        Integer between 1 to 9 specifying the compression level when using a compressed encoding (gzip or bzip). A value
        of :obj:`1` compresses the data the least amount and is the fastest, while a value of :obj:`9` compresses the
        data the most and is the slowest.
    index_order : {'C', 'F'}, optional
        Specifies the index order used for writing. Either 'C' (C-order) where the dimensions are ordered from
        slowest-varying to fastest-varying (e.g. (z, y, x)), or 'F' (Fortran-order) where the dimensions are ordered
        from fastest-varying to slowest-varying (e.g. (x, y, z)).

    See Also
    --------
    :meth:`read`, :meth:`read_header`, :meth:`read_data`
    """

    if header is None:
        header = {}

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

    # Update the dimension and sizes fields in the header based on the data. Since NRRD expects meta data to be in
    # Fortran order we are required to reverse the shape in the case of the array being in C order. E.g., data was read
    # using index_order='C'.
    header['dimension'] = data.ndim
    header['sizes'] = list(data.shape) if index_order == 'F' else list(data.shape[::-1])

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

            header['data file'] = os.path.basename(data_filename) \
                if relative_data_path else os.path.abspath(data_filename)
        else:
            # TODO This will cause issues for relative data files because it will not save in the correct spot
            data_filename = header['data file']
    elif filename.endswith('.nrrd') and detached_header:
        data_filename = filename
        header['data file'] = os.path.basename(data_filename) \
            if relative_data_path else os.path.abspath(data_filename)
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
                fh.write(('%s:=%s\n' % (field, value_str)).encode('ascii'))
            else:
                fh.write(('%s: %s\n' % (field, value_str)).encode('ascii'))

        # Write the closing extra newline
        fh.write(b'\n')

        # If header & data in the same file is desired, write data in the file
        if not detached_header:
            _write_data(data, fh, header, compression_level=compression_level, index_order=index_order)

    # If detached header desired, write data to different file
    if detached_header:
        with open(data_filename, 'wb') as data_fh:
            _write_data(data, data_fh, header, compression_level=compression_level, index_order=index_order)


def _write_data(data, fh, header, compression_level=None, index_order='F'):
    if index_order not in ['F', 'C']:
        raise NRRDError('Invalid index order')

    if header['encoding'] == 'raw':
        # Convert the data into a string
        raw_data = data.tostring(order=index_order)

        # Write the raw data directly to the file
        fh.write(raw_data)
    elif header['encoding'].lower() in ['ascii', 'text', 'txt']:
        # savetxt only works for 1D and 2D arrays, so reshape any > 2 dim arrays into one long 1D array
        if data.ndim > 2:
            np.savetxt(fh, data.ravel(order=index_order), '%.17g')
        else:
            np.savetxt(fh, data if index_order == 'C' else data.T, '%.17g')

    else:
        # Convert the data into a string
        raw_data = data.tostring(order=index_order)

        # Construct the compressor object based on encoding
        if header['encoding'] in ['gzip', 'gz']:
            compressobj = zlib.compressobj(compression_level, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        elif header['encoding'] in ['bzip2', 'bz2']:
            compressobj = bz2.BZ2Compressor(compression_level)
        else:
            raise NRRDError('Unsupported encoding: "%s"' % header['encoding'])

        # Write the data in chunks (see _WRITE_CHUNKSIZE declaration for more information why)
        # Obtain the length of the data since we will be using it repeatedly, more efficient
        start_index = 0
        raw_data_len = len(raw_data)

        # Loop through the data and write it by chunk
        while start_index < raw_data_len:
            # End index is start index plus the chunk size
            # Set to the string length to read the remaining chunk at the end
            end_index = min(start_index + _WRITE_CHUNKSIZE, raw_data_len)

            # Write the compressed data
            fh.write(compressobj.compress(raw_data[start_index:end_index]))

            start_index = end_index

        # Finish writing the data
        fh.write(compressobj.flush())
        fh.flush()
