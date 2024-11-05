import unittest

import numpy as np

import nrrd


class TestFieldParsing(unittest.TestCase):
    def setUp(self):
        pass

    def assert_equal_with_datatype(self, desired, actual):
        if isinstance(desired, list):
            self.assertEqual(desired[0].dtype, np.array(actual[0]).dtype)
        else:
            self.assertEqual(desired.dtype, np.array(actual[0]).dtype)
        np.testing.assert_equal(desired, actual)

    def test_parse_vector(self):
        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector should be enclosed by parentheses.'):
            nrrd.parse_vector('100, 200, 300)')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector should be enclosed by parentheses.'):
            nrrd.parse_vector('(100, 200, 300')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector should be enclosed by parentheses.'):
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

        with self.assertRaisesRegex(nrrd.NRRDError, 'dtype should be None for automatic type detection, float or int'):
            nrrd.parse_vector('(100.47655, 220.32)', dtype=np.uint8)

    def test_parse_optional_vector(self):
        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector should be enclosed by parentheses.'):
            nrrd.parse_optional_vector('100, 200, 300)')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector should be enclosed by parentheses.'):
            nrrd.parse_optional_vector('(100, 200, 300')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector should be enclosed by parentheses.'):
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

        with self.assertRaisesRegex(nrrd.NRRDError, 'dtype should be None for automatic type detection, float or int'):
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

        with self.assertRaisesRegex(nrrd.NRRDError, 'Matrix should have same number of elements in each row'):
            nrrd.parse_matrix('(1,0,0,0) (0,1,0) (0,0,1)')

        with self.assertRaisesRegex(nrrd.NRRDError, 'dtype should be None for automatic type detection, float or int'):
            nrrd.parse_matrix('(1,0,0) (0,1,0) (0,0,1)', dtype=np.uint8)

    def test_parse_optional_matrix(self):
        self.assert_equal_with_datatype(nrrd.parse_optional_matrix(
            '(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(nrrd.parse_optional_matrix('(1,0,0) (0,1,0) (0,0,1)'),
                                        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])

        self.assert_equal_with_datatype(nrrd.parse_optional_matrix(
            'none (1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[np.nan, np.nan, np.nan], [1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0],
             [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(nrrd.parse_optional_matrix(
            '(1.4726600000000003,-0,0) none (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [np.nan, np.nan, np.nan], [0, 1.4726600000000003, 0],
             [0, 0, 4.7619115092114601]])

        with self.assertRaisesRegex(nrrd.NRRDError, 'Matrix should have same number of elements in each row'):
            nrrd.parse_optional_matrix('(1,0,0,0) (0,1,0) (0,0,1)')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Matrix should have same number of elements in each row'):
            nrrd.parse_optional_matrix('none (1,0,0,0) (0,1,0) (0,0,1)')

    def test_parse_number_list_int(self):
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4'), [1, 2, 3, 4])
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4', dtype=float), [1., 2., 3., 4.])
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4', dtype=int), [1, 2, 3, 4])

        self.assert_equal_with_datatype(nrrd.parse_number_list('1'), [1])

        with self.assertRaisesRegex(nrrd.NRRDError, 'dtype should be None for automatic type detection, float or int'):
            nrrd.parse_number_list('1 2 3 4', dtype=np.uint8)

    def test_parse_number_list_float(self):
        self.assert_equal_with_datatype(nrrd.parse_number_list('1.5 2 3 4'), [1.5, 2., 3., 4.])
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2 3 4.9', dtype=float), [1., 2., 3., 4.9])
        self.assert_equal_with_datatype(nrrd.parse_number_list('1 2.9 3 4', dtype=int), [1, 2, 3, 4])

        self.assert_equal_with_datatype(nrrd.parse_number_list('1.3'), [1.3])

    def test_parse_number_auto_dtype(self):
        self.assertEqual(nrrd.parse_number_auto_dtype('25'), 25)
        self.assertEqual(nrrd.parse_number_auto_dtype('25.125'), 25.125)

    def test_parse_vector_list(self):
        self.assert_equal_with_datatype(
            nrrd.parse_vector_list('(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(
            nrrd.parse_vector_list('(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)',
                                   dtype=float),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(
            nrrd.parse_vector_list('(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)',
                                   dtype=int), [[1, 0, 0], [0, 1, 0], [0, 0, 4]])

        self.assert_equal_with_datatype(nrrd.parse_vector_list('(1,0,0) (0,1,0) (0,0,1)'),
                                        [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.assert_equal_with_datatype(nrrd.parse_vector_list('(1,0,0) (0,1,0) (0,0,1)', dtype=float),
                                        [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        self.assert_equal_with_datatype(nrrd.parse_vector_list('(1,0,0) (0,1,0) (0,0,1)', dtype=int),
                                        [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector list should have same number of elements in each row'):
            nrrd.parse_vector_list('(1,0,0,0) (0,1,0) (0,0,1)')

        with self.assertRaisesRegex(nrrd.NRRDError, 'dtype should be None for automatic type detection, float or int'):
            nrrd.parse_vector_list('(1,0,0) (0,1,0) (0,0,1)', dtype=np.uint8)

        vector_list = nrrd.parse_vector_list('(1,0,0) (0,1,0) (0,0,1)')
        self.assertIsInstance(vector_list, list)
        self.assertTrue(all(isinstance(vector, np.ndarray) for vector in vector_list))

    def test_parse_optional_vector_list(self):
        self.assert_equal_with_datatype(nrrd.parse_optional_vector_list(
            '(1.4726600000000003,-0,0) (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(nrrd.parse_optional_vector_list('(1,0,0) (0,1,0) (0,0,1)'),
                                        [[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        self.assert_equal_with_datatype(nrrd.parse_optional_vector_list(
            '(1.4726600000000003,-0,0) none (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], None, [0, 1.4726600000000003, 0],
             [0, 0, 4.7619115092114601]])

        self.assert_equal_with_datatype(nrrd.parse_optional_vector_list(
            '(1.4726600000000003,-0,0) none (-0,1.4726600000000003,-0) (0,-0,4.7619115092114601)'),
            [[1.4726600000000003, 0, 0], None, [0, 1.4726600000000003, 0], [0, 0, 4.7619115092114601]])

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector list should have same number of elements in each row'):
            nrrd.parse_optional_vector_list('(1,0,0,0) (0,1,0) (0,0,1)')

        with self.assertRaisesRegex(nrrd.NRRDError, 'Vector list should have same number of elements in each row'):
            nrrd.parse_optional_vector_list('none (1,0,0,0) (0,1,0) (0,0,1)')

        vector_list = nrrd.parse_optional_vector_list('(1,0,0) (0,1,0) none (0,0,1)')
        self.assertIsInstance(vector_list, list)
        self.assertTrue(all(vector is None or isinstance(vector, np.ndarray) for vector in vector_list))


if __name__ == '__main__':
    unittest.main()
