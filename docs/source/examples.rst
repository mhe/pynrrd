Examples
========

.. currentmodule:: nrrd

Basic Example
-------------
.. code-block:: python

    import numpy as np
    import nrrd
    
    data = np.linspace(1, 50, 50)
    nrrd.write('output.nrrd', data)
    
    data2, header = nrrd.read('output.nrrd')
    print(np.all(data == data2))
    >>> True

    print(header)
    >>> OrderedDict([('type', 'double'), ('dimension', 1), ('sizes', array([50])), ('endian', 'little'), ('encoding', 'gzip')])

Example only reading header
---------------------------
.. code-block:: python

    import numpy as np
    import nrrd
    
    data = np.linspace(1, 50, 50)
    nrrd.write('output.nrrd', data)
    
    header = nrrd.read_header('output.nrrd')
    print(header)
    >>> OrderedDict([('type', 'double'), ('dimension', 1), ('sizes', array([50])), ('endian', 'little'), ('encoding', 'gzip')])

Example with fields and custom fields
-------------------------------------
.. code-block:: python

    import numpy as np
    import nrrd

    data = np.linspace(1, 60, 60).reshape((3, 10, 2))
    header = {'kinds': ['domain', 'domain', 'domain'], 'units': ['mm', 'mm', 'mm'], 'spacings': [1.0458, 1.0458, 2.5], 'space': 'right-anterior-superior', 'space directions': np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), 'encoding': 'ASCII', 'custom_field_here1': 24.34, 'custom_field_here2': np.array([1, 2, 3, 4])}
    custom_field_map = {'custom_field_here1': 'double', 'custom_field_here2': 'int list'}
    
    nrrd.write('output.nrrd', data, header, custom_field_map=custom_field_map)
    
    data2, header2 = nrrd.read('output.nrrd', custom_field_map)
    
    print(np.all(data == data2))
    >>> True
    
    print(header)
    >>> {'units': ['mm', 'mm', 'mm'], 'spacings': [1.0458, 1.0458, 2.5], 'custom_field_here1': 24.34, 'space': 'right-anterior-superior', 'space directions': array([[1, 0, 0],
       [0, 1, 0],
       [0, 0, 1]]), 'type': 'double', 'encoding': 'ASCII', 'kinds': ['domain', 'domain', 'domain'], 'dimension': 3, 'custom_field_here2': array([1, 2, 3, 4]), 'sizes': [3, 10, 2]}
    
    print(header2)
    >>> OrderedDict([('type', 'double'), ('dimension', 3), ('space', 'right-anterior-superior'), ('sizes', array([ 3, 10,  2])), ('space directions', array([[1., 0., 0.],
       [0., 1., 0.],
       [0., 0., 1.]])), ('kinds', ['domain', 'domain', 'domain']), ('encoding', 'ASCII'), ('spacings', array([1.0458, 1.0458, 2.5   ])), ('units', ['mm', 'mm', 'mm']), ('custom_field_here1', 24.34), ('custom_field_here2', array([1, 2, 3, 4]))])

Example reading NRRD file with duplicated header
-------------
.. code-block:: python

    import nrrd

    # set this field to True to enable the reading of files with duplicated header
    nrrd.reader.ALLOW_DUPLICATE_FIELD = True

    #name of the file you want to read with a duplicated header
    filename = "filename.nrrd"

    #read the file
    # filedata = numpy array
    # fileheader = header of the NRRD file
    filedata, fileheader = nrrd.read(filename)
    >>> UserWarning: Duplicate header field: 'space' warnings.warn(dup_message)
