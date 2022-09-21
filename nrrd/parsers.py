from typing import Any, Optional, Type, Union

import nptyping as npt
import numpy as np
from typing_extensions import Literal

from nrrd.errors import NRRDError


def parse_vector(x: str, dtype: Optional[Type[Union[int, float]]] = None) -> npt.NDArray[Literal['*'], Any]:
    """Parse NRRD vector from string into (N,) :class:`numpy.ndarray`.

    See :ref:`background/datatypes:int vector` and :ref:`background/datatypes:double vector` for more information on
    the format.

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD vector
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be :class:`float`, :class:`int` or :obj:`None`. If
        :obj:`dtype` is :obj:`None`, then it will be automatically determined by checking any of the vector elements
        for fractional numbers. If found, then the vector will be converted to :class:`float`, otherwise :class:`int`.
        Default is to automatically determine datatype.

    Returns
    -------
    vector : (N,) :class:`numpy.ndarray`
        Vector that is parsed from the :obj:`x` string
    """

    if x[0] != '(' or x[-1] != ')':
        raise NRRDError('Vector should be enclosed by parentheses.')

    # Always convert to float and then truncate to integer if desired
    # The reason why is parsing a floating point string to int will fail (i.e. int('25.1') will fail)
    vector = np.array([float(x) for x in x[1:-1].split(',')])

    # If using automatic datatype detection, then start by converting to float and determining if the number is whole
    # Truncate to integer if dtype is int also
    if dtype is None:
        vector_trunc = vector.astype(int)

        if np.all((vector - vector_trunc) == 0):
            vector = vector_trunc
    elif dtype == int:
        vector = vector.astype(int)
    elif dtype != float:
        raise NRRDError('dtype should be None for automatic type detection, float or int')

    return vector


def parse_optional_vector(x: str, dtype: Optional[Type[Union[int, float]]] = None) -> \
        Optional[npt.NDArray[Literal['*'], Any]]:
    """Parse optional NRRD vector from string into (N,) :class:`numpy.ndarray` or :obj:`None`.

    Function parses optional NRRD vector from string into an (N,) :class:`numpy.ndarray`. This function works the same
    as :meth:`parse_vector` except if :obj:`x` is 'none', :obj:`vector` will be :obj:`None`

    See :ref:`background/datatypes:int vector` and :ref:`background/datatypes:double vector` for more information on
    the format.

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD vector or 'none'
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be :class:`float`, :class:`int` or :obj:`None`. If
        :obj:`dtype` is :obj:`None`, then it will be automatically determined by checking any of the vector elements
        for fractional numbers. If found, then the vector will be converted to :class:`float`, otherwise :class:`int`.
        Default is to automatically determine datatype.

    Returns
    -------
    vector : (N,) :class:`numpy.ndarray` or :obj:`None`
        Vector that is parsed from the :obj:`x` string or :obj:`None` if :obj:`x` is 'none'
    """

    if x == 'none':
        return None
    else:
        return parse_vector(x, dtype)


def parse_matrix(x: str, dtype: Optional[Type[Union[int, float]]] = None) -> npt.NDArray[Literal['*, *'], Any]:
    """Parse NRRD matrix from string into (M,N) :class:`numpy.ndarray`.

    See :ref:`background/datatypes:int matrix` and :ref:`background/datatypes:double matrix` for more information on
    the format.

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD matrix
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be :class:`float`, :class:`int` or :obj:`None`. If
        :obj:`dtype` is :obj:`None`, then it will be automatically determined by checking any of the elements
        for fractional numbers. If found, then the matrix will be converted to :class:`float`, otherwise :class:`int`.
        Default is to automatically determine datatype.

    Returns
    -------
    matrix : (M,N) :class:`numpy.ndarray`
        Matrix that is parsed from the :obj:`x` string
    """

    # Split input by spaces, convert each row into a vector and stack them vertically to get a matrix
    matrix = [parse_vector(x, dtype=float) for x in x.split()]

    # Get the size of each row vector and then remove duplicate sizes
    # There should be exactly one value in the matrix because all row sizes need to be the same
    if len(np.unique([len(x) for x in matrix])) != 1:
        raise NRRDError('Matrix should have same number of elements in each row')

    matrix = np.vstack(matrix)

    # If using automatic datatype detection, then start by converting to float and determining if the number is whole
    # Truncate to integer if dtype is int also
    if dtype is None:
        matrix_trunc = matrix.astype(int)

        if np.all((matrix - matrix_trunc) == 0):
            matrix = matrix_trunc
    elif dtype == int:
        matrix = matrix.astype(int)
    elif dtype != float:
        raise NRRDError('dtype should be None for automatic type detection, float or int')

    return matrix


