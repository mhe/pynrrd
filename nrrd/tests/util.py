import os
import sys
import unittest

# TODO Why is this necessary?
# Look on level up for nrrd.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

DATA_DIR_PATH = os.path.join(os.path.dirname(__file__), 'data')
RAW_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nrrd')
RAW_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nhdr')
RAW_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.raw')
GZ_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz.nrrd')
BZ2_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_bz2.nrrd')
GZ_LINESKIP_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz_lineskip.nrrd')
RAW_4D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test_simple4d_raw.nrrd')

ASCII_1D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test1d_ascii.nrrd')
ASCII_2D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test2d_ascii.nrrd')

# Fix issue with assertRaisesRegex only available in Python 3 while
# assertRaisesRegexp is available in Python 2 (and deprecated in Python 3)
if not hasattr(unittest.TestCase, 'assertRaisesRegex'):
    unittest.TestCase.assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegexp')
