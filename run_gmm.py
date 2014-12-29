

import sys, os
# for debugging
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
import nibabel as nib

import argparse

import numpy
import tempfile

sys.path.append('/Users/paulaljabar/work/scripts/python')
import imageUtilsPythonPA

import subprocess

irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'
sys.path.append(irtkDir)

skDir = '/Users/paulaljabar/work/packages/python/scikit-learn/build/temp.macosx-10.9-intel-2.7'
sys.path.append(skDir)
skDir = '/Users/paulaljabar/work/packages/python/scikit-learn/'
sys.path.append(skDir)

from sklearn import mixture






def main(*args):
  
#  helpText = "   Get an affine transformation between two images based on their \
#  header information. The resulting transformation will define correspondence \
#  between voxels with the same image coordinates (indices) in each image. This \
#  can be useful if two images same grid but different orientations, for example."
#  
#  parser = argparse.ArgumentParser(description=helpText)
#  
#  helpText = "Target Image: filename.nii.gz"
#  parser.add_argument("targetImage", type=str, help=helpText)
#
#  helpText = "Source Image: filename.nii.gz"
#  parser.add_argument("sourceImage", help=helpText, type=str)
#  
#  helpText = "Transformation: name.dof"
#  parser.add_argument("dofout", help=helpText, type=str)
#  
##  helpText = "Optional argument"
##  parser.add_argument("-opt", type=int, nargs='+', help=helpText, metavar='label')
#
#  #############################################################
#      
#  args = parser.parse_args()


  dir = '/Users/paulaljabar/work/collab/ucl/robsMR/resampled'
  os.chdir(dir)
  
  t2Img = nib.load('t2-n4.nii.gz')
  t1Img = nib.load('t1.nii.gz')
  t1SagImg = nib.load('t1-sagittal.nii.gz')
  maskImg  = nib.load('brainmask2.nii.gz')
  
  t2data = t2Img.get_data()
  t1data = t1Img.get_data()
  t1sagData = t1SagImg.get_data()
  maskData = maskImg.get_data()
  
  inds = maskData > 0
  
  t2gmmData = t2data[inds].reshape(-1,1)
  t1gmmData = t1data[inds].reshape(-1,1)
  t1sagGmmData = t1sagData[inds].reshape(-1,1)
  
  gmmData = numpy.concatenate((t2gmmData, t1gmmData, t1sagGmmData), axis=1 )

  nComps = 5
  gmm = mixture.GMM(nComps)
  
  gmm.fit(gmmData)
  
  pred = gmm.predict(gmmData)
  pred = pred + numpy.ones(pred.shape)
  
  newLabels = numpy.copy(maskData)
  
  newLabels[inds] = pred

  outImg = nib.Nifti1Image(newLabels, maskImg.get_affine())
  outputName = 'gmm-multimodal-hardLabels.nii.gz'
  nib.save(outImg, outputName)

  
  predProbs = gmm.predict_proba(gmmData)
  for i in range(nComps):
    outputName = 'gmm-multimodal-class-{:02d}.nii.gz'.format(i+1)
    outData = numpy.zeros(maskData.shape)
    outData[inds] = predProbs[:,i]
    outImgClass = nib.Nifti1Image(outData, maskImg.get_affine())
    nib.save(outImgClass, outputName)
  
#  dir = '/Users/paulaljabar/work/collab/ucl/robsMR/nstk_seg/t2'
#  os.chdir(dir)
#  
#  
#  labelImg = nib.load('result/kmeans-5classes.nii.gz')
#
#  labels = labelImg.get_data()
#  
#  mrImg = nib.load('nuCorrected/withStemBrain_N3.nii.gz')
#  
#  mrData = mrImg.get_data()
#  
#  dataForGMM = mrData[labels == 5]
#  
#  gmm = mixture.GMM(3)
#  
#  gmm.fit(dataForGMM)
#  
#  pred = gmm.predict(dataForGMM)
#  
#  newLabels = numpy.copy(labels)
#  
#  temp = newLabels[labels == 5]
#  temp = temp + pred
#  newLabels[labels == 5] = temp
#  
#          
#  outImg = nib.Nifti1Image(newLabels, labelImg.get_affine())
#  outputName = 'bla.nii.gz'
#  nib.save(outImg, outputName)
#
#  
#  print labels.shape
#  


  
if __name__ == '__main__':
  sys.exit(main(*sys.argv))


