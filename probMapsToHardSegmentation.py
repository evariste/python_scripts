#!/usr/bin/python

# Paul Aljabar. December 2013.

import os
import sys

# for debugging
# sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')

import nibabel as nib
import numpy
import argparse

#####################################################################     

def main(*args):

  helpText = "Convert a set of probabilistic label maps into a hard label image.\
              All images must have the same voxel grid."
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "Output image (name.nii or name.nii.gz)"
  parser.add_argument("output", help=helpText, type=str)
  
  helpText="Input images, label maps that need to be combined"
  parser.add_argument("-inputImages", type=str, nargs='+', help=helpText, metavar='img')
  
  helpText = "Optional: Labels to assign for each input image. \
    Assumed to be in presented correct order for given input images. \
    (Default: 1, 2, . . . )."
  parser.add_argument("-labels", type=int, nargs='+', help=helpText, metavar='label')

  #############################################################
      
  args = parser.parse_args()
  
  inputImages = args.inputImages
  labels = args.labels
    
  if labels is None:
    labels = range(1, 1+len(inputImages))
  
  if not len(labels) == len(inputImages):
    print 'Warning: Number of input images and label images do not match. Using labesl 1 to {:d}'.format(len(inputImages))
    labels = range(1, 1+len(inputImages))
    
  
  print 'Input images: ', inputImages
  print 'Labels      : ', labels
  print ''
    
  img = nib.load(inputImages[0])
  imgData = img.get_data()

  # Storage for output label image.    
  labelsOut = numpy.zeros(imgData.shape, dtype=numpy.int16)

  sumProbs = numpy.zeros(imgData.shape)
  
  # find sum over all images for each voxel
  for n in range(len(inputImages)):
    img = nib.load(inputImages[n])
    imgData = img.get_data()
    sumProbs = sumProbs + imgData

  # Assume this value represents 100% occupancy.    
  maxProbVal = numpy.max(sumProbs)
  
  # background label probabity is 100% - total sum over all, it has label zero
  # and we can assume it is winning so far.
  
  winningProb = maxProbVal * numpy.ones(imgData.shape) - sumProbs

  for n in range(len(inputImages)):
    print '     Processing image {:s}'.format(inputImages[n])
    img = nib.load(inputImages[n])
    imgData = img.get_data()
    
    if not cmp(imgData.shape, labelsOut.shape) == 0:
      print 'Error, image dimensions not all the same'
      exit(code = 1)
    
    # Where does current map beat the winning probability?
    inds = winningProb <= imgData
    labelsOut[inds]   = labels[n]
    winningProb[inds] = imgData[inds]
  
  outImg = nib.Nifti1Image(labelsOut, img.get_affine())
  outImg.set_data_dtype(int16)
  nib.save(outImg, args.output)

#####################################################################     

if __name__ == '__main__':
  sys.exit(main(*sys.argv))
  

