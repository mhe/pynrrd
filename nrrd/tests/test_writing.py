import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import tempfile
import numpy as np
from nrrd.tests.util import *
import nrrd


class TestWritingFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_write_dir = tempfile.mkdtemp('nrrdtest')
        self.data_input, _ = nrrd.read(RAW_NRRD_FILE_PATH)

        with open(RAW_DATA_FILE_PATH, 'rb') as f:
            self.expected_data = f.read()

    def write_and_read_back_with_encoding(self, encoding, level=9):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_{}_{}.nrrd'.format(encoding, str(level)))
        nrrd.write(output_filename, self.data_input, {u'encoding': encoding},
                   compression_level=level)

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], encoding)

        return output_filename

    def test_write_raw(self):
        self.write_and_read_back_with_encoding(u'raw')

    def test_write_gz(self):
        self.write_and_read_back_with_encoding(u'gzip')

    def test_write_bzip2(self):
        self.write_and_read_back_with_encoding(u'bzip2')

    def test_write_gz_level1(self):
        import os
        fn = self.write_and_read_back_with_encoding(u'gzip', level=1)

        self.assertLess(os.path.getsize(GZ_NRRD_FILE_PATH), os.path.getsize(fn))

    def test_write_bzip2_level1(self):
        fn = self.write_and_read_back_with_encoding(u'bzip2', level=1)

        # note: we don't currently assert reduction here, because with the binary ball test data,
        #       the output size does not change at different bz2 levels.
        # self.assertLess(os.path.getsize(BZ2_NRRD_FILE_PATH), os.path.getsize(fn))

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

    def test_write_custom_fields_without_custom_field_map(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_custom_fields.nrrd')

        data, header = nrrd.read(ASCII_1D_CUSTOM_FIELDS_FILE_PATH)
        nrrd.write(output_filename, data, header)

        with open(output_filename, 'r') as fh:
            lines = fh.readlines()

            # Strip newline from end of line
            lines = [line.rstrip() for line in lines]

            self.assertEqual(lines[5], 'type: uint8')
            self.assertEqual(lines[6], 'dimension: 1')
            self.assertEqual(lines[7], 'sizes: 27')
            self.assertEqual(lines[8], 'kinds: domain')
            self.assertEqual(lines[9], 'encoding: ASCII')
            self.assertEqual(lines[10], 'spacings: 1.0458000000000001')
            self.assertEqual(lines[11], 'int:=24')
            self.assertEqual(lines[12], 'double:=25.5566')
            self.assertEqual(lines[13], 'string:=This is a long string of information that is important.')
            self.assertEqual(lines[14], 'int list:=1 2 3 4 5 100')
            self.assertEqual(lines[15], 'double list:=0.2 0.502 0.8')
            self.assertEqual(lines[16], 'string list:=words are split by space in list')
            self.assertEqual(lines[17], 'int vector:=(100, 200, -300)')
            self.assertEqual(lines[18], 'double vector:=(100.5,200.3,-300.99)')
            self.assertEqual(lines[19], 'int matrix:=(1,0,0) (0,1,0) (0,0,1)')
            self.assertEqual(lines[20], 'double matrix:=(1.2,0.3,0) (0,1.5,0) (0,-0.55,1.6)')

    def test_write_custom_fields_with_custom_field_map(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_custom_fields.nrrd')

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

        data, header = nrrd.read(ASCII_1D_CUSTOM_FIELDS_FILE_PATH, custom_field_map)
        nrrd.write(output_filename, data, header, custom_field_map=custom_field_map)

        with open(output_filename, 'r') as fh:
            lines = fh.readlines()

            # Strip newline from end of line
            lines = [line.rstrip() for line in lines]

            self.assertEqual(lines[5], 'type: uint8')
            self.assertEqual(lines[6], 'dimension: 1')
            self.assertEqual(lines[7], 'sizes: 27')
            self.assertEqual(lines[8], 'kinds: domain')
            self.assertEqual(lines[9], 'encoding: ASCII')
            self.assertEqual(lines[10], 'spacings: 1.0458000000000001')
            self.assertEqual(lines[11], 'int:=24')
            self.assertEqual(lines[12], 'double:=25.5566')
            self.assertEqual(lines[13], 'string:=This is a long string of information that is important.')
            self.assertEqual(lines[14], 'int list:=1 2 3 4 5 100')
            self.assertEqual(lines[15], 'double list:=0.20000000000000001 0.502 0.80000000000000004')
            self.assertEqual(lines[16], 'string list:=words are split by space in list')
            self.assertEqual(lines[17], 'int vector:=(100,200,-300)')
            self.assertEqual(lines[18], 'double vector:=(100.5,200.30000000000001,-300.99000000000001)')
            self.assertEqual(lines[19], 'int matrix:=(1,0,0) (0,1,0) (0,0,1)')
            self.assertEqual(lines[20], 'double matrix:=(1.2,0.29999999999999999,0) (0,1.5,0) (0,-0.55000000000000004,'
                                        '1.6000000000000001)')

    def test_write_detached_raw_as_nrrd(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nhdr')
        output_data_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nrrd')

        nrrd.write(output_data_filename, self.data_input, {u'encoding': 'raw'}, detached_header=True)

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], 'raw')
        self.assertEqual(header['data file'], output_data_filename)

    def test_write_detached_raw_odd_extension(self):
        output_data_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nrrd2')

        nrrd.write(output_data_filename, self.data_input, {u'encoding': 'raw'}, detached_header=True)

        # Read back the same file
        data, header = nrrd.read(output_data_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], 'raw')
        self.assertEqual('data file' in header, False)

    def test_write_detached_raw_odd_extension(self):
        output_data_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nrrd2')

        nrrd.write(output_data_filename, self.data_input, {u'encoding': 'raw'}, detached_header=True)

        # Read back the same file
        data, header = nrrd.read(output_data_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], 'raw')
        self.assertEqual('data file' in header, False)

    def test_write_fake_encoding(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nhdr')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Invalid encoding specification while writing NRRD file: fake'):
            nrrd.write(output_filename, self.data_input, {u'encoding': 'fake'})

    def test_write_detached_gz(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nhdr')
        output_data_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.raw.gz')

        nrrd.write(output_filename, self.data_input, {u'encoding': 'gz'}, detached_header=False)

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], 'gz')
        self.assertEqual(header['data file'], output_data_filename)

    def test_write_detached_bz2(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nhdr')
        output_data_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.raw.bz2')

        nrrd.write(output_filename, self.data_input, {u'encoding': 'bz2'}, detached_header=False)

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], 'bz2')
        self.assertEqual(header['data file'], output_data_filename)

    def test_write_detached_ascii(self):
        output_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.nhdr')
        output_data_filename = os.path.join(self.temp_write_dir, 'testfile_detached_raw.txt')

        nrrd.write(output_filename, self.data_input, {u'encoding': 'txt'}, detached_header=False)

        # Read back the same file
        data, header = nrrd.read(output_filename)
        self.assertEqual(self.expected_data, data.tostring(order='F'))
        self.assertEqual(header['encoding'], 'txt')
        self.assertEqual(header['data file'], output_data_filename)


if __name__ == '__main__':
    unittest.main()
