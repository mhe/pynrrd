#!/bin/bash

#==========================
#Experiment 1
#--------------------------
python testNrrd.py \
--inputDWIScan /Users/johnsonhj/src/NEP-11/BRAINSTools-build/ExternalData/TestData/DWI_TestData_OUTPUTS/SiemensVerio.nrrd \
--NEP_build_path /Users/johnsonhj/src/NEP-11/bin \
--outputDir /scratch/TEST1

#==========================
#Experiment 2
#--------------------------
python testNrrd.py \
--inputDWIScan /Shared/johnsonhj/HDNI/20150319_DWIProcessing/Results/FMRI_HD_024/0506/10595/Outputs/CorrectedDWI_in_T2Space.nrrd \
--NEP_build_path /Users/johnsonhj/src/NEP-11/bin \
--outputDir /scratch/TEST2
