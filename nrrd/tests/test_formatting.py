import unittest

import numpy as np

import nrrd


class TestFieldFormatting(unittest.TestCase):
    def setUp(self):
        pass

    def test_format_number(self):
        # Loop through 0 -> 10 in increments of 0.1 and test if the formatted number equals what str(number) returns.
        for x in np.linspace(0.1, 10.0, 100):
            self.assertEqual(nrrd.format_number(x), format(x, '.17').rstrip('0').rstrip('.'))

        # A few example floating points and the resulting output numbers that should be seen
        values = {
            123412341234.123: '123412341234.123',
            0.000000123123: '1.2312300000000001e-07'
        }

        for key, value in values.items():
            self.assertEqual(nrrd.format_number(key), value)

    def test_format_vector(self):
        self.assertEqual(nrrd.format_vector([1, 2, 3]), '(1,2,3)')
        self.assertEqual(nrrd.format_vector([1., 2., 3.]), '(1,2,3)')
        self.assertEqual(nrrd.format_vector([1.2, 2., 3.2]), '(1.2,2,3.2000000000000002)')

        self.assertEqual(nrrd.format_vector(np.array([1, 2, 3])), '(1,2,3)')
        self.assertEqual(nrrd.format_vector(np.array([1., 2., 3.])), '(1,2,3)')
        self.assertEqual(nrrd.format_vector(np.array([1.2, 2., 3.2])), '(1.2,2,3.2000000000000002)')

    def test_format_optional_vector(self):
        self.assertEqual(nrrd.format_optional_vector([1, 2, 3]), '(1,2,3)')
        self.assertEqual(nrrd.format_optional_vector([1., 2., 3.]), '(1,2,3)')
        self.assertEqual(nrrd.format_optional_vector([1.2, 2., 3.2]), '(1.2,2,3.2000000000000002)')

        self.assertEqual(nrrd.format_optional_vector(np.array([1, 2, 3])), '(1,2,3)')
        self.assertEqual(nrrd.format_optional_vector(np.array([1., 2., 3.])), '(1,2,3)')
        self.assertEqual(nrrd.format_optional_vector(np.array([1.2, 2., 3.2])), '(1.2,2,3.2000000000000002)')

        self.assertEqual(nrrd.format_optional_vector(None), 'none')
        self.assertEqual(nrrd.format_optional_vector(np.array([np.nan, np.nan, np.nan])), 'none')
        self.assertEqual(nrrd.format_optional_vector([np.nan, np.nan, np.nan]), 'none')
        self.assertEqual(nrrd.format_optional_vector([None, None, None]), 'none')
        self.assertEqual(nrrd.format_optional_vector(np.array([None, None, None])), 'none')

    def test_format_matrix(self):
        self.assertEqual(nrrd.format_matrix(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])), '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_matrix(np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]])), '(1,2,3) (4,5,6) '
                                                                                                   '(7,8,9)')
        self.assertEqual(nrrd.format_matrix(np.array([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]])),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

        self.assertEqual(nrrd.format_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_matrix([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]), '(1,2,3) (4,5,6) '
                                                                                         '(7,8,9)')
        self.assertEqual(nrrd.format_matrix([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]]),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

    def test_format_optional_matrix(self):
        self.assertEqual(nrrd.format_optional_matrix(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix(np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]])),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix(np.array([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]])),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

        self.assertEqual(nrrd.format_optional_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]]),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

        self.assertEqual(nrrd.format_optional_matrix(np.array([
            [np.nan, np.nan, np.nan], [1, 2, 3], [4, 5, 6], [7, 8, 9]])),
            'none (1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix(np.array([
            [1, 2, 3], [np.nan, np.nan, np.nan], [4, 5, 6], [7, 8, 9]])),
            '(1,2,3) none (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix(np.array([
            [None, None, None], [1, 2, 3], [4, 5, 6], [7, 8, 9]])),
            'none (1,2,3) (4,5,6) (7,8,9)')

        self.assertEqual(nrrd.format_optional_matrix([
            [np.nan, np.nan, np.nan], [1, 2, 3], [4, 5, 6], [7, 8, 9]]),
            'none (1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix([
            [1, 2, 3], [np.nan, np.nan, np.nan], [4, 5, 6], [7, 8, 9]]),
            '(1,2,3) none (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_matrix([
            [None, None, None], [1, 2, 3], [4, 5, 6], [7, 8, 9]]),
            'none (1,2,3) (4,5,6) (7,8,9)')

    def test_format_number_list(self):
        self.assertEqual(nrrd.format_number_list([1, 2, 3]), '1 2 3')
        self.assertEqual(nrrd.format_number_list([1., 2., 3.]), '1 2 3')
        self.assertEqual(nrrd.format_number_list([1.2, 2., 3.2]), '1.2 2 3.2000000000000002')

        self.assertEqual(nrrd.format_number_list(np.array([1, 2, 3])), '1 2 3')
        self.assertEqual(nrrd.format_number_list(np.array([1., 2., 3.])), '1 2 3')
        self.assertEqual(nrrd.format_number_list(np.array([1.2, 2., 3.2])), '1.2 2 3.2000000000000002')

    def test_format_vector_list(self):
        self.assertEqual(nrrd.format_vector_list([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_vector_list([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_vector_list([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]]),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

        self.assertEqual(nrrd.format_vector_list(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_vector_list(np.array([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]])),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_vector_list(np.array([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]])),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

    def test_format_optional_vector_list(self):
        self.assertEqual(nrrd.format_optional_vector_list([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]]),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

        self.assertEqual(nrrd.format_optional_vector_list([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([[1., 2., 3.], [4., 5., 6.], [7., 8., 9.]]),
                         '(1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([[1, 2.2, 3.3], [4.4, 5.5, 6.6], [7.7, 8.8, 9.9]]),
                         '(1,2.2000000000000002,3.2999999999999998) (4.4000000000000004,5.5,6.5999999999999996) '
                         '(7.7000000000000002,8.8000000000000007,9.9000000000000004)')

        self.assertEqual(nrrd.format_optional_vector_list([[np.nan, np.nan, np.nan], [1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         'none (1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([[1, 2, 3], [np.nan, np.nan, np.nan], [4, 5, 6], [7, 8, 9]]),
                         '(1,2,3) none (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([[None, None, None], [1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         'none (1,2,3) (4,5,6) (7,8,9)')
        self.assertEqual(nrrd.format_optional_vector_list([None, [1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                         'none (1,2,3) (4,5,6) (7,8,9)')


if __name__ == '__main__':
    unittest.main()
