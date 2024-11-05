Supported Fields
================

.. currentmodule:: nrrd

A list of supported fields, according to the NRRD specification, and its corresponding datatype can be seen below. Each field has a link to the NRRD specification providing a detailed description of the field.

========================  ==============================================
Field                     NRRD Datatype
========================  ==============================================
dimension_                :ref:`background/datatypes:int`
type_                     :ref:`background/datatypes:string`
sizes_                    :ref:`background/datatypes:int list`
endian_                   :ref:`background/datatypes:string`
encoding_                 :ref:`background/datatypes:string`
`datafile or data file`_  :ref:`background/datatypes:string`
`lineskip or line skip`_  :ref:`background/datatypes:int`
`byteskip or byte skip`_  :ref:`background/datatypes:int`
content_                  :ref:`background/datatypes:string`
kinds_                    :ref:`background/datatypes:string list`
labels_                   :ref:`background/datatypes:quoted string list`
units_                    :ref:`background/datatypes:quoted string list`
min_                      :ref:`background/datatypes:double`
max_                      :ref:`background/datatypes:double`
spacings_                 :ref:`background/datatypes:double list`
thicknesses_              :ref:`background/datatypes:double list`
centerings_               :ref:`background/datatypes:string list`
`oldmin or old min`_      :ref:`background/datatypes:double`
`oldmax or old max`_      :ref:`background/datatypes:double`
`axismins or axis mins`_  :ref:`background/datatypes:double list`
`axismaxs or axis maxs`_  :ref:`background/datatypes:double list`
`sample units`_           :ref:`background/datatypes:string`
space_                    :ref:`background/datatypes:string`
`space dimension`_        :ref:`background/datatypes:int`
`space units`_            :ref:`background/datatypes:quoted string list`
`space directions`_       :ref:`background/datatypes:double matrix` or :ref:`background/datatypes:double vector list` depending on :data:`nrrd.SPACE_DIRECTIONS_TYPE`
`space origin`_           :ref:`background/datatypes:double vector`
`measurement frame`_      :ref:`background/datatypes:int matrix`
========================  ==============================================

.. _dimension: http://teem.sourceforge.net/nrrd/format.html#dimension
.. _type: http://teem.sourceforge.net/nrrd/format.html#type
.. _sizes: http://teem.sourceforge.net/nrrd/format.html#sizes
.. _endian: http://teem.sourceforge.net/nrrd/format.html#endian
.. _encoding: http://teem.sourceforge.net/nrrd/format.html#encoding
.. _datafile or data file: http://teem.sourceforge.net/nrrd/format.html#datafile
.. _lineskip or line skip: http://teem.sourceforge.net/nrrd/format.html#lineskip
.. _byteskip or byte skip: http://teem.sourceforge.net/nrrd/format.html#byteskip
.. _content: http://teem.sourceforge.net/nrrd/format.html#content
.. _kinds: http://teem.sourceforge.net/nrrd/format.html#kinds
.. _labels: http://teem.sourceforge.net/nrrd/format.html#labels
.. _units: http://teem.sourceforge.net/nrrd/format.html#units
.. _min: http://teem.sourceforge.net/nrrd/format.html#min
.. _max: http://teem.sourceforge.net/nrrd/format.html#max
.. _spacings: http://teem.sourceforge.net/nrrd/format.html#spacings
.. _thicknesses: http://teem.sourceforge.net/nrrd/format.html#thicknesses
.. _centerings: http://teem.sourceforge.net/nrrd/format.html#centers
.. _oldmin or old min: http://teem.sourceforge.net/nrrd/format.html#oldmin
.. _oldmax or old max: http://teem.sourceforge.net/nrrd/format.html#oldmax
.. _axismins or axis mins: http://teem.sourceforge.net/nrrd/format.html#axismins
.. _axismaxs or axis maxs: http://teem.sourceforge.net/nrrd/format.html#axismaxs
.. _sample units: http://teem.sourceforge.net/nrrd/format.html#sampleunits
.. _space: http://teem.sourceforge.net/nrrd/format.html#space
.. _space dimension: http://teem.sourceforge.net/nrrd/format.html#spacedimension
.. _space units: http://teem.sourceforge.net/nrrd/format.html#spaceunits
.. _space directions: http://teem.sourceforge.net/nrrd/format.html#spacedirections
.. _space origin: http://teem.sourceforge.net/nrrd/format.html#spaceorigin
.. _measurement frame: http://teem.sourceforge.net/nrrd/format.html#measurementframe
