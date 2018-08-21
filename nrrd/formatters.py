import numpy as np


def format_number(x):
    """Format number to string

    Function converts a number to string. For numbers of class :class:`float`, up to 17 digits will be used to print
    the entire floating point number. Any padding zeros will be removed at the end of the number.

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
        value = '{:.17g}'.format(x)
    else:
        value = str(x)

    return value


def format_vector(x):
    """Format a 1D Numpy array into NRRD vector string

    Function converts a 1D Numpy array into a string using NRRD vector format.

    NRRD Vector:
    **Syntax:** (<Number 1>, <Number 2>, <Number 3>, ... <Number N>)
    **Example:** (1, 2, 3, 4)

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


def format_optional_vector(x):
    """Format a 1D Numpy array into NRRD optional vector string

    Function converts a 1D Numpy array or None object into a string using NRRD vector format. If the input :obj:`x` is
    None, then :obj:`vector` will be 'none'

    An optional NRRD vector is structured as one of the following:
        * (<Number 1>, <Number 2>, <Number 3>, ... <Number N>) OR
        * none

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


def format_matrix(x):
    """Format a 2D Numpy array into NRRD matrix string

    Function converts a 2D Numpy array into a string using the NRRD matrix format.
    A NRRD matrix is structured as follows:
        * (<Number 1>, <Number 2>, <Number 3>, ... <Number N>) (<Number 1>, <Number 2>, <Number 3>, ... <Number N>)

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


def format_optional_matrix(x):
    """Format a 2D Numpy array into a NRRD optional matrix string

    Function converts a 2D Numpy array into a string using the NRRD matrix format. For any rows of the matrix that
    contain all NaNs for each element, the row will be replaced with a 'none' indicating the row has no vector.
    A NRRD matrix is structured as follows:
        * (<Number 1>, <Number 2>, <Number 3>, ... <Number N>) (<Number 1>, <Number 2>, <Number 3>, ... <Number N>)

    For example, the following matrix NRRD input

      x:
      array([[ nan,  nan,  nan],
       [  1.,   2.,   3.],
       [  4.,   5.,   6.],
       [  7.,   8.,   9.]])

    will return

      none (1, 2, 3) (4, 5, 6) (7, 8, 9)

    Parameters
    ----------
    x : (M,N) :class:`numpy.ndarray`
        Matrix to convert to NRRD vector string

    Returns
    -------
    matrix : :class:`str`
        String containing NRRD matrix
    """

    return ' '.join([format_optional_vector(y) for y in x])


def format_number_list(x):
    """Format a 1D Numpy array into NRRD number list.

    Function converts a 1D Numpy array into a string using NRRD number list format.
    A NRRD number list is structured as follows:
        * <Number 1> <Number 2> <Number 3> ... <Number N>

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
