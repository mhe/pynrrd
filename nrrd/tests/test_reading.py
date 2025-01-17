import io
import unittest
from typing import ClassVar

import numpy as np
from typing_extensions import Literal

import nrrd
from nrrd.tests.util import *


class Abstract:
    class TestReadingFunctions(unittest.TestCase):
        index_order: ClassVar[Literal['F', 'C']]

        def setUp(self):
            self.expected_header = {'dimension': 3,
                                    'encoding': 'raw',
                                    'endian': 'little',
                                    'kinds': ['domain', 'domain', 'domain'],
                                    'sizes': np.array([30, 30, 30]),
                                    'space': 'left-posterior-superior',
                                    'space directions': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                                    'space origin': np.array([0, 0, 0]),
                                    'type': 'short'}

            self.expected_data = np.fromfile(RAW_DATA_FILE_PATH, np.int16).reshape((30, 30, 30))
            if self.index_order == 'F':
                self.expected_data = self.expected_data.T

        def test_read_header_only(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)

            # np.testing.assert_equal is used to compare the headers because it will appropriately handle each
            # value in the structure. Since some values can be Numpy arrays inside the headers, this must be used to
            # compare the two values.
            np.testing.assert_equal(self.expected_header, header)

        def test_read_header_only_with_filename(self):
            header = nrrd.read_header(RAW_NRRD_FILE_PATH)

            # np.testing.assert_equal is used to compare the headers because it will appropriately handle each
            # value in the structure. Since some values can be Numpy arrays inside the headers, this must be used to
            # compare the two values.
            np.testing.assert_equal(self.expected_header, header)

        def test_read_detached_header_only(self):
            expected_header = self.expected_header
            expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)

            with open(RAW_NHDR_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)

            np.testing.assert_equal(self.expected_header, header)

        def test_read_header_and_data_filename(self):
            data, header = nrrd.read(RAW_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_detached_header_and_data(self):
            expected_header = self.expected_header
            expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)

            data, header = nrrd.read(RAW_NHDR_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_detached_header_and_data_with_byteskip_minus1(self):
            expected_header = self.expected_header
            expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)
            expected_header['byte skip'] = -1

            data, header = nrrd.read(RAW_BYTESKIP_NHDR_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_detached_header_and_nifti_data_with_byteskip_minus1(self):
            expected_header = self.expected_header
            expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)
            expected_header['byte skip'] = -1
            expected_header['encoding'] = 'gzip'
            expected_header['data file'] = 'BallBinary30x30x30.nii.gz'

            data, header = nrrd.read(GZ_BYTESKIP_NIFTI_NHDR_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_detached_header_and_nifti_data(self):
            with self.assertRaisesRegex(
                    nrrd.NRRDError,
                    'Size of the data does not equal the product of all the dimensions: 27000-27176=-176'):
                nrrd.read(GZ_NIFTI_NHDR_FILE_PATH, index_order=self.index_order)

        def test_read_detached_header_and_data_with_byteskip_minus5(self):
            with self.assertRaisesRegex(nrrd.NRRDError,
                                        'Invalid byteskip, allowed values are greater than or equal to -1'):
                nrrd.read(RAW_INVALID_BYTESKIP_NHDR_FILE_PATH, index_order=self.index_order)

        def test_read_header_and_gz_compressed_data(self):
            expected_header = self.expected_header
            expected_header['encoding'] = 'gzip'

            data, header = nrrd.read(GZ_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_header_and_gz_compressed_data_with_byteskip_minus1(self):
            expected_header = self.expected_header
            expected_header['encoding'] = 'gzip'
            expected_header['type'] = 'int16'
            expected_header['byte skip'] = -1

            data, header = nrrd.read(GZ_BYTESKIP_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_header_and_bz2_compressed_data(self):
            expected_header = self.expected_header
            expected_header['encoding'] = 'bzip2'

            data, header = nrrd.read(BZ2_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_header_and_gz_compressed_data_with_lineskip3(self):
            expected_header = self.expected_header
            expected_header['encoding'] = 'gzip'
            expected_header['line skip'] = 3

            data, header = nrrd.read(GZ_LINESKIP_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(self.expected_header, header)
            np.testing.assert_equal(data, self.expected_data)

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_raw_header(self):
            expected_header = {'type': 'float', 'dimension': 3, 'min': 0, 'max': 35.4}
            header = nrrd.read_header(('NRRD0005', 'type: float', 'dimension: 3', 'min: 0', 'max: 35.4'))
            self.assertEqual(expected_header, header)

            expected_header = {'my extra info': 'my : colon-separated : values'}
            header = nrrd.read_header(('NRRD0005', 'my extra info:=my : colon-separated : values'))
            np.testing.assert_equal(expected_header, header)

        def test_read_dup_field_error_and_warn(self):
            expected_header = {'type': 'float', 'dimension': 3}
            header_txt_tuple = ('NRRD0005', 'type: float', 'dimension: 3', 'type: float')

            with self.assertRaisesRegex(nrrd.NRRDError, 'Duplicate header field: type'):
                header = nrrd.read_header(header_txt_tuple)

            import warnings
            with warnings.catch_warnings(record=True) as w:
                nrrd.reader.ALLOW_DUPLICATE_FIELD = True
                header = nrrd.read_header(header_txt_tuple)

                self.assertTrue('Duplicate header field: type' in str(w[0].message))

                self.assertEqual(expected_header, header)
                nrrd.reader.ALLOW_DUPLICATE_FIELD = False

        def test_read_header_and_ascii_1d_data(self):
            expected_header = {'dimension': 1,
                               'encoding': 'ASCII',
                               'kinds': ['domain'],
                               'sizes': [27],
                               'spacings': [1.0458000000000001],
                               'type': 'unsigned char'}

            data, header = nrrd.read(ASCII_1D_NRRD_FILE_PATH, index_order=self.index_order)

            self.assertEqual(header, expected_header)
            np.testing.assert_equal(data.dtype, np.uint8)
            np.testing.assert_equal(data, np.arange(1, 28))

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_header_and_ascii_2d_data(self):
            expected_header = {'dimension': 2,
                               'encoding': 'ASCII',
                               'kinds': ['domain', 'domain'],
                               'sizes': [3, 9],
                               'spacings': [1.0458000000000001, 2],
                               'type': 'unsigned short'}

            data, header = nrrd.read(ASCII_2D_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(header, expected_header)
            np.testing.assert_equal(data.dtype, np.uint16)

            expected_shape = (3, 9) if self.index_order == 'F' else (9, 3)
            np.testing.assert_equal(data, np.arange(1, 28).reshape(expected_shape, order=self.index_order))

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_read_simple_4d_nrrd(self):
            expected_header = {'type': 'double',
                               'dimension': 4,
                               'space': 'right-anterior-superior',
                               'sizes': np.array([1, 1, 1, 1]),
                               'space directions': np.array([[1.5, 0., 0.],
                                                             [0., 1.5, 0.],
                                                             [0., 0., 1.],
                                                             [np.nan, np.nan, np.nan]]),
                               'endian': 'little',
                               'encoding': 'raw',
                               'measurement frame': np.array([[1.0001, 0., 0.],
                                                              [0., 1.0000000006, 0.],
                                                              [0., 0., 1.000000000000009]])}

            data, header = nrrd.read(RAW_4D_NRRD_FILE_PATH, index_order=self.index_order)

            np.testing.assert_equal(header, expected_header)
            np.testing.assert_equal(data.dtype, np.float64)
            np.testing.assert_equal(header['measurement frame'].dtype, np.float64)
            np.testing.assert_equal(data, np.array([[[[0.76903426]]]]))

            # Test that the data read is able to be edited
            self.assertTrue(data.flags['WRITEABLE'])

        def test_custom_fields_without_field_map(self):
            expected_header = {'dimension': 1,
                               'encoding': 'ASCII',
                               'kinds': ['domain'],
                               'sizes': [27],
                               'spacings': [1.0458000000000001],
                               'int': '24',
                               'double': '25.5566',
                               'string': 'This is a long string of information that is important.',
                               'int list': '1 2 3 4 5 100',
                               'double list': '0.2 0.502 0.8',
                               'string list': 'words are split by space in list',
                               'int vector': '(100, 200, -300)',
                               'double vector': '(100.5,200.3,-300.99)',
                               'int matrix': '(1,0,0) (0,1,0) (0,0,1)',
                               'double matrix': '(1.2,0.3,0) (0,1.5,0) (0,-0.55,1.6)',
                               'type': 'unsigned char'}

            header = nrrd.read_header(ASCII_1D_CUSTOM_FIELDS_FILE_PATH)

            self.assertEqual(header, expected_header)

        def test_custom_fields_with_field_map(self):
            expected_header = {'dimension': 1,
                               'encoding': 'ASCII',
                               'kinds': ['domain'],
                               'sizes': [27],
                               'spacings': [1.0458000000000001],
                               'int': 24,
                               'double': 25.5566,
                               'string': 'This is a long string of information that is important.',
                               'int list': np.array([1, 2, 3, 4, 5, 100]),
                               'double list': np.array([0.2, 0.502, 0.8]),
                               'string list': ['words', 'are', 'split', 'by', 'space', 'in', 'list'],
                               'int vector': np.array([100, 200, -300]),
                               'double vector': np.array([100.5, 200.3, -300.99]),
                               'int matrix': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                               'double matrix': np.array([[1.2, 0.3, 0.0], [0.0, 1.5, 0.0], [0.0, -0.55, 1.6]]),
                               'type': 'unsigned char'}

            custom_field_map = {'int': 'int',
                                'double': 'double',
                                'string': 'string',
                                'int list': 'int list',
                                'double list': 'double list',
                                'string list': 'string list',
                                'int vector': 'int vector',
                                'double vector': 'double vector',
                                'int matrix': 'int matrix',
                                'double matrix': 'double matrix'}
            header = nrrd.read_header(ASCII_1D_CUSTOM_FIELDS_FILE_PATH, custom_field_map)

            np.testing.assert_equal(header, expected_header)

        def test_invalid_custom_field(self):
            custom_field_map = {'int': 'fake'}

            with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid field type given: fake'):
                nrrd.read_header(ASCII_1D_CUSTOM_FIELDS_FILE_PATH, custom_field_map)

        def test_invalid_magic_line(self):
            with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid NRRD magic line. Is this an NRRD file?'):
                nrrd.read_header(('invalid magic line', 'my extra info:=my : colon-separated : values'))

        def test_invalid_magic_line2(self):
            with self.assertRaisesRegex(nrrd.NRRDError,
                                        'Unsupported NRRD file version \\(version: 2000\\). This library '
                                        'only supports v5 and below.'):
                nrrd.read_header(('NRRD2000', 'my extra info:=my : colon-separated : values'))

        def test_invalid_magic_line3(self):
            with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid NRRD magic line: NRRDnono'):
                nrrd.read_header(('NRRDnono', 'my extra info:=my : colon-separated : values'))

        def test_missing_required_field(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Delete required field
                del header['type']

                with self.assertRaisesRegex(nrrd.NRRDError, 'Header is missing required field: type'):
                    nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)

        def test_wrong_sizes(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Make the number of dimensions wrong
                header['dimension'] = 2

                with self.assertRaisesRegex(nrrd.NRRDError, 'Number of elements in sizes does not match dimension. '
                                                            'Dimension: 2, len\\(sizes\\): 3'):
                    nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)

        def test_invalid_encoding(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Set the encoding to be incorrect
                header['encoding'] = 'fake'

                with self.assertRaisesRegex(nrrd.NRRDError, 'Unsupported encoding: fake'):
                    nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)

        def test_detached_header_no_filename(self):
            self.expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)

            with open(RAW_NHDR_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # No filename is specified for read_data
                with self.assertRaisesRegex(nrrd.NRRDError,
                                            'Filename parameter must be specified when a relative data file'
                                            ' path is given'):
                    nrrd.read_data(header, fh)

        def test_invalid_lineskip(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Set the line skip to be incorrect
                header['line skip'] = -1

                with self.assertRaisesRegex(nrrd.NRRDError,
                                            'Invalid lineskip, allowed values are greater than or equal to'
                                            ' 0'):
                    nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)

        def test_missing_endianness(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Delete the endian field from header
                # Since our data is short (itemsize = 2), we should receive an error
                del header['endian']

                with self.assertRaisesRegex(nrrd.NRRDError, 'Header is missing required field: endian'):
                    nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)

        def test_big_endian(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Set endianness to big to verify it is doing correctly
                header['endian'] = 'big'

                data = nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)
                np.testing.assert_equal(data, self.expected_data.byteswap())

        def test_invalid_endian(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                np.testing.assert_equal(self.expected_header, header)

                # Set endianness to fake value
                header['endian'] = 'fake'

                with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid endian value in header: fake'):
                    nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)

        def test_invalid_index_order(self):
            with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid index order'):
                nrrd.read(RAW_NRRD_FILE_PATH, index_order=None)

        def test_read_quoted_string_header(self):
            header = nrrd.read_header([
                'NRRD0004',
                '# Complete NRRD file format specification at:',
                '# http://teem.sourceforge.net/nrrd/format.html',
                'type: double',
                'dimension: 3',
                'space dimension: 3',
                'sizes: 32 40 16',
                'encoding: raw',
                'units: "mm" "cm" "in"',
                'space units: "mm" "cm" "in"',
                'labels: "X" "Y" "f(log(X, 10), Y)"',
                'space origin: (-0.79487200000000002,-1,-0.38461499999999998)'
            ])

            # Check that the quoted values were appropriately parsed
            self.assertEqual(['mm', 'cm', 'in'], header['units'])
            self.assertEqual(['mm', 'cm', 'in'], header['space units'])
            self.assertEqual(['X', 'Y', 'f(log(X, 10), Y)'], header['labels'])

        def test_read_quoted_string_header_no_quotes(self):
            header = nrrd.read_header([
                'NRRD0004',
                '# Complete NRRD file format specification at:',
                '# http://teem.sourceforge.net/nrrd/format.html',
                'type: double',
                'dimension: 3',
                'space dimension: 3',
                'sizes: 32 40 16',
                'encoding: raw',
                'units: mm cm in',
                'space units: mm cm in',
                'labels: X Y f(log(X,10),Y)',
                'space origin: (-0.79487200000000002,-1,-0.38461499999999998)'
            ])

            # Check that the quoted values were appropriately parsed
            self.assertEqual(['mm', 'cm', 'in'], header['units'])
            self.assertEqual(['mm', 'cm', 'in'], header['space units'])
            self.assertEqual(['X', 'Y', 'f(log(X,10),Y)'], header['labels'])

        def test_read_memory(self):
            def test(filename: str):
                with open(filename, 'rb') as fh:
                    # Read into BytesIO and test that
                    x = fh.read()
                    memory_file = io.BytesIO(x)
                    memory_header = nrrd.read_header(memory_file)
                    memory_data = nrrd.read_data(memory_header, memory_file)

                    # Read normally via file handle
                    fh.seek(0)
                    expected_header = nrrd.read_header(fh)
                    expected_data = nrrd.read_data(expected_header, fh)

                    np.testing.assert_equal(expected_header, memory_header)
                    np.testing.assert_equal(expected_data, memory_data)

                    # Test that the data read is able to be edited
                    self.assertTrue(memory_data.flags['WRITEABLE'])

            paths = [
                RAW_NRRD_FILE_PATH,
                GZ_NRRD_FILE_PATH,
                GZ_BYTESKIP_NRRD_FILE_PATH,
                GZ_LINESKIP_NRRD_FILE_PATH,
                BZ2_NRRD_FILE_PATH,
                ASCII_1D_NRRD_FILE_PATH,
                ASCII_2D_NRRD_FILE_PATH,
                RAW_4D_NRRD_FILE_PATH,
            ]

            for filename in paths:
                with self.subTest(filename):
                    test(filename)

        def test_read_space_directions_list(self):
            try:
                nrrd.SPACE_DIRECTIONS_TYPE = 'double vector list'

                _, header = nrrd.read(RAW_4D_NRRD_FILE_PATH, index_order=self.index_order)
                self.assertIsInstance(header['space directions'], list)
                self.assertTrue(
                    all(vector is None or isinstance(vector, np.ndarray) for vector in header['space directions']))
                np.testing.assert_equal(header['space directions'][0].dtype, np.float64)
                np.testing.assert_equal(header['space directions'], [np.array([1.5, 0., 0.]),
                                        np.array([0., 1.5, 0.]),
                                        np.array([0., 0., 1.]),
                                        None])
            finally:
                nrrd.SPACE_DIRECTIONS_TYPE = 'double matrix'

        def test_file_parameter_not_closed(self):
            with open(RAW_NRRD_FILE_PATH, 'rb') as fh:
                header = nrrd.read_header(fh)
                nrrd.read_data(header, fh)
                self.assertFalse(fh.closed)


class TestReadingFunctionsFortran(Abstract.TestReadingFunctions):
    index_order = 'F'


class TestReadingFunctionsC(Abstract.TestReadingFunctions):
    index_order = 'C'


if __name__ == '__main__':
    unittest.main()
