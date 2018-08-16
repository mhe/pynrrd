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
                                u'keyvaluepairs': {},
                                u'kinds': ['domain', 'domain', 'domain'],
                                u'sizes': np.array([30, 30, 30]),
                                u'space': 'left-posterior-superior',
                                u'space directions': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                                u'space origin': np.array([0, 0, 0]),
                                u'type': 'short'}

        self.expected_data = np.fromfile(RAW_DATA_FILE_PATH, np.int16).reshape((30, 30, 30), order='F')

    def test_read_header_only(self):
        header = None
        with open(RAW_NRRD_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)

        # np.testing.assert_equal is used to compare the headers because it will appropriately handle each
        # value in the structure. Since some of the values can be Numpy arrays inside the headers, this must be
        # used to compare the two values.
        np.testing.assert_equal(self.expected_header, header)

    def test_read_detached_header_only(self):
        header = None
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        with open(RAW_NHDR_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)
        np.testing.assert_equal(self.expected_header, header)

    def test_read_detached_header_only_filename(self):
        with self.assertRaisesRegex(nrrd.NrrdError, 'Missing magic "NRRD" word. Is this an NRRD file\?'):
            nrrd.read_header(RAW_NHDR_FILE_PATH)

    def test_read_header_and_data_filename(self):
        data, header = nrrd.read(RAW_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

    def test_read_detached_header_and_data(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        data, header = nrrd.read(RAW_NHDR_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

    def test_read_header_and_gz_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        data, header = nrrd.read(GZ_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

    def test_read_header_and_bz2_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'bzip2'
        data, header = nrrd.read(BZ2_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

    def test_read_header_and_gz_compressed_data_with_lineskip3(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        expected_header[u'line skip'] = 3
        data, header = nrrd.read(GZ_LINESKIP_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        np.testing.assert_equal(data, self.expected_data)

    def test_read_raw_header(self):
        expected_header = {u'type': 'float', u'dimension': 3, u'keyvaluepairs': {}}
        header = nrrd.read_header(('NRRD0005', 'type: float', 'dimension: 3'))
        self.assertEqual(expected_header, header)

        expected_header = {u'keyvaluepairs': {u'my extra info': u'my : colon-separated : values'}}
        header = nrrd.read_header(('NRRD0005', 'my extra info:=my : colon-separated : values'))
        np.testing.assert_equal(expected_header, header)

    def test_read_header_and_ascii_1d_data(self):
        expected_header = {u'dimension': 1,
                           u'encoding': 'ascii',
                           u'keyvaluepairs': {},
                           u'kinds': ['domain'],
                           u'sizes': [27],
                           u'spacings': [1.0458000000000001],
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
                           u'spacings': [1.0458000000000001, 2],
                           u'type': 'unsigned short'}

        data, header = nrrd.read(ASCII_2D_NRRD_FILE_PATH)

        np.testing.assert_equal(header, expected_header)
        np.testing.assert_equal(data.dtype, np.uint16)
        np.testing.assert_equal(data, np.arange(1, 28).reshape(3, 9, order='F'))

    def test_read_simple_4d_nrrd(self):
        expected_header = {'keyvaluepairs': {},
                           'type': 'double',
                           'dimension': 4,
                           'space': 'right-anterior-superior',
                           'sizes': np.array([1, 1, 1, 1]),
                           'space directions': np.array([[1.5, 0., 0.],
                                                         [0., 1.5, 0.],
                                                         [0., 0., 1.],
                                                         [np.NaN, np.NaN, np.NaN]]),
                           'endian': 'little',
                           'encoding': 'raw',
                           'measurement frame': np.array([[1., 0., 0.],
                                                          [0., 1., 0.],
                                                          [0., 0., 1.]])}

        data, header = nrrd.read(RAW_4D_NRRD_FILE_PATH)

        np.testing.assert_equal(header, expected_header)
        np.testing.assert_equal(data.dtype, np.float64)
        np.testing.assert_equal(data, np.array([[[[0.76903426]]]]))


if __name__ == '__main__':
    unittest.main()