def parse_optional_matrix(x: str) -> Optional[npt.NDArray[Literal['*, *'], Any]]:
    """Parse optional NRRD matrix from string into (M,N) :class:`numpy.ndarray` of :class:`float`.

    Function parses optional NRRD matrix from string into an (M,N) :class:`numpy.ndarray` of :class:`float`. This
    function works the same as :meth:`parse_matrix` except if a row vector in the matrix is none, the resulting row in
    the returned matrix will be all NaNs.

    See :ref:`background/datatypes:double matrix` for more information on the format.

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD matrix

    Returns
    -------
    matrix : (M,N) :class:`numpy.ndarray` of :class:`float`
        Matrix that is parsed from the :obj:`x` string
    """

    # Split input by spaces to get each row and convert into a vector. The row can be 'none', in which case it will
    # return None
    matrix = [parse_optional_vector(x, dtype=float) for x in x.split()]

    # Get the size of each row vector, 0 if None
    sizes = np.array([0 if x is None else len(x) for x in matrix])

    # Get sizes of each row vector removing duplicate sizes
    # Since each row vector should be same size, the unique sizes should return one value for the row size or it may
    # return a second one (0) if there are None vectors
    unique_sizes = np.unique(sizes)

    if len(unique_sizes) != 1 and (len(unique_sizes) != 2 or unique_sizes.min() != 0):
        raise NRRDError('Matrix should have same number of elements in each row')

    # Create a vector row of NaN's that matches same size of remaining vector rows
    # Stack the vector rows together to create matrix
    nan_row = np.full((unique_sizes.max()), np.nan)
    matrix = np.vstack([nan_row if x is None else x for x in matrix])

    return matrix


def parse_number_list(x: str, dtype: Optional[Type[Union[int, float]]] = None) -> npt.NDArray[Literal['*'], Any]:
    """Parse NRRD number list from string into (N,) :class:`numpy.ndarray`.

    See :ref:`background/datatypes:int list` and :ref:`background/datatypes:double list` for more information on the
    format.

    Parameters
    ----------
    x : :class:`str`
        String containing NRRD number list
    dtype : data-type, optional
        Datatype to use for the resulting Numpy array. Datatype can be :class:`float`, :class:`int` or :obj:`None`. If
        :obj:`dtype` is :obj:`None`, then it will be automatically determined by checking for fractional numbers. If
        found, then the string will be converted to :class:`float`, otherwise :class:`int`. Default is to automatically
        determine datatype.

    Returns
    -------
    vector : (N,) :class:`numpy.ndarray`
        Vector that is parsed from the :obj:`x` string
    """

    # Always convert to float and then perform truncation to integer if necessary
    number_list = np.array([float(x) for x in x.split()])

    if dtype is None:
        number_list_trunc = number_list.astype(int)

        # If there is no difference between the truncated number list and the number list, then that means that the
        # number list was all integers and we can just return that
        if np.all((number_list - number_list_trunc) == 0):
            number_list = number_list_trunc
    elif dtype == int:
        number_list = number_list.astype(int)
    elif dtype != float:
        raise NRRDError('dtype should be None for automatic type detection, float or int')

    return number_list


def parse_number_auto_dtype(x: str) -> Union[int, float]:
    """Parse number from string with automatic type detection.

    Parses input string and converts to a number using automatic type detection. If the number contains any
    fractional parts, then the number will be converted to float, otherwise the number will be converted to an int.

    See :ref:`background/datatypes:int` and :ref:`background/datatypes:double` for more information on the format.

    Parameters
    ----------
    x : :class:`str`
        String representation of number

    Returns
    -------
    result : :class:`int` or :class:`float`
        Number parsed from :obj:`x` string
    """

    value: Union[int, float] = float(x)

    if value.is_integer():
        value = int(value)

    return value
