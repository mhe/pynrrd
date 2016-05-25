"""
testNrrd.py
==============
FIRST, DWIConvert nrrd to nii.gz
SECOND, Use existing nibabel to read .nii.gz
THIRD, Use new nrrd.py to read .nrrd file
VERIFY that the pynrrd can be converted to nibabel compliant data model
FINAL, do something interesting with manipulating DWI data (i.e. average close gradients)
Last, write averaged nrrd file to disk

Usage:
  testNrrd.py --inputDWIScan DWISCAN --outputDir OUTPUTDIR --NEP_build_path PROGRAM_PATH

Options:
  -h --help                             Show this help and exit
  -v --version                          Print the version and exit
  --inputDWIScan DWISCAN                Path to the test DWI scan
  --outputDir OUTPUTDIR                 Path to your test directory
  --NEP_build_path PROGRAM_PATH         Path to last NEP build for DWIConvert
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


def unit_vector(vector):
  """ Returns the unit vector of the vector.  """
  v_norm = np.linalg.norm(vector)
  if v_norm < 1e-4: ## allow for small tolerance
    return vector
  else:
    return vector / v_norm

def angle_between(v1, v2):
  """ Returns the angle in radians between vectors 'v1' and 'v2' """
  v1_u = unit_vector(v1)
  v2_u = unit_vector(v2)
  angle = np.arccos(np.dot(v1_u, v2_u))
  if np.isnan(angle):
    if (v1_u == v2_u).all():
      return 0.0
    else:
      return np.pi
  return angle

def angle_degrees(v1,v2):
  ang_rad=angle_between(v1,v2)
  return ang_rad*180/np.pi

def average(v1,v2):
  return np.mean( np.array([ v1, v2 ]), axis=0 )

def AverageLikeGradients(nrrd_data,nrrd_bvecs,nrrd_bvals,gradient_index):
    starting_num_bvecs = len(nrrd_bvecs)
    processed_list = [ False ] * starting_num_bvecs
    remove_list = [ False ] * starting_num_bvecs
    for i in range(0,starting_num_bvecs):
       processed_list[i] = True
       for j in range(i,starting_num_bvecs):
         if processed_list[j] == False:
           if( angle_degrees(nrrd_bvecs[i], nrrd_bvecs[j] ) < 3
               and abs(nrrd_bvals[i] - nrrd_bvals[j] ) < 1 ):
                  nrrd_bvecs[i] = average(nrrd_bvecs[i], nrrd_bvecs[j] )
                  nrrd_bvals[i] = average(nrrd_bvals[i], nrrd_bvals[j] )
                  processed_list[j] = True
                  remove_list[j] = True


    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.delete.html
    remove_indices = []
    for index in range(0,len(remove_list)):
      if remove_list[index]:
         remove_indices.append(index)

    nrrd_bvecs = np.delete( nrrd_bvecs, remove_indices, 0 )
    nrrd_bvals = np.delete( nrrd_bvals, remove_indices, 0 )
    if(gradient_index == -1): gradient_index = 0
    nrrd_data = np.delete( nrrd_data, remove_indices, gradient_index)
    return nrrd_data, nrrd_bvecs, nrrd_bvals

#######################
#######################
#######################
#######################
#######################
#######################
# Testing Code Here
if __name__ == '__main__':
  import os
  import sys
  import subprocess
  import nibabel as nib
  from dipy.io import read_bvals_bvecs

  from docopt import docopt
  argv = docopt(__doc__, version='1.0')
  print argv

  DWISCAN = argv['--inputDWIScan']
  assert os.path.exists(DWISCAN), "Input DWI scan is not found: %s" % DWISCAN

  PROGRAM_PATH = argv['--NEP_build_path']

  if argv['--outputDir'] == None:
    print("*** Output directory is set to current working directory.")
    OUTPUTDIR = os.getcwd()
  else:
    OUTPUTDIR = argv['--outputDir']
    assert os.path.exists(OUTPUTDIR), "Output directory is not found: %s" % OUTPUTDIR

  # FIRST use nibabel to read nifti formatted DWI data
  print("Making some nifti formatted data")
  arg1='--inputVolume'+' '+str(DWISCAN)
  arg2='--conversionMode NrrdToFSL'
  arg3='--outputVolume'+' '+os.path.join(OUTPUTDIR,'testFSL.nii.gz')
  subprocess.call([os.path.join(PROGRAM_PATH,'DWIConvert'), arg1, arg2, arg3])

  # SECOND
  nifti_file=os.path.join(OUTPUTDIR,'testFSL.nii.gz')
  fbvec=os.path.join(OUTPUTDIR,'testFSL.bvec')
  fbval=os.path.join(OUTPUTDIR,'testFSL.bval')

  img = nib.load(nifti_file)
  data = img.get_data()

  nifti_bvals, nifti_bvecs = read_bvals_bvecs(fbval, fbvec)
  print nifti_bvals
  print nifti_bvecs
  print type(nifti_bvals)
  print type(nifti_bvecs)

  #THIRD use nrrd.py + new header parser to read data
  nrrd_data,myOptions,nrrd_bvecs,nrrd_bvals, gradient_index = ReadNAMICDWIFromNrrd(DWISCAN)

  print type(nrrd_bvecs)
  print type(nrrd_bvals)

  print np.subtract(nifti_bvecs,nrrd_bvecs)
  print np.subtract(nifti_bvals,nrrd_bvals)

  # FINAL
  # Write an algorithm purely in python to average similar gradients together
  #
  print("Number of components BEFORE averaging: {0}".format(len(nrrd_bvecs)))

  nrrd_data,nrrd_bvecs,nrrd_bvals=AverageLikeGradients(nrrd_data,nrrd_bvecs,nrrd_bvals,gradient_index)

  print("Number of components AFTER averaging: {0}".format(len(nrrd_bvecs)))
  #print("4th dimension of nrrd_data after averaging: {0}".format(len(nrrd_data[:,:,:,1])))
  outputNrrdFilename=os.path.join(OUTPUTDIR,'averagedNrrdFile.nrrd')
  WriteNAMICDWIToNrrd(outputNrrdFilename,nrrd_data,nrrd_bvecs,nrrd_bvals,myOptions)
  print("Output nrrd file is written to the disk: {0}.".format(outputNrrdFilename))

  sys.exit(0)
