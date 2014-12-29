# In shell:
#
#  cd dicom-data/P31067/
#  
#  cd CTSTD20091217/
#  ~/work/packages/mricron/dcm2nii dcm112628116.0* 
#  
#  ls 20091217_11373252STHHalfbody2Ds003a001.nii.gz 
#  
#  cd ../
#  cd PET2DACWB20091217/
#  
#  ~/work/packages/mricron/dcm2nii dcm112600025.0*
#  
#  ls 20091217_113901STHHalfbody2Ds004a001.nii.gz 
 
# After script, run a command like this to visualise:
#
# rview CTSTD20091217/20091217_11373252STHHalfbody2Ds003a001.nii.gz \
#    PET2DACWB20091217/20091217_113901STHHalfbody2Ds004a001.nii.gz  \
#    -seg ct-roi.nii.gz  -lut lut.seg  -linear -smax 10000 -mix  \
#    -scolor red -origin -15 -14 -209 -res 1.5 -tmax 2200

# Or more generally as
#
# rview ${ctDir}/${ctImage} ${petDir}/${petImage}  \
#    -seg ct- roi.nii.gz  -lut lut.seg  -linear -smax 10000 -mix  \
#    -scolor red -origin -15 -14 -209 -res 1.5 -tmax 2200


import sys, os

# for debugging
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
import nibabel

import numpy

import scipy

#irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'
#sys.path.append(irtkDir)
#
#import subprocess


 
##########################################################################

def main(*args):
  
  # Where are the image data
  imageDir = '/Users/paulaljabar/work/petros/temp/dicom-data/P31067'
  
  petDir = 'PET2DACWB20091217'
  ctDir = 'CTSTD20091217'
  
  petImgName = '20091217_113901STHHalfbody2Ds004a001.nii.gz'
  ctImgName = '20091217_11373252STHHalfbody2Ds003a001.nii.gz'
  # ctImgName = 'o20091217_11373252STHHalfbody2Ds003a001.nii.gz'
  
  
  os.chdir(imageDir)

  petImgFile = os.path.join(imageDir, petDir, petImgName)
  ctImgFile = os.path.join(imageDir, ctDir, ctImgName)
  
  petImg = nibabel.load(petImgFile)
  ctImg = nibabel.load(ctImgFile)
  
  
  # Matlab struct with various other types of data, including ROI definition
  matFileDir = '/Users/paulaljabar/work/petros/temp/roi-data/ROI_store_p31067'
  matFileName = 'struc_tex_ANON035210165200_lbl_154-166_roi_1_rnd_5667.mat'
  matFile = os.path.join(matFileDir, matFileName)

  matData = scipy.io.loadmat(matFile)
 
  # Recover flat indices into the CT array that define the voxels of the ROI.
  inds = matData['struc_tex']['hot_vox_ind_tot'][0][0].squeeze()
    
  ctData = ctImg.get_data()
  petData = petImg.get_data()
  
  petROIdata = matData['struc_tex']['mini_ac_1'][0][0].squeeze()
  
  # The main bit:
  roiData = numpy.zeros(ctData.shape)
  
  xdim,ydim,zdim = ctData.shape
  
  # Get a list of tuples to represent the image coordinates of each of the ROI
  # voxels. Need to subtract 1 from variable inds because it is intended for
  # matlab where 1-indexing is used
  ijks = [ numpy.unravel_index(i, ctData.shape, order='F') for i in inds-1 ]

  # Loop over all voxels in ROI:
  for ijk in ijks:    
    i,j,k = ijk
    # Note the mangling of i and j here, they are not simply used directly
    roiData[j, ydim-i, k] = 1
    


  # Save result:  
  outputName = os.path.join(imageDir, 'ct-roi.nii.gz')

  roiImg = nibabel.Nifti1Image(roiData, ctImg.get_affine())
  nibabel.save(roiImg, outputName)

##########################################################################

if __name__ == '__main__':
  sys.exit(main(*sys.argv))

