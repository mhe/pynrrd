import bz2
import io
import os
import re
import shlex
import warnings
import zlib
from collections import OrderedDict
from typing import IO, AnyStr, Iterable, Tuple

from nrrd.parsers import *
from nrrd.types import IndexOrder, NRRDFieldMap, NRRDFieldType, NRRDHeader

# Older versions of Python had issues when uncompressed data was larger than 4GB (2^32). This should be fixed in latest
# version of Python 2.7 and all versions of Python 3. The fix for this issue is to read the data in smaller chunks.
# Chunk size is set to be large at 1GB to improve performance. If issues arise decompressing larger files, try to reduce
# this value
_READ_CHUNKSIZE: int = 2 ** 32

_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']

ALLOW_DUPLICATE_FIELD = False
"""Allow duplicate header fields when reading NRRD files

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

Note:
    Duplicated fields are prohibited by the NRRD file specification.
"""

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


def _get_field_type(field: str, custom_field_map: Optional[NRRDFieldMap]) -> NRRDFieldType:
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
    elif field in ['kinds', 'centerings']:
        return 'string list'
    elif field in ['labels', 'units', 'space units']:
        return 'quoted string list'
    # No int vector fields yet
    # elif field in []:
    #     return 'int vector'
    elif field in ['space origin']:
        return 'double vector'
    elif field in ['measurement frame']:
        return 'double matrix'
    elif field in ['space directions']:
        return 'double matrix'
    else:
        if custom_field_map and field in custom_field_map:
            return custom_field_map[field]

        # Default the type to string if unknown type
        return 'string'


def _parse_field_value(value: str, field_type: NRRDFieldType) -> Any:
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
        return [str(x) for x in value.split()]
    elif field_type == 'quoted string list':
        return shlex.split(value)
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
        raise NRRDError(f'Invalid field type given: {field_type}')


def _determine_datatype(header: NRRDHeader) -> np.dtype:
    """Determine the numpy dtype of the data."""

    # Convert the NRRD type string identifier into a NumPy string identifier using a map
    np_typestring = _TYPEMAP_NRRD2NUMPY[header['type']]

    # This is only added if the datatype has more than one byte and is not using ASCII encoding
    # Note: Endian is not required for ASCII encoding
    if np.dtype(np_typestring).itemsize > 1 and header['encoding'] not in ['ASCII', 'ascii', 'text', 'txt']:
        if 'endian' not in header:
            raise NRRDError('Header is missing required field: endian')
        elif header['endian'] == 'big':
            np_typestring = '>' + np_typestring
        elif header['endian'] == 'little':
            np_typestring = '<' + np_typestring
        else:
            raise NRRDError(f'Invalid endian value in header: {header["endian"]}')

    return np.dtype(np_typestring)


def _validate_magic_line(line: str) -> int:
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
            raise NRRDError(f'Unsupported NRRD file version (version: {version}). This library only supports v5 '
                            'and below.')
    except ValueError:
        raise NRRDError(f'Invalid NRRD magic line: {line}')

    return len(line)


