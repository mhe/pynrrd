import os
import warnings

# Enable all warnings
warnings.simplefilter('always')

DATA_DIR_PATH = os.path.join(os.path.dirname(__file__), 'data')
RAW_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nrrd')
RAW_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.nhdr')
RAW_BYTESKIP_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_byteskip_minus_one.nhdr')
GZ_BYTESKIP_NIFTI_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_byteskip_minus_one_nifti.nhdr')
GZ_NIFTI_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_nifti.nhdr')
RAW_INVALID_BYTESKIP_NHDR_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_byteskip_minus_five.nhdr')
RAW_DATA_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30.raw')
GZ_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz.nrrd')
BZ2_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_bz2.nrrd')
GZ_LINESKIP_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz_lineskip.nrrd')
GZ_BYTESKIP_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'BallBinary30x30x30_gz_byteskip_minus_one.nrrd')
RAW_4D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test_simple4d_raw.nrrd')

ASCII_1D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test1d_ascii.nrrd')
ASCII_2D_NRRD_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test2d_ascii.nrrd')
ASCII_1D_CUSTOM_FIELDS_FILE_PATH = os.path.join(DATA_DIR_PATH, 'test_customFields.nrrd')
