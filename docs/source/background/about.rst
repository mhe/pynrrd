About the NRRD file format
==========================

.. currentmodule:: nrrd

NRRD stands for **N**\ early **R**\ aw **R**\ aster **D**\ ata and is a file format designed for scientific visualization and image processing involving N-dimensional data. It is a simple and flexible file format with a header containing information about the data that can be read by simply opening the NRRD file in a text editor. Many other file formats such as PNG, JPG, DICOM cannot be read with a simple text editor! In addition, the raw data can be stored in a NRRD file in a number of commonly known formats such as ASCII, gzip, bzip or even raw. The header information and data itself can be stored in the same file or separately. Another feature of the NRRD file format is the support of custom key/value pairs in the header to allow storing of user information not defined in the NRRD specification.

The general structure of the NRRD file format is as follows::

    NRRD<NRRD file version>
    # Complete NRRD file format specification at:
    # http://teem.sourceforge.net/nrrd/format.html
    <field>: <value>
    <field>: <value>
    ...
    <field>: <value>
    <custom field>:=<value>
    <custom field>:=<value>
    ...
    <custom field>:=<value>
    # Comments are identified with a # symbol

    <data here if stored in same file, otherwise stored in detached file>

As with most file formats, the file begins with a magic line that uniquely identifies the file as a NRRD file. Along with the magic line is a version that identifies what revision of the NRRD specification is used. As of today, the latest NRRD version is 5. Line comments can be specified by starting the line with a # symbol. Following the magic line is the header which is written in ASCII with the structure :code:`<field>: <value>` or :code:`<field>:=<value>` in the case of a custom field. The header is finished reading once a blank line has been read. If the data is stored in the same file (based on whether the header contains a datafile field), then the data will follow the header.

More information on the NRRD file format can be found `here <http://teem.sourceforge.net/nrrd/index.html>`_.