import os
import sys
import tempfile

import numpy as np

# Look on level up for nrrd.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import nrrd
import unittest

DATA_DIR_PATH = os.path.dirname(__file__)
RAW_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nrrd')
RAW_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nhdr')
RAW_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.raw')
GZ_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz.nrrd')
BZ2_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_bz2.nrrd')
GZ_LINESKIP_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz_lineskip.nrrd')

ASCII_1D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test1d_ascii.nrrd')
ASCII_2D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test2d_ascii.nrrd')


class TestReadingFunctions(unittest.TestCase):
    def setUp(self):
        self.expected_header = {u'dimension': 3,
                                u'encoding': 'raw',
                                u'endian': 'little',
                                u'keyvaluepairs': {},
                                u'kinds': ['domain', 'domain', 'domain'],
                                u'sizes': [30, 30, 30],
                                u'space': 'left-posterior-superior',
                                u'space directions': [['1', '0', '0'], ['0', '1', '0'], ['0', '0', '1']],
                                u'space origin': ['0', '0', '0'],
                                u'type': 'short'}
        with open(RAW_DATA_FILE_PATH, 'rb') as f:
            self.expected_data = f.read()

    def test_read_header_only(self):
        header = None
        with open(RAW_NRRD_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)
        self.assertEqual(self.expected_header, header)

    def test_read_detached_header_only(self):
        header = None
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        with open(RAW_NHDR_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)
        self.assertEqual(self.expected_header, header)

    def test_read_detached_header_only_filename(self):
        try:
            assertRaisesRegex = self.assertRaisesRegex  # Python 3
        except AttributeError:
            assertRaisesRegex = self.assertRaisesRegexp  # Python 2
        with assertRaisesRegex(nrrd.NrrdError, 'Missing magic "NRRD" word. Is this an NRRD file\?'):
            nrrd.read_header(RAW_NHDR_FILE_PATH)

    def test_read_header_and_data_filename(self):
        data, header = nrrd.read(RAW_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_detached_header_and_data(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        data, header = nrrd.read(RAW_NHDR_FILE_PATH)
        self.assertEqual(expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_gz_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        data, header = nrrd.read(GZ_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_bz2_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'bzip2'
        data, header = nrrd.read(BZ2_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_gz_compressed_data_with_lineskip3(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        expected_header[u'line skip'] = 3
        data, header = nrrd.read(GZ_LINESKIP_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_raw_header(self):
        expected_header = {u'type': 'float', u'dimension': 3, u'keyvaluepairs': {}}
        header = nrrd.read_header(("NRRD0005", "type: float", "dimension: 3"))
        self.assertEqual(expected_header, header)

        expected_header = {u'keyvaluepairs': {u'my extra info': u'my : colon-separated : values'}}
        header = nrrd.read_header(("NRRD0005", "my extra info:=my : colon-separated : values"))
        self.assertEqual(expected_header, header)

    def test_read_header_and_ascii_1d_data(self):
        expected_header = {u'dimension': 1,
                           u'encoding': 'ascii',
                           u'keyvaluepairs': {},
                           u'kinds': ['domain'],
                           u'sizes': [27],
                           u'spacings': ['1.0458000000000001'],
                           u'type': 'unsigned char'}

        data, header = nrrd.read(ASCII_1D_NRRD_FILE_PATH)

        self.assertEqual(header, expected_header)
        np.testing.assert_equal(data.dtype, np.uint8)
        np.testing.assert_equal(data, np.arange(1, 28))

    def test_read_header_and_ascii_2d_data(self):
        expected_header = {u'dimension': 2,
                           u'encoding': 'ascii',
                           u'keyvaluepairs': {},
                           u'kinds': ['domain', 'domain'],
                           u'sizes': [3, 9],
                           u'spacings': ['1.0458000000000001', '2'],
                           u'type': 'unsigned short'}

        data, header = nrrd.read(ASCII_2D_NRRD_FILE_PATH)

        self.assertEqual(header, expected_header)
        np.testing.assert_equal(data.dtype, np.uint16)
        np.testing.assert_equal(data, np.arange(1, 28).reshape(3, 9, order='F'))


class TestWritingFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_write_dir = tempfile.mkdtemp("nrrdtest")
        self.data_input, _ = nrrd.read(RAW_NRRD_FILE_PATH)
        with open(RAW_DATA_FILE_PATH, 'rb') as f:
            self.expected_data = f.read()

    def write_and_read_back_with_encoding(self, encoding):
        output_filename = os.path.join(self.temp_write_dir, "testfile_%s.nrrd" % encoding)
        nrrd.write(output_filename, self.data_input, {u'encoding': encoding})
        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], encoding)

    def test_write_raw(self):
        self.write_and_read_back_with_encoding(u'raw')

    def test_write_gz(self):
        self.write_and_read_back_with_encoding(u'gzip')

    def test_write_bz2(self):
        self.write_and_read_back_with_encoding(u'bzip2')

    def test_write_ascii_1d(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_ascii_1d.nrrd')

        x = np.arange(1, 28)
        nrrd.write(output_filename, x, {u'encoding': 'ascii'})

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(header['encoding'], 'ascii')
        np.testing.assert_equal(data, x)

    def test_write_ascii_2d(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_ascii_2d.nrrd')

        x = np.arange(1, 28).reshape(3, 9, order='F')
        nrrd.write(output_filename, x, {u'encoding': 'ascii'})

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(header['encoding'], 'ascii')
        np.testing.assert_equal(data, x)

    def test_write_ascii_3d(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_ascii_3d.nrrd')

        x = np.arange(1, 28).reshape(3, 3, 3, order='F')
        nrrd.write(output_filename, x, {u'encoding': 'ascii'})

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(header['encoding'], 'ascii')
        np.testing.assert_equal(x, data)


if __name__ == '__main__':
    unittest.main()
