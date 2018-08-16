import tempfile
import unittest
import nrrd
import numpy as np
from nrrd.tests.util import *

class TestWritingFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_write_dir = tempfile.mkdtemp('nrrdtest')
        self.data_input, _ = nrrd.read(RAW_NRRD_FILE_PATH)
        with open(RAW_DATA_FILE_PATH, 'rb') as f:
            self.expected_data = f.read()

    def write_and_read_back_with_encoding(self, encoding):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_%s.nrrd' % encoding)
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
