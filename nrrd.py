#!/usr/bin/env python
# encoding: utf-8
"""
nrrd.py
An all-python (and numpy) implementation for reading and writing nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Copyright (c) 2011-2017 Maarten Everts and others. See LICENSE and AUTHORS.

"""

import bz2
import os
import zlib
from datetime import datetime

from formatters import *
from parsers import *

__version__ = '0.2.5'

# Reading and writing gzipped data directly gives problems when the uncompressed
# data is larger than 4GB (2^32). Therefore we'll read and write the data in
# chunks. How this affects speed and/or memory usage is something to be analyzed
# further. The following two values define the size of the chunks.
_READ_CHUNKSIZE = 2 ** 20
_WRITE_CHUNKSIZE = 2 ** 20



























if __name__ == "__main__":
    import doctest

    doctest.testmod()
