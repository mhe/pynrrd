__author__ = 'johnsonhj'

import nrrd
import numpy as np
class nrrdDWIHeader:
    """A helper class for manipulating header information
    from a nrrd DWI data set into a nibabel compliant
    format"""
    def __init__(self,pynrrdDataModel):
        self.modality=None                      #Matches NRRD File
        self.global_BValue=None                 #Matches NRRD File
        self.gradientUnormalizedVectors=[None] #Matches NRRD File

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
        return gradient_index

    def _ExtractGlobalBValue(self, pyNrrdKVUnknownMetaData):
        globalBValueString=pyNrrdKVUnknownMetaData.get(u'DWMRI_b-value','0').lstrip().rstrip()
        self.global_BValue=float( globalBValueString )

    def _ExtractUnormalizedBValues(self,pyNrrdKVUnknownMetaData,pynrrdDataModel):
        """Unnormalized data values from the nrrd files, where the
        magnitude is reflective of the scale relative to the global_BValue"""
        gradient_index = self._getGradientStorageIndex(pynrrdDataModel)
        numGradients = pynrrdDataModel[u'sizes'][gradient_index]
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
            elif ( abs( 1.0-norm ) > 1e-4 ): #Avoid B0 and need greater than 1e-4 from 1. for rescaling
                self.gradientVectors[index] = gv/norm
                self.gradientBValues[index] = self.global_BValue/norm

    def _ConvertNrrdToNibabelDWIDataModel(self, pynrrdDataModel):
        pyNrrdKVUnknownMetaData=pynrrdDataModel['keyvaluepairs']
        self._ExtractDWIModality(pyNrrdKVUnknownMetaData)
        self._ExtractGlobalBValue(pyNrrdKVUnknownMetaData)
        self._ComputeNormalizedBvecBVals(pyNrrdKVUnknownMetaData,pynrrdDataModel)

def ReadNAMICDWIFromNrrd(filename):
    nrrd_dwi_data,nrrd_dwi_header=nrrd.read(filename)
    nibabelDataModelDWI=nrrdDWIHeader(nrrd_dwi_header)
    nrrd_dwi_bvec=nibabelDataModelDWI.gradientVectors
    nrrd_dwi_bval=nibabelDataModelDWI.gradientBValues
    return (nrrd_dwi_data, nrrd_dwi_header, nrrd_dwi_bvec, nrrd_dwi_bval)

def WriteNAMICDWIToNrrd(filename, data, options, bvec, bval):
    # Not yet filled in
    pass



#######################
#######################
#######################
#######################
#######################
#######################
# Testing Code Here
# FIRST DWIConvert nrrd to nii.gz
# SECOND Use existing nibabel to read .nii.gz
# THIRD Use new nrrd.py to read .nrrd file
# VERIFY that the pynrrd can be converted to nibabel compliant data model
# FINAL: do something interesting with manipulating DWI data (i.e. average close gradients)

# FIRST use nibabel to read nifti formatted DWI data
"""
echo "Making some nifti formatted data"
DWIConvert \
   --inputVolume /Users/johnsonhj/src/NEP-11/BRAINSTools-build/ExternalData/TestData/DWI_TestData_OUTPUTS/SiemensVerio.nrrd  \
   --conversionMode NrrdToFSL \
   --outputVolume testFSL.nii.gz
"""
# SECOND
import nibabel as nib
nifti_file='/scratch/testFSL.nii.gz'
fbvec='/scratch/testFSL.bvec'
fbval='/scratch/testFSL.bval'

import nibabel as nib
img = nib.load(nifti_file)
data = img.get_data()

from dipy.io import read_bvals_bvecs
nifti_bvals, nifti_bvecs = read_bvals_bvecs(fbval, fbvec)
print nifti_bvals
print nifti_bvecs
print type(nifti_bvals)
print type(nifti_bvecs)

#THIRD use nrrd.py + new header parser to read data

#ds='/Users/johnsonhj/src/NEP-11/BRAINSTools-build/ExternalData/TestData/DWI_TestData_OUTPUTS/PhilipsAchieva2.nrrd'
ds='/Users/johnsonhj/src/NEP-11/BRAINSTools-build/ExternalData/TestData/DWI_TestData_OUTPUTS/SiemensVerio.nrrd'
myNrrd,myOptions,nrrd_bvecs,nrrd_bvals = ReadNAMICDWIFromNrrd(ds)

print type(nrrd_bvecs)
print type(nrrd_bvals)

print np.subtract(nifti_bvecs,nrrd_bvecs)
print np.subtract(nifti_bvals,nrrd_bvals)

# FINAL
## Ali
# Write an algorithm purely in python to average similar gradients together
#
# starting_num_bvecs = len(nrrd_bvecs)
# processed_list = [ False ] * starting_num_bvecs
# remove_list = [ False ] * starting_num_bvecs
# for i in range(0,starting_num_bvecs):
#     processed_list[i] = True
#     for j in range(i,starting_num_bvecs):
#       if processed_list[j] == False:
#         if( angle_between(nrrd_bvecs[i], nrrd_bvecs[j] ) < 3_degrees 
#             && abs(nrrd_bvals[i] - nrrd_bvals[j] ) < 1 ):
#                nrrd_bvecs[i] = average(nrrd_bvecs[i], nrrd_bvecs[j] )
#                nrrd_bvals[i] = average(nrrd_bvals[i], nrrd_vals[j] )            
#                processed_list[j] = True
#                remove_list[j] =True
#
# # http://docs.scipy.org/doc/numpy/reference/generated/numpy.delete.html
# for index in remove_list:
#    if remove_list[index] == True:
#         np.delete( bvecs, index, 0 )
#         np.delete( bvals, index, 0 )
#         np.delete( nrrd_data, (:,:,:,index), 0)

      
