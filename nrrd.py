#!/usr/bin/env python
# encoding: utf-8
"""
nrrd.py
An all-python (and numpy) implementation for nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Created by Maarten Everts on 2009-06-26.
Copyright (c) 2009 University of Groningen. All rights reserved.
"""

import numpy
import gzip
import bz2

class NrrdError(Exception):
    """Exceptions for Nrrd class."""
    pass

def _nrrd_read_header_lines(nrrdfile):
    """Read header lines from a .nrrd/.nhdr file."""
    line = nrrdfile.readline()
    if line[:-2] != 'NRRD000':
        raise NrrdError('Missing magic "NRRD" word, is this an NRRD file?')
    # assert(line[:-2] == 'NRRD000')
    if line[-2] > '5':
        raise NrrdError('NRRD file version too new for this library.')
    # assert(line[-2] <= '5')
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


def nrrdvector(inp):
    """Parse a vector from a nrrd header, return a list."""
    assert inp[0] == '(', "Vector should be enclosed by parenthesis."
    assert inp[-1] == ')', "Vector should be enclosed by parenthesis."
    return [float(x) for x in inp[1:-1].split(',')]

def optional_nrrdvector(inp):
    """Parse a vector from a nrrd header that can also be none."""
    if (inp == "none"):
        return inp
    else:
        return nrrdvector(inp)

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
    'space origin': nrrdvector,
    'space directions': lambda fieldValue:
                        [optional_nrrdvector(x) for x in fieldValue.split(' ')],
    'measurement frame': lambda fieldValue:
                        [nrrdvector(x) for x in fieldValue.split(' ')],
}

#TODO: block size
# pre-calculate the list of required fields
_NRRD_REQUIRED_FIELDS = ['dimension', 'type', 'encoding', 'sizes']



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
                for i in range(lineskip):
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
        # Reshape the data (we need to reverse the order).
        shape_tmp = list(self.fields['sizes'])
        shape_tmp.reverse()
        self.data = numpy.reshape(self.data, tuple(shape_tmp))

def main():
    """Main function to test the nrrd module."""
    print "Reading nrrd file header"
    testnrrd = Nrrd("helix-ten-broken.nhdr")
    print testnrrd.data.shape
    print "Done."

if __name__ == '__main__':
    main()
