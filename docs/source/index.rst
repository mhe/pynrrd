pynrrd
======

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

.. image:: https://codecov.io/gh/mhe/pynrrd/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/mhe/pynrrd

pynrrd is a pure-Python module for reading and writing `NRRD <http://teem.sourceforge.net/nrrd/>`_ files into and
from numpy arrays.

Dependencies
------------

TODO Put requirements here instead?

In v1.0+, Python 3.7 or above is required for this module. If you need this library for an older version of Python, please install a the v0.x release instead.

* `Numpy <https://numpy.org/>`_
* nptyping
* typing_extensions

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

Quick Start
-----------
.. code-block:: python

    import numpy as np
    import nrrd

    # Some sample numpy data
    data = np.zeros((5, 4, 3, 2))
    filename = 'testdata.nrrd'

    # Write to a NRRD file
    nrrd.write(filename, data)

    # Read the data back from file
    readdata, header = nrrd.read(filename)
    print(readdata.shape)
    print(header)

Contents
--------

TODO Put titles here!

.. toctree::
   :hidden:
   :maxdepth: 1

   Home <self>

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples

.. toctree::
   :maxdepth: 1
   :caption: Background

   user-guide

.. toctree::
   :maxdepth: 1
   :caption: Reference

   pynrrd

.. toctree::
    :caption: Links
    :hidden:

    Source code <https://github.com/mhe/pynrrd>
    Issue tracker <https://github.com/mhe/pynrrd/issues>
    Releases <https://github.com/mhe/pynrrd/releases>
    PyPi <https://pypi.org/project/pynrrd/>
    License <https://github.com/mhe/pynrrd/blob/master/LICENSE>