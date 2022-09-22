.. image:: https://travis-ci.org/mhe/pynrrd.svg?branch=master
    :target: https://travis-ci.org/mhe/pynrrd
    :alt: Build Status

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.592532.svg
   :target: https://doi.org/10.5281/zenodo.592532
   :alt: DOI

.. image:: https://img.shields.io/pypi/pyversions/pynrrd.svg
    :target: https://img.shields.io/pypi/pyversions/pynrrd.svg
    :alt: Python version

.. image:: https://badge.fury.io/py/pynrrd.svg
    :target: https://badge.fury.io/py/pynrrd
    :alt: PyPi version

.. image:: https://readthedocs.org/projects/pynrrd/badge/?version=stable
    :target: https://pynrrd.readthedocs.io/en/stable/?badge=stable
    :alt: Documentation Status

.. image:: https://codecov.io/gh/mhe/pynrrd/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/mhe/pynrrd

|

pynrrd
======
pynrrd is a pure-Python module for reading and writing `NRRD <http://teem.sourceforge.net/nrrd/>`_ files into and
from numpy arrays.

Requirements
------------

* `numpy <https://numpy.org/>`_
* nptyping
* typing_extensions

v1.0+ requires Python 3.7 or above. If you have an older Python version, please install a v0.x release instead.

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

Install from source (recommended for contributing to pynrrd)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For developers that want to contribute to pynrrd, you can clone the pynrrd repository and install it using the following commands:

.. code-block:: bash

    git clone https://github.com/mhe/pynrrd.git
    cd pynrrd
    pip install .

or, for the last line, instead use:

.. code-block:: bash

    pip install -e .

to install in 'develop' or 'editable' mode, where changes can be made to the local working code and Python will use
the updated pynrrd code.

**Tests**

The tests can be run via the following command from the base directory:

.. code-block:: bash

    python -m unittest discover -v nrrd/tests

**Format and Lint code**

 This repository uses pre-commit hooks to run format and lint the code and they are enforced in CI. See [pre-commit](https://pre-commit.com)

Example usage
-------------
.. code-block:: python

    import numpy as np
    import nrrd

    # Some sample numpy data
    data = np.zeros((5,4,3,2))
    filename = 'testdata.nrrd'

    # Write to a NRRD file
    nrrd.write(filename, data)

    # Read the data back from file
    readdata, header = nrrd.read(filename)
    print(readdata.shape)
    print(header)


Next Steps
----------
For more information, see the `documentation <http://pynrrd.readthedocs.io/>`_.

License
-------
See the `LICENSE <https://github.com/mhe/pynrrd/blob/master/LICENSE>`_ for more information.
