import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
from nrrd.tests.util import *
import nrrd


class TestReadingFunctions(unittest.TestCase):
    def setUp(self):
        self.expected_header = {u'dimension': 3,
                                u'encoding': 'raw',
                                u'endian': 'little',
                                u'kinds': ['domain', 'domain', 'domain'],
                                u'sizes': np.array([30, 30, 30]),
                                u'space': 'left-posterior-superior',
                                u'space directions': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                                u'space origin': np.array([0, 0, 0]),
                                u'type': 'short'}

        self.expected_data = np.fromfile(RAW_DATA_FILE_PATH, np.int16).reshape((30, 30, 30), order='F')

    def test_read_header_only(self):
        with open(RAW_NRRD_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)

        # np.testing.assert_equal is used to compare the headers because it will appropriately handle each
        # value in the structure. Since some of the values can be Numpy arrays inside the headers, this must be
        # used to compare the two values.
        np.testing.assert_equal(self.expected_header, header)

    def test_read_header_only_with_filename(self):
        header = nrrd.read_header(RAW_NRRD_FILE_PATH)

        # np.testing.assert_equal is used to compare the headers because it will appropriately handle each
        # value in the structure. Since some of the values can be Numpy arrays inside the headers, this must be
        # used to compare the two values.
        np.testing.assert_equal(self.expected_header, header)

    def test_read_detached_header_only(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)

        with open(RAW_NHDR_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)

        np.testing.assert_equal(self.expected_header, header)

    def test_read_header_and_data_filename(self):
        data, header = nrrd.read(RAW_NRRD_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_detached_header_and_data(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)

        data, header = nrrd.read(RAW_NHDR_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_detached_header_and_data_with_byteskip_minus1(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        expected_header[u'byte skip'] = -1

        data, header = nrrd.read(RAW_BYTESKIP_NHDR_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_detached_header_and_nifti_data_with_byteskip_minus1(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        expected_header[u'byte skip'] = -1
        expected_header[u'encoding'] = 'gzip'
        expected_header[u'data file'] = 'BallBinary30x30x30.nii.gz'

        data, header = nrrd.read(GZ_BYTESKIP_NIFTI_NHDR_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_detached_header_and_nifti_data(self):
        with self.assertRaisesRegex(nrrd.NRRDError, 'Size of the data does not equal '
                                                    + 'the product of all the dimensions: 27000-27176=-176'):
            nrrd.read(GZ_NIFTI_NHDR_FILE_PATH)

    def test_read_detached_header_and_data_with_byteskip_minus5(self):
        with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid byteskip, allowed values '
                                                    + 'are greater than or equal to -1'):
            nrrd.read(RAW_INVALID_BYTESKIP_NHDR_FILE_PATH)

    def test_read_header_and_gz_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'

        data, header = nrrd.read(GZ_NRRD_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_header_and_gz_compressed_data_with_byteskip_minus1(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        expected_header[u'type'] = 'int16'
        expected_header[u'byte skip'] = -1

        data, header = nrrd.read(GZ_BYTESKIP_NRRD_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_header_and_bz2_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'bzip2'

        data, header = nrrd.read(BZ2_NRRD_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_header_and_gz_compressed_data_with_lineskip3(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        expected_header[u'line skip'] = 3

        data, header = nrrd.read(GZ_LINESKIP_NRRD_FILE_PATH)

        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_raw_header(self):
        expected_header = {u'type': 'float', u'dimension': 3, u'min': 0, u'max': 35.4}
        header = nrrd.read_header(('NRRD0005', 'type: float', 'dimension: 3', 'min: 0', 'max: 35.4'))
        self.assertEqual(expected_header, header)

        expected_header = {u'my extra info': u'my : colon-separated : values'}
        header = nrrd.read_header(('NRRD0005', 'my extra info:=my : colon-separated : values'))
        np.testing.assert_equal(expected_header, header)

    def test_read_dup_field_error_and_warn(self):
        expected_header = {u'type': 'float', u'dimension': 3}
        header_txt_tuple = ('NRRD0005', 'type: float', 'dimension: 3', 'type: float')

        with self.assertRaisesRegex(nrrd.NRRDError, "Duplicate header field: 'type'"):
            header = nrrd.read_header(header_txt_tuple)

        import warnings
        with warnings.catch_warnings(record=True) as w:
            nrrd.reader.ALLOW_DUPLICATE_FIELD = True
            header = nrrd.read_header(header_txt_tuple)

            self.assertTrue("Duplicate header field: 'type'" in str(w[0].message))

            self.assertEqual(expected_header, header)
            nrrd.reader.ALLOW_DUPLICATE_FIELD = False

    def test_read_header_and_ascii_1d_data(self):
        expected_header = {u'dimension': 1,
                           u'encoding': 'ASCII',
                           u'kinds': ['domain'],
                           u'sizes': [27],
                           u'spacings': [1.0458000000000001],
                           u'type': 'unsigned char'}

        data, header = nrrd.read(ASCII_1D_NRRD_FILE_PATH)

        self.assertEqual(header, expected_header)
        np.testing.assert_equal(data.dtype, np.uint8)
        np.testing.assert_equal(data, np.arange(1, 28))

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_read_header_and_ascii_2d_data(self):
        expected_header = {u'dimension': 2,
                           u'encoding': 'ASCII',
                           u'kinds': ['domain', 'domain'],
                           u'sizes': [3, 9],
                           u'spacings': [1.0458000000000001, 2],
                           u'type': 'unsigned short'}

        data, header = nrrd.read(ASCII_2D_NRRD_FILE_PATH)

        np.testing.assert_equal(header, expected_header)
        np.testing.assert_equal(data.dtype, np.uint16)
        np.testing.assert_equal(data, np.arange(1, 28).reshape(3, 9, order='F'))

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
                                                         [np.NaN, np.NaN, np.NaN]]),
                           'endian': 'little',
                           'encoding': 'raw',
                           'measurement frame': np.array([[1.0001, 0., 0.],
                                                          [0., 1.0000000006, 0.],
                                                          [0., 0., 1.000000000000009]])}

        data, header = nrrd.read(RAW_4D_NRRD_FILE_PATH)

        np.testing.assert_equal(header, expected_header)
        np.testing.assert_equal(data.dtype, np.float64)
        np.testing.assert_equal(header['measurement frame'].dtype, np.float64)
        np.testing.assert_equal(data, np.array([[[[0.76903426]]]]))

        # Test that the data read is able to be edited
        self.assertTrue(data.flags['WRITEABLE'])

    def test_custom_fields_without_field_map(self):
        expected_header = {u'dimension': 1,
                           u'encoding': 'ASCII',
                           u'kinds': ['domain'],
                           u'sizes': [27],
                           u'spacings': [1.0458000000000001],
                           u'int': '24',
                           u'double': '25.5566',
                           u'string': 'This is a long string of information that is important.',
                           u'int list': '1 2 3 4 5 100',
                           u'double list': '0.2 0.502 0.8',
                           u'string list': 'words are split by space in list',
                           u'int vector': '(100, 200, -300)',
                           u'double vector': '(100.5,200.3,-300.99)',
                           u'int matrix': '(1,0,0) (0,1,0) (0,0,1)',
                           u'double matrix': '(1.2,0.3,0) (0,1.5,0) (0,-0.55,1.6)',
                           u'type': 'unsigned char'}

        header = nrrd.read_header(ASCII_1D_CUSTOM_FIELDS_FILE_PATH)

        self.assertEqual(header, expected_header)

    def test_custom_fields_with_field_map(self):
        expected_header = {u'dimension': 1,
                           u'encoding': 'ASCII',
                           u'kinds': ['domain'],
                           u'sizes': [27],
                           u'spacings': [1.0458000000000001],
                           u'int': 24,
                           u'double': 25.5566,
                           u'string': 'This is a long string of information that is important.',
                           u'int list': np.array([1, 2, 3, 4, 5, 100]),
                           u'double list': np.array([0.2, 0.502, 0.8]),
                           u'string list': ['words', 'are', 'split', 'by', 'space', 'in', 'list'],
                           u'int vector': np.array([100, 200, -300]),
                           u'double vector': np.array([100.5, 200.3, -300.99]),
                           u'int matrix': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                           u'double matrix': np.array([[1.2, 0.3, 0.0], [0.0, 1.5, 0.0], [0.0, -0.55, 1.6]]),
                           u'type': 'unsigned char'}

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
        with self.assertRaisesRegex(nrrd.NRRDError, 'Unsupported NRRD file version \\(version: 2000\\). This library '
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

            with self.assertRaisesRegex(nrrd.NRRDError, 'Header is missing required field: "type".'):
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

            with self.assertRaisesRegex(nrrd.NRRDError, 'Unsupported encoding: "fake"'):
                nrrd.read_data(header, fh, RAW_NRRD_FILE_PATH)


if __name__ == '__main__':
    unittest.main()
