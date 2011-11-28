#!/usr/bin/env python
# encoding: utf-8
"""
nrrd.py
An all-python (and numpy) implementation for reading and writing nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Copyright (c) 2011 Maarten Everts and David Hammond. See LICENSE.

"""

import numpy
import zlib,gzip
import bz2

class NrrdError(Exception):
    """Exceptions for Nrrd class."""
    pass

def _nrrd_read_header_lines(nrrdfile):
    """Read header lines from a .nrrd/.nhdr file."""
    line = nrrdfile.readline()
    if line[:-2] != 'NRRD000':
        raise NrrdError('Missing magic "NRRD" word, is this an NRRD file?')
    if line[-2] > '5':
        raise NrrdError('NRRD file version too new for this library.')
    headerlines = []
    while line != '\n' and line != '':
        headerlines.append(line)
        line = nrrdfile.readline()
    return headerlines

_NRRD_TYPE_MAPPING = {
                 'signed char': 'i1', 
                 'int8': 'i1', 
                 'int8_t': 'i1',
                 'uchar': 'u1',
                 'unsigned char': 'u1',
                 'uint8': 'u1',
                 'uint8_t': 'u1',
                 'short': 'i2',
                 'short int': 'i2',
                 'signed short': 'i2',
                 'signed short int': 'i2',
                 'int16': 'i2',
                 'int16_t': 'i2',
                 'ushort': 'u2',
                 'unsigned short': 'u2',
                 'unsigned short int': 'u2',
                 'uint16': 'u2',
                 'uint16_t': 'u2',
                 'int': 'i4',
                 'signed int': 'i4',
                 'int32': 'i4',
                 'int32_t': 'i4',
                 'uint': 'u4',
                 'unsigned int': 'u4',
                 'uint32': 'u4',
                 'uint32_t': 'u4',
                 'longlong': 'i8',
                 'long long': 'i8',
                 'long long int': 'i8',
                 'signed long long': 'i8',
                 'signed long long int': 'i8',
                 'int64': 'i8',
                 'int64_t': 'i8',
                 'ulonglong': 'u8',
                 'unsigned long long': 'u8',
                 'unsigned long long int': 'u8',
                 'uint64': 'u8',
                 'uint64_t': 'u8',
                 'float': 'f4',
                 'double': 'f8',
                 'block': 'V'}


def parse_nrrdvector(inp):
    """Parse a vector from a nrrd header, return a list."""
    assert inp[0] == '(', "Vector should be enclosed by parenthesis."
    assert inp[-1] == ')', "Vector should be enclosed by parenthesis."
    return [float(x) for x in inp[1:-1].split(',')]

def parse_optional_nrrdvector(inp):
    """Parse a vector from a nrrd header that can also be none."""
    if (inp == "none"):
        return inp
    else:
        return parse_nrrdvector(inp)

_NRRD_FIELD_PARSERS = {
    'dimension': int,
    'type': str,
    'sizes': lambda fieldValue: [int(x) for x in fieldValue.split(' ')],
    'endian': str,
    'encoding': str,
    'min': float,
    'max': float,
    'oldmin': float,
    'old min': float,
    'oldmax': float,
    'old max': float,
    'lineskip': int,
    'line skip': int,
    'byteskip': int,
    'byte skip': int,
    'content': str,
    'sample units': str,
    'datafile': str,
    'data file': str,
    'spacings': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'thicknesses': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axis mins': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axismins': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axis maxs': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'axismaxs': lambda fieldValue: [float(x) for x in fieldValue.split(' ')],
    'centerings': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'labels': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'units': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'kinds': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'space': str,
    'space dimension': int,
    'space units': lambda fieldValue: [str(x) for x in fieldValue.split(' ')],
    'space origin': parse_nrrdvector,
    'space directions': lambda fieldValue:
                        [parse_optional_nrrdvector(x) for x in fieldValue.split(' ')],
    'measurement frame': lambda fieldValue:
                        [parse_nrrdvector(x) for x in fieldValue.split(' ')],
}

_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']

_NRRD_FIELD_ORDER=[
    'type',
    'dimension',
    'space',
    'sizes',
    'space directions',
    'kinds',
    'endian',
    'encoding',
    'min',
    'max',
    'oldmin',
    'old min',
    'oldmax',
    'old max',
    'lineskip',
    'line skip',
    'byteskip',
    'byte skip',
    'content',
    'sample units',
    'datafile',
    'data file',
    'spacings',
    'thicknesses',
    'axis mins',
    'axismins',
    'axis maxs',
    'axismaxs',
    'centerings',
    'labels',
    'units',
    'space dimension',
    'space units',
    'space origin',
    'measurement frame']

