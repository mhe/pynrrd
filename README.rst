.. image:: https://travis-ci.org/mhe/pynrrd.svg?branch=master
    :target: https://travis-ci.org/mhe/pynrrd
    :alt: Build Status

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.62065.svg
    :target: https://doi.org/10.5281/zenodo.62065
    :alt: DOI

pynrrd
======
pynrrd is a pure-Python module for reading and writing `NRRD <http://teem.sourceforge.net/nrrd/>`_ files into and 
from numpy arrays.

Dependencies
------------
The module's only dependency is `numpy <http://numpy.scipy.org/>`_.

Installation
------------
Install via pip and PyPi repository (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install pynrrd

Install via pip and GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install git+https://github.com/mhe/pynrrd.git
    
Install from source
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python setup.py install

Example usage
-------------

.. code-block:: python

    import numpy as np
    import nrrd
    
    # some sample numpy data
    data = np.zeros((5,4,3,2))
    filename = 'testdata.nrrd'
    
    # write to a NRRD file
    nrrd.write(filename, data)
    
    # read the data back from file
    readdata, options = nrrd.read(filename)
    print readdata.shape
    print options


Tests
-----

To run the tests:

.. code-block:: bash

    python -m unittest discover -v nrrd/tests

Bugs and shortcomings
---------------------

Most of the `NRRD format specification <http://teem.sourceforge.net/nrrd/format.html>`_ is implemented. Exceptions
are: 

-  files where "data file" is "LIST"

Other shortcomings:

- More documentation is desirable, in particular for the options that
  can be passed to the write function.
- pynrrd is currently probably fairly forgiving in what it accepts for as
  NRRD files and could be made stricter.


License
-------

See `LICENSE <https://github.com/mhe/pynrrd/blob/master/LICENSE>`_.
