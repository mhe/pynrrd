Reference Guide
===============

Table of Contents
-----------------

Reading NRRD files
~~~~~~~~~~~~~~~~~~
.. autosummary::

    nrrd.read
    nrrd.read_header
    nrrd.read_data
    nrrd.reader.ALLOW_DUPLICATE_FIELD

Writing NRRD files
~~~~~~~~~~~~~~~~~~
.. autosummary::

    nrrd.write

Parsing NRRD fields
~~~~~~~~~~~~~~~~~~~
.. autosummary::

    nrrd.parse_number_auto_dtype
    nrrd.parse_number_list
    nrrd.parse_vector
    nrrd.parse_optional_vector
    nrrd.parse_matrix
    nrrd.parse_optional_matrix

Formatting NRRD fields
~~~~~~~~~~~~~~~~~~~~~~
.. autosummary::

    nrrd.format_number
    nrrd.format_number_list
    nrrd.format_vector
    nrrd.format_optional_vector
    nrrd.format_matrix
    nrrd.format_optional_matrix

NRRD Module
-----------

.. automodule:: nrrd
    :members:
    :undoc-members:
    :show-inheritance:

.. autodata:: nrrd.reader.ALLOW_DUPLICATE_FIELD
