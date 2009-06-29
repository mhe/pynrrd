#!/usr/bin/env python
# encoding: utf-8
"""
nrrd.py
An all-python (and numpy) implementation for nrrd files.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

Created by Maarten Everts on 2009-06-26.
Copyright (c) 2009 University of Groningen. All rights reserved.
"""

import sys
import os
import unittest
import numpy
import gzip
import bz2

def nrrdReadHeaderLines(nrrdFile):
	line = nrrdFile.readline()
	assert(line[:-2] == 'NRRD000')
	assert(line[-2] <= '5')
	headerLines = []
	while line != '\n' and line != '':
		headerLines.append(line)
		line = nrrdFile.readline()
	return headerLines
	
def typestring2dtype(typestring):
	"""Converts a string describing a string to a numpy dtype"""
	pass

nrrd2numpyTypeString = {
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


def nrrdVector(inp):
	assert inp[0] == '(', "Vector should be enclosed by parenthesis."
	assert inp[-1] == ')', "Vector should be enclosed by parenthesis."
	return [float(x) for x in inp[1:-1].split(',')]
	
def optionalNrrdVector(inp):
	if (inp == "none"):
		return inp
	else:
		return nrrdVector(inp)

nrrdFieldParsers = {
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
	'space origin': nrrdVector,
	'space directions': lambda fieldValue: [optionalNrrdVector(x) for x in fieldValue.split(' ')],
	'measurement frame': lambda fieldValue: [nrrdVector(x) for x in fieldValue.split(' ')],
}

#TODO: block size
# pre-calculate the list of required fields
requiredNrrdFields = ['dimension','type','encoding','sizes']


class nrrd:
	def __init__(self,filename):
		self.filename = filename
		self.filehandle = open(filename,'rb')
		rawHeaderLines = [line.strip() for line in nrrdReadHeaderLines(self.filehandle)]
		headerLines = filter(lambda x: x[0] != '#',rawHeaderLines)
		self.version = headerLines[0]
		self.rawFields = dict(filter(lambda x: len(x)==2,[line.split(': ',1) for line in headerLines]))
		self.keyvalue = dict(filter(lambda x: len(x)==2,[line.split(':=',1) for line in headerLines]))
		self.parseFields()
		self.processFields()
		self.readData(self.filehandle)
		# self.filehandle.close()
	def parseFields(self):
		self.fields = {}
		for field,value in self.rawFields.iteritems():
			assert field in nrrdFieldParsers, "Unexpected field in nrrd header: %s" % (field)
			self.fields[field] = nrrdFieldParsers[field](value)
	def processFields(self):
		# Check whether the required fields are there
		for field in requiredNrrdFields:
			assert self.fields.has_key(field), "Nrrd header misses required field: %s" % (field)
		# Process the data type
		numpyTypeString = nrrd2numpyTypeString[self.rawFields['type']]
		assert numpy.dtype(numpyTypeString).itemsize > 1 and self.fields.has_key('endian'), "Nrrd header misses required field: endian"
		if self.fields['endian'] == 'big':
			numpyTypeString = '>' + numpyTypeString
		elif self.fields['endian'] == 'little':
			numpyTypeString = '<' + numpyTypeString
		self.dtype = numpy.dtype(numpyTypeString)
	def getLineSkip(self):
		if "lineskip" in self.fields:
			return self.fields["lineskip"]
		elif "line skip" in self.fields:
			return self.fields["line skip"]
		else:
			return 0
	def getByteSkip(self):
		if "byteskip" in self.fields:
			return self.fields["byteskip"]
		elif "byte skip" in self.fields:
			return self.fields["byte skip"]
		else:
			return 0
	def getDataFile(self):
		if "datafile" in self.fields:
			return self.fields["datafile"]
		elif "data file" in self.fields:
			return self.fields["data file"]
		else:
			return None					
	def readData(self,filehandle):
		tmpShape = list(self.fields['sizes'])
		tmpShape.reverse()
		newShape = tuple(tmpShape)
		# determine byte and line skip
		lineskip = self.getLineSkip()
		byteskip = self.getByteSkip()
		datafile = self.getDataFile()
		datafilehandle = filehandle
		if datafile:
			datafilehandle = open(datafile,'rb')
		totalNumBytes = self.dtype.itemsize * numpy.array(self.fields['sizes']).prod()	
		if self.fields['encoding'] == 'raw':
			if byteskip == -1:
				datafilehandle.seek(-totalNumBytes,2)
			else:
				for i in range(lineskip):
					datafilehandle.readline()
				datafilehandle.read(byteskip)
			self.data = numpy.fromfile(datafilehandle,self.dtype)		
		elif self.fields['encoding'] == 'gzip' or self.fields['encoding'] == 'gz':
			self.gzipHandler = gzip.GzipFile(fileobj=datafilehandle)
			# unfortunately, numpy.fromfile does not support reading from a gzip
			# stream, so we'll do it like this. I have no idea what the performance
			# implications are.
			tmpData = self.gzipHandler.read()
			self.data = numpy.fromstring(tmpData,self.dtype)
		elif self.fields['encoding'] == 'bzip2' or self.fields['encoding'] == 'bz2':
			self.bz2Handler = bz2.BZ2File(fileobj=datafilehandle)
			# Again, unfortunately, numpy.fromfile does not support reading from a gzip
			# stream, so we'll do it like this. I have no idea what the performance
			# implications are.
			tmpData = self.bz2Handler.read()
			self.data = numpy.fromstring(tmpData,self.dtype)
		else:
			assert False, "Unsupported encoding."				
		# Reshape the data
		self.data = numpy.reshape(self.data,newShape)
		# Ok, assume no detached header for now
		# Another assumption: gzip
		# tmpShape = list(self.fields['sizes'])
		# tmpShape.reverse()
		# newShape = tuple(tmpShape)
		
		

		
class nrrdTests(unittest.TestCase):
	def setUp(self):
		pass


if __name__ == '__main__':
	#unittest.main()
	print "Reading nrrd file header"
	testNrrd = nrrd("helix-ten.nhdr")
	print "Done."