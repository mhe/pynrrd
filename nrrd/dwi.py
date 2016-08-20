"""
dwi.py

A python implementation that provides important elements for using DWI imaging data in nrrd format.
See http://teem.sourceforge.net/nrrd/format.html for the specification.

"""

__author__ = 'johnsonhj,aghayoor'

import nrrd
import numpy as np
from math import sqrt
from collections import OrderedDict

class nrrdDWIHeader:
    """A helper class for manipulating header information
    from a nrrd DWI data set into a nibabel compliant
    format"""
    def __init__(self,pynrrdDataModel):
        self.modality=None                      #Matches NRRD File
        self.global_BValue=None                 #Matches NRRD File
        self.gradientUnormalizedVectors=[None] #Matches NRRD File

        self.gradientIndex=-1
        self.gradientBValues=[None]             #Computed
        self.gradientVectors=[None]             #Computed
        self._ConvertNrrdToNibabelDWIDataModel(pynrrdDataModel)

    def Print(self):
        print("global_BValue {0}".format(self.global_BValue) )
        print("modality {0}".format(self.modality) )
        print("gradientBValues {0}".format(self.gradientBValues) )
        print("gradientDirections {0}".format(self.gradientUnormalizedVectors) )

    def _getGradientStorageIndex(self,pynrrdDataModel):
        """The 4D index that has separate gradients.
        all other directions are the spatial dimensions."""
        gradient_index=-1;
        centerings=pynrrdDataModel['centerings']
        numdwidims=len(centerings)
        for test_index in range(0,numdwidims):
            if centerings[test_index] not in ['cell']:
                gradient_index=test_index
        self.gradientIndex = gradient_index

    def _ExtractGlobalBValue(self, pyNrrdKVUnknownMetaData):
        globalBValueString=pyNrrdKVUnknownMetaData.get(u'DWMRI_b-value','0').lstrip().rstrip()
        self.global_BValue=float( globalBValueString )

    def _ExtractUnormalizedBValues(self,pyNrrdKVUnknownMetaData,pynrrdDataModel):
        """Unnormalized data values from the nrrd files, where the
        magnitude is reflective of the scale relative to the global_BValue"""
        self._getGradientStorageIndex(pynrrdDataModel)
        numGradients = pynrrdDataModel[u'sizes'][self.gradientIndex]
        self.gradientUnormalizedVectors= np.array( [ [ None, None, None ] for x in range(0,numGradients) ] )
        gvec_Fields=pyNrrdKVUnknownMetaData.copy() #Clone so we can remove items
        for k,v in gvec_Fields.iteritems():
            if k.startswith("DWMRI_gradient_"):
                index=int(k.split('_')[2])
                self.gradientUnormalizedVectors[index,:]=np.array([ float(x) for x in v.rstrip().lstrip().split() ],
                                                    copy=True, order='C', ndmin=1)
                pyNrrdKVUnknownMetaData.pop(k)


    def _ExtractDWIModality(self,pyNrrdKVUnknownMetaData):
        self.modality=pyNrrdKVUnknownMetaData.get("modality","UNKNOWN").lstrip().rstrip()

    def _ComputeNormalizedBvecBVals(self,pyNrrdKVUnknownMetaData,pynrrdDataModel):
        self._ExtractGlobalBValue(pyNrrdKVUnknownMetaData)
        self._ExtractUnormalizedBValues(pyNrrdKVUnknownMetaData,pynrrdDataModel)
        self._ComputeNormalizedGradientsAndBValues()

    def _ComputeNormalizedGradientsAndBValues(self):
        """Following conventions of NRRD format, expand
        to normalized vectors and estimate BValues
        :return: void
        """
        numGradients=len( self.gradientUnormalizedVectors )

        self.gradientVectors = np.array(self.gradientUnormalizedVectors)
        self.gradientBValues = np.array( [ self.global_BValue ] * numGradients )
        for index in range(0,numGradients):
            gv = self.gradientUnormalizedVectors[index]
            norm=np.linalg.norm(gv)
            if norm < 1e-2:
                self.gradientVectors[index] = gv * 0.0
                self.gradientBValues[index] = 0.0
            elif ( abs( 1.0-norm ) > 1e-4 ): # Avoid rescaling if norm is almost one
                self.gradientVectors[index] = gv/norm
                b_i = self.global_BValue * (norm**2) # norm = sqrt(b_i/b_max)
                self.gradientBValues[index] = float("{0:.1f}".format(b_i))

    def _ConvertNrrdToNibabelDWIDataModel(self, pynrrdDataModel):
        pyNrrdKVUnknownMetaData=pynrrdDataModel['keyvaluepairs']
        self._ExtractDWIModality(pyNrrdKVUnknownMetaData)
        self._ExtractGlobalBValue(pyNrrdKVUnknownMetaData)
        self._ComputeNormalizedBvecBVals(pyNrrdKVUnknownMetaData,pynrrdDataModel)

def ReadNAMICDWIFromNrrd(filename):
    nrrd_dwi_data,nrrd_dwi_header=nrrd.read(filename)
    #print("my options: {0}".format(nrrd_dwi_header))
    nibabelDataModelDWI=nrrdDWIHeader(nrrd_dwi_header)
    nrrd_dwi_bvec=nibabelDataModelDWI.gradientVectors
    nrrd_dwi_bval=nibabelDataModelDWI.gradientBValues
    gradient_index=nibabelDataModelDWI.gradientIndex
    return (nrrd_dwi_data, nrrd_dwi_header, nrrd_dwi_bvec, nrrd_dwi_bval, gradient_index)

def WriteNAMICDWIToNrrd(filename, data, bvecs, bvals, options=None):
    """
    :param filename: The filename to write to disk
    :param data: The numpy 4d file to be written
    :param bvecs: The bvecs values to be written
    :param bvals: The bvals to be written
    :param options: Optional parameters to be written to the nrrd header
    :return:
    """
    keyvaluePairDict=OrderedDict()
    if options is not None:
        keyvaluePairDict=OrderedDict( options.get( 'keyvaluepairs',OrderedDict() ))

    ## First remove all existing bval/bvec fields from dictionary
    keyvaluePairDict.pop('modality',None)

    for k,v in keyvaluePairDict.iteritems():
        if k.startswith('DWMRI_'):
            keyvaluePairDict.pop(k, None)

    keyvaluePairDict[u'modality']=u'DWMRI'
    maxBvalue = max(bvals)
    keybval=u'DWMRI_b-value'
    keyvaluePairDict[keybval]=maxBvalue

    numGradients = len(bvecs)
    for index in range(0,numGradients):
        this_scale = sqrt(bvals[index] / maxBvalue)
        this_vec = [ x * this_scale for x in bvecs[index]]
        #print bvecs[index],this_vec

        keyvec=u'DWMRI_gradient_{:04d}'.format(index)
        # convert gradient vector value to string (only for consistency with input)
        vec_string= lambda this_vec: u''.join(nrrd._convert_to_reproducible_floatingpoint(x)+'  ' for x in this_vec).rstrip()
        keyvaluePairDict[keyvec]=vec_string(this_vec)
    options['keyvaluepairs']=keyvaluePairDict
    options['encoding']='gzip' # Always use gzip compression for DWI data
    nrrd.write(filename,data,options)
