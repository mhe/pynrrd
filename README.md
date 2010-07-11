pynrrd
===========

pynrrd is a pure-Python module for reading data in [nrrd][1] files into
numpy arrays.

[1]: http://teem.sourceforge.net/nrrd/

Dependencies
------------

The module's only dependency is [numpy][2].

[2]: http://numpy.scipy.org/

Installation
------------

    python setup.py install

Usage
-----

    from nrrd import Nrrd
    nrrdfile = Nrrd('mynrrdfile.nrrd')
    # nrrdfile.data has the data as a numpy array
    print nrrdfile.data.shape

Bugs and shortcomings
---------------------

At the moment, the module only supports reading nrrd files. Writing support is
planned. Most of the [nrrd format specification][3] is implemented. Exceptions
are: 

-  files where encoding is 'txt', 'text', or 'ascii'
-  files where "data file" is "LIST"

[3]: http://teem.sourceforge.net/nrrd/format.html

License
-------

See LICENSE.
