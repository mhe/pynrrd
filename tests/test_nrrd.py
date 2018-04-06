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

# Fix issue with assertRaisesRegex only available in Python 3 while
# assertRaisesRegexp is available in Python 2 (and deprecated in Python 3)
if not hasattr(unittest.TestCase, 'assertRaisesRegex'):
    unittest.TestCase.assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegexp')


class TestFieldParsing(unittest.TestCase):
    def setUp(self):
        pass

    def assert_equal_with_datatype(self, desired, actual):
        self.assertEqual(desired.dtype, np.array(actual[0]).dtype)
        np.testing.assert_equal(desired, actual)

    def test_parse_vector(self):
        with self.assertRaisesRegex(nrrd.NrrdError, "Vector should be enclosed by parentheses."):
            nrrd.parse_vector('100, 200, 300)')

        with self.assertRaisesRegex(nrrd.NrrdError, "Vector should be enclosed by parentheses."):
            nrrd.parse_vector('(100, 200, 300')

        with self.assertRaisesRegex(nrrd.NrrdError, "Vector should be enclosed by parentheses."):
            nrrd.parse_vector('100, 200, 300')

        self.assert_equal_with_datatype(nrrd.parse_vector('(100, 200, 300)'), [100, 200, 300])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100, 200, 300)', dtype=float), [100., 200., 300.])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100, 200, 300)', dtype=int), [100, 200, 300])

        self.assert_equal_with_datatype(nrrd.parse_vector('(100.50, 200, 300)'), [100.50, 200., 300.])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100, 200.50, 300)', dtype=float), [100., 200.50, 300.])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100, 200, 300.50)', dtype=int), [100, 200, 300])

        self.assert_equal_with_datatype(nrrd.parse_vector('(100.47655, 220.32, 300.50)'), [100.47655, 220.32, 300.50])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100.47655, 220.32, 300.50)', dtype=float),
                                        [100.47655, 220.32, 300.50])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100.47655, 220.32, 300.50)', dtype=int), [100, 220, 300])

        self.assert_equal_with_datatype(nrrd.parse_vector('(100.47655, 220.32)'), [100.47655, 220.32])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100.47655, 220.32)', dtype=float), [100.47655, 220.32])
        self.assert_equal_with_datatype(nrrd.parse_vector('(100.47655, 220.32)', dtype=int), [100, 220])

        with self.assertRaisesRegex(nrrd.NrrdError, "dtype should be None for automatic type detection, float or int"):
            nrrd.parse_vector('(100.47655, 220.32)', dtype=np.uint8)

    def test_parse_optional_vector(self):
        with self.assertRaisesRegex(nrrd.NrrdError, "Vector should be enclosed by parentheses."):
            nrrd.parse_optional_vector('100, 200, 300)')

        with self.assertRaisesRegex(nrrd.NrrdError, "Vector should be enclosed by parentheses."):
            nrrd.parse_optional_vector('(100, 200, 300')

        with self.assertRaisesRegex(nrrd.NrrdError, "Vector should be enclosed by parentheses."):
            nrrd.parse_optional_vector('100, 200, 300')

        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100, 200, 300)'), [100, 200, 300])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100, 200, 300)', dtype=float),
                                        [100., 200., 300.])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100, 200, 300)', dtype=int), [100, 200, 300])

        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.50, 200, 300)'), [100.50, 200., 300.])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100, 200.50, 300)', dtype=float),
                                        [100., 200.50, 300.])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100, 200, 300.50)', dtype=int),
                                        [100, 200, 300])

        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.47655, 220.32, 300.50)'),
                                        [100.47655, 220.32, 300.50])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.47655, 220.32, 300.50)', dtype=float),
                                        [100.47655, 220.32, 300.50])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.47655, 220.32, 300.50)', dtype=int),
                                        [100, 220, 300])

        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.47655, 220.32)'),
                                        [100.47655, 220.32])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.47655, 220.32)', dtype=float),
                                        [100.47655, 220.32])
        self.assert_equal_with_datatype(nrrd.parse_optional_vector('(100.47655, 220.32)', dtype=int), [100, 220])

        self.assertEqual(nrrd.parse_optional_vector('none'), None)

        with self.assertRaisesRegex(nrrd.NrrdError, "dtype should be None for automatic type detection, float or int"):
            nrrd.parse_optional_vector('(100.47655, 220.32)', dtype=np.uint8)

    def test_parse_matrix(self):
        self.assert_equal_with_datatype(
            nrrd.parse_matrix('(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(
            nrrd.parse_matrix('(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)',
                              dtype=float),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(
            nrrd.parse_matrix('(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)',
                              dtype=int), [[1, 0, 0], [0, 1, 0], [0, 0, 4]])

        self.assert_equal_with_datatype(nrrd.parse_matrix('(1,0,0) (0,1,0) (0,0,1)'),
                                        [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.assert_equal_with_datatype(nrrd.parse_matrix('(1,0,0) (0,1,0) (0,0,1)', dtype=float),
                                        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        self.assert_equal_with_datatype(nrrd.parse_matrix('(1,0,0) (0,1,0) (0,0,1)', dtype=int),
                                        [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        with self.assertRaisesRegex(nrrd.NrrdError, "dtype should be None for automatic type detection, float or int"):
            nrrd.parse_matrix('(1,0,0) (0,1,0) (0,0,1)', dtype=np.uint8)

    def test_parse_optional_matrix(self):
        self.assert_equal_with_datatype(nrrd.parse_optional_matrix(
            '(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(nrrd.parse_optional_matrix('(1,0,0) (0,1,0) (0,0,1)'),
                                        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])

        self.assert_equal_with_datatype(nrrd.parse_optional_matrix(
            'none (1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[np.NaN, np.NaN, np.NaN], [1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0],
             [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(nrrd.parse_optional_matrix(
            '(1.4726600000000003,-0,0) none (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [np.NaN, np.NaN, np.NaN], [0, 1.4726600000000003, 0],
             [0, 0, 4.7619115092114601]])


    def test_parse_number_list(self):
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4'), [1, 2, 3, 4])
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4', dtype=float), [1., 2., 3., 4.])
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4', dtype=int), [1, 2, 3, 4])

        self.assert_equal_with_datatype(nrrd.parse_number_list('1'), [1])

        with self.assertRaisesRegex(nrrd.NrrdError, "dtype should be None for automatic type detection, float or int"):
            nrrd.parse_number_list('1 2 3 4', dtype=np.uint8)

        # print(nrrd.parse_number_auto_dtype('25'))


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
        with open(RAW_DATA_FILE_PATH, 'rb') as f:
            self.expected_data = f.read()

    def test_read_header_only(self):
        header = None
        with open(RAW_NRRD_FILE_PATH, 'rb') as f:
            header = nrrd.read_header(f)
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
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_detached_header_and_data(self):
        expected_header = self.expected_header
        expected_header[u'data file'] = os.path.basename(RAW_DATA_FILE_PATH)
        data, header = nrrd.read(RAW_NHDR_FILE_PATH)

        np.testing.assert_equal(expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_gz_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        data, header = nrrd.read(GZ_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_bz2_compressed_data(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'bzip2'
        data, header = nrrd.read(BZ2_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_header_and_gz_compressed_data_with_lineskip3(self):
        expected_header = self.expected_header
        expected_header[u'encoding'] = 'gzip'
        expected_header[u'line skip'] = 3
        data, header = nrrd.read(GZ_LINESKIP_NRRD_FILE_PATH)
        np.testing.assert_equal(self.expected_header, header)
        self.assertEqual(self.expected_data, data.tostring(order='F'))

    def test_read_raw_header(self):
        expected_header = {u'type': 'float', u'dimension': 3, u'keyvaluepairs': {}}
        header = nrrd.read_header(("NRRD0005", "type: float", "dimension: 3"))
        self.assertEqual(expected_header, header)

        expected_header = {u'keyvaluepairs': {u'my extra info': u'my : colon-separated : values'}}
        header = nrrd.read_header(("NRRD0005", "my extra info:=my : colon-separated : values"))
        self.assertEqual(expected_header, header)


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


if __name__ == '__main__':
    unittest.main()