def read_header(file: Union[str, Iterable[AnyStr]], custom_field_map: Optional[NRRDFieldMap] = None) -> NRRDHeader:
    """Read contents of header and parse values from :obj:`file`

    :obj:`file` can be a filename indicating where the NRRD header is located or a string iterator object. If a
    filename is specified, then the file will be opened and closed after the header is read from it. If not specifying
    a filename, the :obj:`file` parameter can be any sort of iterator that returns a string each time :meth:`next` is
    called. The two common objects that meet these requirements are file objects and a list of strings. When
    :obj:`file` is a file object, it must be opened with the binary flag ('b') on platforms where that makes a
    difference, such as Windows.

    See :ref:`background/how-to-use:reading nrrd files` for more information on reading NRRD files.

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
            return read_header(fh, custom_field_map)

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
            if not ALLOW_DUPLICATE_FIELD:
                raise NRRDError(f'Duplicate header field: {field}')
            else:
                warnings.warn(f'Duplicate header field: {field}')

        # Get the datatype of the field based on its field name and custom field map
        field_type = _get_field_type(field, custom_field_map)

        # Parse the field value using the datatype retrieved
        # Place it in the header dictionary
        header[field] = _parse_field_value(value, field_type)

    # Reading the file line by line is buffered and so the header is not in the correct position for reading data if
    # the file contains the data in it as well. The solution is to set the file pointer to just behind the header.
    if hasattr(file, 'seek'):
        file.seek(header_size)

    return header


def read_data(header: NRRDHeader, fh: Optional[IO] = None, filename: Optional[str] = None,
              index_order: IndexOrder = 'F') -> npt.NDArray:
    """Read data from file into :class:`numpy.ndarray`

    The two parameters :obj:`fh` and :obj:`filename` are optional depending on the parameters but it never hurts to
    specify both. The file handle (:obj:`fh`) is necessary if the header is attached with the NRRD data. However, if
    the NRRD data is detached from the header, then the :obj:`filename` parameter is required to obtain the absolute
    path to the data file.

    See :ref:`background/how-to-use:reading nrrd files` for more information on reading NRRD files.

    Parameters
    ----------
    header : :class:`dict` (:class:`str`, :obj:`Object`)
        Parsed fields/values obtained from :meth:`read_header` function
    fh : file-object, optional
        File object pointing to first byte of data. Only necessary if data is attached to header.
    filename : :class:`str`, optional
        Filename of the header file. Only necessary if data is detached from the header. This is used to get the
        absolute data path.
    index_order : {'C', 'F'}, optional
        Specifies the index order of the resulting data array. Either 'C' (C-order) where the dimensions are ordered
        from slowest-varying to fastest-varying (e.g. (z, y, x)), or 'F' (Fortran-order) where the dimensions are
        ordered from fastest-varying to slowest-varying (e.g. (x, y, z)).

    Returns
    -------
    data : :class:`numpy.ndarray`
        Data read from NRRD file

    See Also
    --------
    :meth:`read`, :meth:`read_header`
    """

    if index_order not in ['F', 'C']:
        raise NRRDError('Invalid index order')

    # Check that the required fields are in the header
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in header:
            raise NRRDError(f'Header is missing required field: {field}')

    if header['dimension'] != len(header['sizes']):
        raise NRRDError(f'Number of elements in sizes does not match dimension. Dimension: {header["dimension"]}, '
                        f'len(sizes): {len(header["sizes"])}')

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
        # Note that this is opened without a "with" block, thus it must be closed manually in all circumstances
        fh = open(data_filename, 'rb')

    # Get the total number of data points by multiplying the size of each dimension together
    total_data_points = header['sizes'].prod(dtype=np.int64)

    # Skip the number of lines requested when line_skip >= 0
    # Irrespective of the NRRD file having attached/detached header
    # Lines are skipped before getting to the beginning of the data
    if line_skip >= 0:
        for _ in range(line_skip):
            fh.readline()
    else:
        # Must close the file because if the file was opened above from detached filename, there is no "with" block to
        # close it for us
        fh.close()

        raise NRRDError('Invalid lineskip, allowed values are greater than or equal to 0')

    # Skip the requested number of bytes or seek backward, and then parse the data using NumPy
    if byte_skip < -1:
        # Must close the file because if the file was opened above from detached filename, there is no "with" block to
        # close it for us
        fh.close()

        raise NRRDError('Invalid byteskip, allowed values are greater than or equal to -1')
    elif byte_skip >= 0:
        fh.seek(byte_skip, os.SEEK_CUR)
    elif byte_skip == -1 and header['encoding'] not in ['gzip', 'gz', 'bzip2', 'bz2']:
        fh.seek(-dtype.itemsize * total_data_points, os.SEEK_END)
    else:
        # The only case left should be: byte_skip == -1 and header['encoding'] == 'gzip'
        byte_skip = -dtype.itemsize * total_data_points

    # If a compression encoding is used, then byte skip AFTER decompressing
    if header['encoding'] == 'raw':
        if isinstance(fh, io.BytesIO):
            raw_data = bytearray(fh.read(total_data_points * dtype.itemsize))
            data = np.frombuffer(raw_data, dtype)
        else:
            data = np.fromfile(fh, dtype)
    elif header['encoding'] in ['ASCII', 'ascii', 'text', 'txt']:
        if isinstance(fh, io.BytesIO):
            data = np.fromstring(fh.read(), dtype, sep=' ')
        else:
            data = np.fromfile(fh, dtype, sep=' ')
    else:
        # Handle compressed data now
        # Construct the decompression object based on encoding
        if header['encoding'] in ['gzip', 'gz']:
            decompobj = zlib.decompressobj(zlib.MAX_WBITS | 16)
        elif header['encoding'] in ['bzip2', 'bz2']:
            decompobj = bz2.BZ2Decompressor()
        else:
            # Must close the file because if the file was opened above from detached filename, there is no "with" block
            # to close it for us
            fh.close()

            raise NRRDError(f'Unsupported encoding: {header["encoding"]}')

        # Loop through the file and read a chunk at a time (see _READ_CHUNKSIZE why it is read in chunks)
        decompressed_data = bytearray()

        # Read all the remaining data from the file
        # Obtain the length of the compressed data since we will be using it repeatedly, more efficient
        compressed_data = fh.read()
        compressed_data_len = len(compressed_data)
        start_index = 0

        # Loop through data and decompress it chunk by chunk
        while start_index < compressed_data_len:
            # Calculate the end index = start index plus chunk size
            # Set to the string length to read the remaining chunk at the end
            end_index = min(start_index + _READ_CHUNKSIZE, compressed_data_len)

            # Decompress and append data
            decompressed_data += decompobj.decompress(compressed_data[start_index:end_index])

            # Update start index
            start_index = end_index

        # Delete the compressed data since we do not need it anymore
        # This could potentially be using a lot of memory
        del compressed_data

        # Byte skip is applied AFTER the decompression. Skip first x bytes of the decompressed data and parse it using
        # NumPy
        data = np.frombuffer(decompressed_data[byte_skip:], dtype)

    # Close the file, even if opened using "with" block, closing it manually does not hurt
    fh.close()

    if total_data_points != data.size:
        raise NRRDError(f'Size of the data does not equal the product of all the dimensions: '
                        f'{total_data_points}-{data.size}={total_data_points - data.size}')

    # In the NRRD header, the fields are specified in Fortran order, i.e, the first index is the one that changes
    # fastest and last index changes slowest. This needs to be taken into consideration since numpy uses C-order
    # indexing.

    # The array shape from NRRD (x,y,z) needs to be reversed as numpy expects (z,y,x).
    data = np.reshape(data, tuple(header['sizes'][::-1]))

    # Transpose data to enable Fortran indexing if requested.
    if index_order == 'F':
        data = data.T

    return data


def read(filename: str, custom_field_map: Optional[NRRDFieldMap] = None, index_order: IndexOrder = 'F') \
        -> Tuple[npt.NDArray, NRRDHeader]:
    """Read a NRRD file and return the header and data

    See :ref:`background/how-to-use:reading nrrd files` for more information on reading NRRD files.

    .. note::
            Users should be aware that the `index_order` argument needs to be consistent between `nrrd.read` and
            `nrrd.write`. I.e., reading an array with `index_order='F'` will result in a transposed version of the
            original data and hence the writer needs to be aware of this.

    Parameters
    ----------
    filename : :class:`str`
        Filename of the NRRD file
    custom_field_map : :class:`dict` (:class:`str`, :class:`str`), optional
        Dictionary used for parsing custom field types where the key is the custom field name and the value is a
        string identifying datatype for the custom field.
    index_order : {'C', 'F'}, optional
        Specifies the index order of the resulting data array. Either 'C' (C-order) where the dimensions are ordered
        from slowest-varying to fastest-varying (e.g. (z, y, x)), or 'F' (Fortran-order) where the dimensions are
        ordered from fastest-varying to slowest-varying (e.g. (x, y, z)).

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

    with open(filename, 'rb') as fh:
        header = read_header(fh, custom_field_map)
        data = read_data(header, fh, filename, index_order)

    return data, header
