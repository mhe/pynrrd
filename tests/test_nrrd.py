import nrrd
import unittest

class TestReadingFunctions(unittest.TestCase):

    def setUp(self):
        self.input_nrrd = 'BallBinary30x30x30.nrrd'
        self.input_nhdr = 'BallBinary30x30x30.nhdr'
        self.input_data_file = 'BallBinary30x30x30.raw'
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

    def test_read_header_only(self):
        header = None
        with open(self.input_nrrd, 'rb') as f:
            header = nrrd.read_header(f)
        self.assertEqual(self.expected_header, header)

    def test_read_detached_header_only(self):
        header = None
        expected_header = self.expected_header
        expected_header['data file'] = self.input_data_file
        with open(self.input_nhdr, 'rb') as f:
            header = nrrd.read_header(f)
        self.assertEqual(self.expected_header, header)

if __name__ == '__main__':
    unittest.main()