class Nrrd:
    """An all-python (and numpy) implementation for nrrd files.
    See http://teem.sourceforge.net/nrrd/format.html for the specification."""
    def __init__(self, filename):
        self.fields = {}
        self.data = numpy.zeros(0)
        self._dtype = None
        filename = filename
        filehandle = open(filename,'rb')
        raw_headerlines = [line.strip() for line in
                          _nrrd_read_header_lines(filehandle)]
        headerlines = [line for line in raw_headerlines if line[0] != '#']
        self.version = headerlines[0]
        self.raw_fields = dict((splitline for splitline in 
                                [line.split(': ', 1) for line in headerlines]
                                if len(splitline)==2))
        self.keyvalue = dict((splitline for splitline in 
                                [line.split(':=', 1) for line in headerlines]
                                if len(splitline)==2))
        self._parse_fields()
        self._process_fields()
        self.read_data(filehandle)
        filehandle.close()
    def _parse_fields(self):
        """Parse the fields in the nrrd header"""
        self.fields = {}
        for field, value in self.raw_fields.iteritems():
            if field not in _NRRD_FIELD_PARSERS:
                raise NrrdError('Unexpected field in nrrd header: "%s".' % field)
            self.fields[field] = _NRRD_FIELD_PARSERS[field](value)
    def _process_fields(self):
        """Process the fields in the nrrd header"""
        # Check whether the required fields are there
        for field in _NRRD_REQUIRED_FIELDS:
            if field not in self.fields:
                raise NrrdError('Nrrd header misses required field: "%s".' % (field))
        # Process the data type
        numpy_typestring = _NRRD_TYPE_MAPPING[self.raw_fields['type']]
        if numpy.dtype(numpy_typestring).itemsize > 1:
            if 'endian' not in self.fields:
                raise NrrdError('Nrrd header misses required field: "endian".')
            if self.fields['endian'] == 'big':
                numpy_typestring = '>' + numpy_typestring
            elif self.fields['endian'] == 'little':
                numpy_typestring = '<' + numpy_typestring
            
        self._dtype = numpy.dtype(numpy_typestring)
    def get_lineskip(self):
        """Get the lineskip if present, otherwise return 0."""
        if "lineskip" in self.fields:
            return self.fields["lineskip"]
        elif "line skip" in self.fields:
            return self.fields["line skip"]
        else:
            return 0
    def get_byteskip(self):
        """Get the byteskip if present, otherwise return 0."""
        if "byteskip" in self.fields:
            return self.fields["byteskip"]
        elif "byte skip" in self.fields:
            return self.fields["byte skip"]
        else:
            return 0
    def get_datafile(self):
        """Return the datafile if present, otherwise return None."""
        if "datafile" in self.fields:
            return self.fields["datafile"]
        elif "data file" in self.fields:
            return self.fields["data file"]
        else:
            return None                    
    def read_data(self, filehandle):
        """Read the actual data into a numpy structure."""
        # determine byte and line skip
        lineskip = self.get_lineskip()
        byteskip = self.get_byteskip()
        datafile = self.get_datafile()
        datafilehandle = filehandle
        if datafile is not None:
            datafilehandle = open(datafile,'rb')
        totalbytes = self._dtype.itemsize *\
                        numpy.array(self.fields['sizes']).prod()
        if self.fields['encoding'] == 'raw':
            if byteskip == -1:
                datafilehandle.seek(-totalbytes, 2)
            else:
                for _ in range(lineskip):
                    datafilehandle.readline()
                datafilehandle.read(byteskip)
            self.data = numpy.fromfile(datafilehandle, self._dtype)        
        elif self.fields['encoding'] == 'gzip' or\
             self.fields['encoding'] == 'gz':
            gzipfile = gzip.GzipFile(fileobj=datafilehandle)
            # Again, unfortunately, numpy.fromfile does not support
            # reading from a gzip stream, so we'll do it like this.
            # I have no idea what the performance implications are.
            self.data = numpy.fromstring(gzipfile.read(), self._dtype)
        elif self.fields['encoding'] == 'bzip2' or\
             self.fields['encoding'] == 'bz2':
            bz2file = bz2.BZ2File(fileobj=datafilehandle)
            # Again, unfortunately, numpy.fromfile does not support
            # reading from a gzip stream, so we'll do it like this.
            # I have no idea what the performance implications are.
            self.data = numpy.fromstring(bz2file.read(), self._dtype)
        else:
            raise NrrdError('Unsupported encoding: "%s"' % self.fields['encoding'])
        # dkh : eliminated need to reverse order of dimensions. nrrd's
        # data layout is same as what numpy calls 'Fortran' order,
        shape_tmp = list(self.fields['sizes'])
        self.data = numpy.reshape(self.data, tuple(shape_tmp),order='F')
        
def format_space_separated_list(fieldValue) :
    return ' '.join([str(x) for x in fieldValue])
def format_nrrdvector(v) :
    return '('+','.join([str(x) for x in v])+')'
def format_optional_nrrdvector(v):
    if (v=='none') :
        return 'none'
    else :
        return format_nrrdvector(v)
def format_str_or_scalar(x):
    if isinstance(x,str) :
        return x
    else :
        return repr(x)

