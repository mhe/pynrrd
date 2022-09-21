from typing import Any, Optional, Union

import nptyping as npt
import numpy as np
from typing_extensions import Literal


def format_number(x: Union[int, float]) -> str:
    """Format number to string

    Function converts a number to string. For numbers of class :class:`float`, up to 17 digits will be used to print
    the entire floating point number. Any padding zeros will be removed at the end of the number.

    See :ref:`background/datatypes:int` and :ref:`background/datatypes:double` for more information on the format.

    .. note::
            IEEE754-1985 standard says that 17 significant decimal digits are required to adequately represent a
            64-bit floating point number. Not all fractional numbers can be exactly represented in floating point. An
            example is 0.1 which will be approximated as 0.10000000000000001.

    Parameters
    ----------
    x : :class:`int` or :class:`float`
        Number to convert to string

    Returns
    -------
    vector : :class:`str`
        String of number :obj:`x`
    """

    if isinstance(x, float):
        # Helps prevent loss of precision as using str() in Python 2 only prints 12 digits of precision.
        # However, IEEE754-1985 standard says that 17 significant decimal digits is required to adequately represent a
        # floating point number.
        # The g option is used rather than f because g precision uses significant digits while f is just the number of
        # digits after the decimal. (NRRD C implementation uses g).
        value = f'{x:.17g}'
    else:
        value = str(x)

    return value


def format_vector(x: npt.NDArray[Literal['*'], Any]) -> str:
    """Format a (N,) :class:`numpy.ndarray` into a NRRD vector string

    See :ref:`background/datatypes:int vector` and :ref:`background/datatypes:double vector` for more information on
    the format.

    Parameters
    ----------
    x : (N,) :class:`numpy.ndarray`
        Vector to convert to NRRD vector string

    Returns
    -------
    vector : :class:`str`
        String containing NRRD vector
    """

    return '(' + ','.join([format_number(y) for y in x]) + ')'


def format_optional_vector(x: Optional[npt.NDArray[Literal['*'], Any]]) -> str:
    """Format a (N,) :class:`numpy.ndarray` into a NRRD optional vector string

    Function converts a (N,) :class:`numpy.ndarray` or :obj:`None` into a string using NRRD vector format. If the input
    :obj:`x` is :obj:`None`, then :obj:`vector` will be 'none'

    See :ref:`background/datatypes:int vector` and :ref:`background/datatypes:double vector` for more information on
    the format.

    Parameters
    ----------
    x : (N,) :class:`numpy.ndarray` or :obj:`None`
        Vector to convert to NRRD vector string

    Returns
    -------
    vector : :class:`str`
        String containing NRRD vector
    """

    # If vector is None or all elements are NaN, then return none
    # Otherwise format the vector as normal
    if x is None or np.all(np.isnan(x)):
        return 'none'
    else:
        return format_vector(x)


def format_matrix(x: npt.NDArray[Literal['*, *'], Any]) -> str:
    """Format a (M,N) :class:`numpy.ndarray` into a NRRD matrix string

    See :ref:`background/datatypes:int matrix` and :ref:`background/datatypes:double matrix` for more information on
    the format.

    Parameters
    ----------
    x : (M,N) :class:`numpy.ndarray`
        Matrix to convert to NRRD vector string

    Returns
    -------
    matrix : :class:`str`
        String containing NRRD matrix
    """

    return ' '.join([format_vector(y) for y in x])


def format_optional_matrix(x: Optional[npt.NDArray[Literal['*, *'], Any]]) -> str:
    """Format a (M,N) :class:`numpy.ndarray` of :class:`float` into a NRRD optional matrix string

    Function converts a (M,N) :class:`numpy.ndarray` of :class:`float` into a string using the NRRD matrix format. For
    any rows of the matrix that contain all NaNs for each element, the row will be replaced with a 'none' indicating
    the row has no vector.

    See :ref:`background/datatypes:double matrix` for more information on the format.

    .. note::
            :obj:`x` must have a datatype of float because NaN's are only defined for floating point numbers.

    Parameters
    ----------
    x : (M,N) :class:`numpy.ndarray` of :class:`float`
        Matrix to convert to NRRD vector string

    Returns
    -------
    matrix : :class:`str`
        String containing NRRD matrix
    """

    return ' '.join([format_optional_vector(y) for y in x])


def format_number_list(x: npt.NDArray[Literal['*'], Any]) -> str:
    """Format a (N,) :class:`numpy.ndarray` into a NRRD number list.

    See :ref:`background/datatypes:int list` and :ref:`background/datatypes:double list` for more information on the
    format.

    Parameters
    ----------
    x : (N,) :class:`numpy.ndarray`
        Vector to convert to NRRD number list string

    Returns
    -------
    list : :class:`str`
        String containing NRRD list
    """

    return ' '.join([format_number(y) for y in x])
