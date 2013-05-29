import nrrd
import unittest
import os
from os.path import dirname, join, basename

DATA_DIR_PATH  = os.path.dirname(__file__) 
RAW_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nrrd')
RAW_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nhdr')
RAW_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.raw')
GZ_NRRD_FILE_PATH  = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz.nrrd')
BZ2_NRRD_FILE_PATH  = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_bz2.nrrd')
GZ_LINESKIP_NRRD_FILE_PATH  = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz_lineskip.nrrd')

class TestReadingFunctions(unittest.TestCase):

    def setUp(self):
        self.expected_header = {'dimension': 3,
                                'encoding': 'raw',
                                'endian': 'little',
                                'keyvaluepairs': {},
                                'kinds': ['domain', 'domain', 'domain'],
                                'sizes': [30, 30, 30],
                                'space': 'left-posterior-superior',
                                'space directions': [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
                                'space origin': [0.0, 0.0, 0.0],
                                'type': 'short'}
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
        expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        with open(RAW_NHDR_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)
        self.assertEqual(self.expected_header, header)

    def test_read_header_and_data(self):
        data, header = nrrd.read(RAW_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_detached_header_and_data(self):
        expected_header = self.expected_header
        expected_header['data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        data, header = nrrd.read(RAW_NHDR_FILE_PATH)
        self.assertEqual(expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_gz_compressed_data(self):
        expected_header = self.expected_header
        expected_header['encoding'] = 'gzip'
        data, header = nrrd.read(GZ_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_bz2_compressed_data(self):
        expected_header = self.expected_header
        expected_header['encoding'] = 'bzip2'
        data, header = nrrd.read(BZ2_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_gz_compressed_data_with_lineskip3(self):
        expected_header = self.expected_header
        expected_header['encoding'] = 'gzip'
        expected_header['line skip'] = 3
        data, header = nrrd.read(GZ_LINESKIP_NRRD_FILE_PATH)
        self.assertEqual(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

if __name__ == '__main__':
    unittest.main()