_NRRD_FIELD_FORMATTERS = {
    'dimension': format_str_or_scalar,
    'type': format_str_or_scalar,
    'sizes': format_space_separated_list,
    'endian': format_str_or_scalar,
    'encoding': format_str_or_scalar,
    'min': format_str_or_scalar,
    'max': format_str_or_scalar,
    'oldmin': format_str_or_scalar,
    'old min': format_str_or_scalar,
    'oldmax': format_str_or_scalar,
    'old max': format_str_or_scalar,
    'lineskip': format_str_or_scalar,
    'line skip': format_str_or_scalar,
    'byteskip': format_str_or_scalar,
    'byte skip': format_str_or_scalar,
    'content': format_str_or_scalar,
    'sample units': format_str_or_scalar,
    'datafile': format_str_or_scalar,
    'data file': format_str_or_scalar,
    'spacings': format_space_separated_list,
    'thicknesses': format_space_separated_list,
    'axis mins': format_space_separated_list,
    'axismins': format_space_separated_list,
    'axis maxs': format_space_separated_list,
    'axismaxs': format_space_separated_list,
    'centerings': format_space_separated_list,
    'labels': format_space_separated_list,
    'units': format_space_separated_list,
    'kinds': format_space_separated_list,
    'space': format_str_or_scalar,
    'space dimension': format_str_or_scalar,
    'space units': format_space_separated_list,
    'space origin': format_nrrdvector,
    'space directions': lambda fieldValue: ' '.join([format_optional_nrrdvector(x) for x in fieldValue]),
    'measurement frame': lambda fieldValue: ' '.join([format_optional_nrrdvector(x) for x in fieldValue]),
}


def write_nrrdfile(filename,fields,data) :
    """Write nrrd file into filename, with header determined from fields, and data given
    as numpy array. If fields does not contain type field, type will be determined from data ndarray"""
    # write header, assuming fields is dictionary as generated by _parse_fields

    # if type not specified, determine it from type of ndarray
    if 'type' not in fields :
        for nrrdtype,numpytype in _NRRD_TYPE_MAPPING.iteritems():
            if(numpy.dtype(numpytype)==data.dtype) :
                fields['type']=nrrdtype
                print "Inferred type",nrrdtype,"from input ndarray"
                break
    
    for field in _NRRD_REQUIRED_FIELDS:
        if field not in fields:
            raise NrrdError('Required field "%s" missing from input to write_nrrdfile.' % (field))
    # Format all fields (i.e., convert to strings)
    formatted_fields={}
    for field,value in fields.iteritems() :
        if field not in _NRRD_FIELD_UNPARSERS:
            raise NrrdError('Unexpected field passed to write_nrrdfile : "%s".' % field)
        if isinstance(value,str):
            # only call formatter if value is not already string ...
            # this makes format operation idempotent
            formatted_fields[field]=value
        else :
            formatted_fields[field]=_NRRD_FIELD_UNPARSERS[field](value)

    # I choose not to functionality implied by the following fields, so remove them
    # from formatted_fields
    undesired_fields=['datafile','data file','lineskip','line skip','byteskip','byte skip']
    for field in undesired_fields :
        if formatted_fields.has_key(field) :
            uparsed_fields.pop(field)
            print "note : removed unused field "+field
    
    outfilehandle=open(filename,'wb')
    outfilehandle.write('NRRD0004\n')
    outfilehandle.write('# This NRRD file generated by dkh modified pynrrd\n')
    outfilehandle.write('# Complete NRRD file format specification at:\n');
    outfilehandle.write('# http://teem.sourceforge.net/nrrd/format.html\n');

    # write the fields in order, this ignores fields not in _NRRD_FIELD_ORDER
    for field in _NRRD_FIELD_ORDER :
        if formatted_fields.has_key(field):
            outline = field+': '+formatted_fields[field]+'\n'
            outfilehandle.write(outline)
    outfilehandle.write('\n')

    # Check that data types of header and of data array match
    if numpy.dtype(_NRRD_TYPE_MAPPING[fields['type']])!=data.dtype :
        raise NrrdError('Data type mismatch between header field and numpy array')
    # Check that sizes from header and data array match
    if data.shape!=tuple(fields['sizes']) :
        raise NrrdError('Mismatch between header size and numpy array')
    
    # now write data directly
    rawdata=data.tostring(order='F');
    if formatted_fields['encoding']=='raw' :
        outfilehandle.write(rawdata)
    elif formatted_fields['encoding']=='gzip':
        gzfileobj=gzip.GzipFile(fileobj=outfilehandle)
        gzfileobj.write(rawdata)
        gzfileobj.close()
#    elif formatted_fields['encoding']=='bz2':
#        bz2fileobj=bz2.BZ2File(fileobj=outfilehandle)
#        bz2fileobj.write(rawdata)
#        bz2fileobj.close()
    else :
        raise NrrdError('Unsupported encoding: "%s"' % formatted_fields['encoding'])
    
    outfilehandle.close()    
    print "wrote %s"%(filename)
