#!/bin/bash

# \Author: Ali Ghayoor

####
# This bash scripts runs the test_dwi.py program on all DWI nrrd formatted files
# that are used for testing in BRAINSTools.
#
# test_dwi.py is a program that is designed to test the functionality of the
# "dwi" submodule in dealing with DWI meta data.
####

# Set your local build directory for BRAINSTools
BRAINSTools_BUILD_DIR="$1"

# Set your output test directory
OUTPUT_DIR="$2"

DWIConvert_EXE_DIR=${BRAINSTools_BUILD_DIR}/bin
input_dir=${BRAINSTools_BUILD_DIR}/BRAINSTools-build/ExternalData/TestData/DWI_TestData_OUTPUTS

if [ ! -e ${OUTPUT_DIR} ]; then
  mkdir ${OUTPUT_DIR}
fi

for testDWI in ${input_dir}/*.nrrd ;
do
  filename=$(basename $testDWI)
  cleanFilename=`echo $filename | sed 's/.nrrd//g'`
  outputDir=${OUTPUT_DIR}/${cleanFilename}
  if [ ! -e ${outputDir} ]; then
    mkdir ${outputDir}
  fi
  python test_dwi.py --inputDWIScan ${testDWI} --program_path ${DWIConvert_EXE_DIR} --outputDir ${outputDir}
done
