#!/bin/bash

#\Authour: Ali Ghayoor

####
# This bash scripts runs the testNrrd.py program on all DWI nrrd data that already
# exist in BRAINSTools build directory for testing DWIConvert.
####

# change this directory to your local build directory for BRAINSTools
BRAINSTools_Build_DIR=/scratch/BS/release-20150706

# change this directory to your local build directory for NamicExternal project
NEP_EXE_DIR=/scratch/NAMICExternalProjects/release_20150701/bin

# change this directory to your local output directory
test_root_dir=/scratch/pynrrd/TEST_readWrite

input_dir=${BRAINSTools_Build_DIR}/BRAINSTools-build/ExternalData/TestData/DWI_TestData_OUTPUTS

if [ ! -e ${test_root_dir} ]; then
  mkdir ${test_root_dir}
fi

for testDWI in ${input_dir}/*.nrrd ;
do
  filename=$(basename $testDWI)
  cleanFilename=`echo $filename | sed 's/.nrrd//g'`
  outputDir=${test_root_dir}/${cleanFilename}
  if [ ! -e ${outputDir} ]; then
    mkdir ${outputDir}
  fi
  python testNrrd.py --inputDWIScan ${testDWI} --NEP_build_path ${NEP_EXE_DIR} --outputDir ${outputDir}
done
