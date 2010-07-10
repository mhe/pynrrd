nrrd-python
===========

python-nrrd is a pure-Python module for reading data in [nrrd][1] files into numpy arrays. 

[1]: http://teem.sourceforge.net/nrrd/

Dependencies
------------

The module's only dependencfy is [numpy][2].

[2]: http://numpy.scipy.org/

Usage
-----

from nrrd import Nrrd
nrrdfile = Nrrd('mynrrdfile.nrrd')
print nrrd.data.shape

Bugs and shortcomings
---------------------

At the moment, the module only supports reading nrrd files. Writing support is planned.
Most of the [nrrd format specification][3] is implemented. Exceptions are:
- files where encoding is 'txt', 'text', or 'ascii'
- files where "data file" is "LIST"

[3]: http://teem.sourceforge.net/nrrd/format.html

License
-------

See LICENSE.
