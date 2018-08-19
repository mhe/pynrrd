[![Build Status](https://travis-ci.org/mhe/pynrrd.svg?branch=master)](https://travis-ci.org/mhe/pynrrd)
[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.62065.svg)](https://doi.org/10.5281/zenodo.62065)

pynrrd
======

pynrrd is a pure-Python module for reading and writing [NRRD][1] files into and 
from numpy arrays.

[1]: http://teem.sourceforge.net/nrrd/

Dependencies
------------

The module's only dependency is [numpy][2].

[2]: http://numpy.scipy.org/

Installation
------------

### Install via pip and PyPi repository (recommended)
    pip install pynrrd

### Install via pip and GitHub
    pip install git+https://github.com/mhe/pynrrd.git
    
### Install from source
    python setup.py install

Example usage
-------------

```python
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
```

Tests
-----

To run the tests:

    python -m unittest discover -v nrrd/tests

Bugs and shortcomings
---------------------

Most of the [NRRD format specification][3] is implemented. Exceptions
are: 

-  files where "data file" is "LIST"

Other shortcomings:

- More documentation is desirable, in particular for the options that
  can be passed to the write function.
- pynrrd is currently probably fairly forgiving in what it accepts for as
  NRRD files and could be made stricter.

[3]: http://teem.sourceforge.net/nrrd/format.html


License
-------

See [LICENSE](https://github.com/mhe/pynrrd/blob/master/LICENSE).
