# For Louise Thomas and Jimmy Bell.

import os
import sys
import argparse

import numpy
from scipy import ndimage

sys.path.append('/Users/paulaljabar/Python')
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
sys.path.append('/Users/paulaljabar/work/packages/python/scikit-learn')

from PIL import Image
import nibabel as nib

from sklearn.cluster import KMeans

from functools import reduce

# For debugging
# import matplotlib.pyplot as plt
# from numpy.core.fromnumeric import ndim
# import subprocess

#####################################################################     

def printCommand(cmd):
  mystr = reduce(lambda x,y : x + ' ' + y, cmd)
  print(mystr)


def main(*args):

  helpText = "Estimate a thumbnail showing a roughly coronal cross section \
  from a whole body data MR image. Save the result in a 2-D image file (png or jpg)."

  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "MR image input. The z-direction is assumed to be superior inferior and the \
  x direction is assumed to be left-right"
  parser.add_argument("input", help=helpText, type=str)
  
  helpText = "2D image output, filename.png or filename.jpg"
  parser.add_argument("output", help=helpText, type=str)
  
  helpText = "Number: Threshold used as a boundary for noise. Any value in the MR data \
  below the threshold is assumed to be noise and set to zero. This is part of \
  the estimation for what is body non-body. If not set manually, then it is guessed \
  from the data in the first slice."
  parser.add_argument("-threshold", help=helpText, type=int, metavar='number')
  
  ################################
    
  args = parser.parse_args()
  
  inputImgName = args.input
  outputImgName = args.output
  
  outputSuffix = outputImgName[-4:]
  if not outputSuffix == '.png' and not outputSuffix == '.jpg':
    print('Output file should have .png or .jpg suffix ')
    exit(code=1) 
     
  img = nib.load(inputImgName)
  
  imgData = img.get_data()

  dims = imgData.shape
  
  xdim = dims[0]
  ydim = dims[1]
  zdim = dims[2]
  
  tdim = 1
  
  if len(dims) > 3:
    tdim = dims[3]
  
  if len(dims) < 4:
    imgData.shape = imgData.shape + (1,)
  
  
  if tdim > 1:
    print('Only one volume per image allowed')
    exit(code=1)
    
  ################

  # Determine threshold
    
  thresh = args.threshold
  
  if thresh is None:
  
    # Guess a threshold below which we assume the MR values are noise.
  
    # Take first slice data and use them to determine a lower threshold for 'real'
    # data.
    temp = imgData[:,:,0,:].reshape( (-1,1) )
    
    thresh = numpy.percentile(temp, 99)
    km = KMeans(n_clusters=2)
    km.fit(temp)
    labels = km.labels_
    
    inds0 = numpy.where(labels == 0)[0]
    inds1 = numpy.where(labels == 1)[0]
    if numpy.size(inds0) > numpy.size(inds1):
      inds = inds0
    else:
      inds = inds1

    thresh = numpy.percentile(temp[inds], 99)



  ################

  # Apply threshold
  mystr = 'Thresholding at {:0.1f}'.format( float(thresh) )
  print(mystr)
  
  tempImgData = numpy.copy(imgData)
  sliceShape = imgData[:,:,0,:].shape
  
  # Make an initial mask based on thresholding the image.
  for z in range(zdim):
    currSlice = numpy.copy(tempImgData[:,:,z,:].squeeze())
    currSlice[currSlice <= thresh] = 0
    currSlice[currSlice > thresh]  = 1    
    tempImgData[:,:,z,:] = numpy.reshape(currSlice, sliceShape)

  ################
  
  # Morphological cleaning
  
  # Previously used irtk tools (see below).

  # Morphological opening using scipy.ndimage.filters:
  # Erode:
  temp = ndimage.filters.minimum_filter(tempImgData, size=3)
  # Dilate:
  mask = ndimage.filters.maximum_filter(temp, size=3)
  
  ################

  # Get mask's largest connected component.
    
  # Label connected components in mask
  label_im, nb_labels = ndimage.label(mask)
    
  # Get largest component
  biggestLabel = 1
  maxSize = 0
  for i in range(1, nb_labels):
    currSize = numpy.count_nonzero(label_im == i)
    if currSize > maxSize:
      maxSize = currSize
      biggestLabel = i
    if maxSize > 0.5 * numpy.count_nonzero(label_im):
      break
  
  mystr = 'biggest label : {:d}'.format(i)
  print(mystr)
  
  mask = numpy.zeros(label_im.shape)
  mask[label_im == biggestLabel] = 1
  
  ################

  # For debugging have a pre-made mask:
  
  
#  outImg = nib.Nifti1Image(mask, img.get_affine())
#  nib.save(outImg, 'pre-made-mask.nii.gz')

#  preMadeMask = nib.load('pre-made-mask.nii.gz')
#  mask = preMadeMask.get_data()
  
  
  ################

  # Guess a range of z slice indices where we have some expectation to find a
  # part of the body.
  
  maskedImgData = mask * imgData
  
  sx = numpy.sum(mask, 0)
  sxy = numpy.sum(sx, 0).squeeze()

  validFraction = 0.005

  inds = numpy.where(sxy > validFraction * xdim * xdim)
  startZ = inds[0][0]
  endZ = inds[0][-1]
  
  ################

  # The Main Part:
  
  # For each x-z point, identify a y-value that is approximately at the centre
  # of the tissue
    
  yCentres = numpy.zeros( (xdim,zdim) )
  
  yInds = numpy.asarray(list(range(ydim)))
  yIndsTiled = numpy.tile(yInds, (xdim, 1))
  
  for z in range(startZ, endZ):
    currSlice = numpy.copy(mask[:,:,z,:].squeeze())
    currSliceBlur = ndimage.filters.gaussian_filter(currSlice, 3)

    temp = numpy.sum(currSliceBlur * yIndsTiled, axis=1)
    sumW = numpy.sum(currSliceBlur, axis=1)
    inds = sumW > 0
    temp[inds] = temp[inds] / sumW[inds]
    
    # Repeat values to the ends of the line
    inds = numpy.where(temp > 0)[0]
    temp[ 0:inds[0] ] = temp[ inds[0] ]
    temp[ inds[-1]: ] = temp[ inds[-1] ]
    
    # Where are the zeros still
    inds = numpy.where(temp == 0)[0]
    
    if len(inds) == 0:
      yCentres[:,z] = temp
      continue
    
    # can be in separate runs
    indJumps = numpy.where(inds[1:] - inds[:-1] > 1)[0]
    
    if len(indJumps) == 0:
      # Only have one run
      startInds = [ inds[0]-1 ]
      endInds   = [ inds[-1]+1 ]
    else:
      startInds = [inds[0]-1]
      startInds = startInds + list( inds[indJumps+1] -1 )
      endInds = list( inds[indJumps] )
      endInds = list( 1+inds[indJumps] ) + list( [ inds[-1]+1 ] )
      
            
    for i in range(len(startInds)):
      startInd = startInds[i]
      endInd   = endInds[i]
      startVal = temp[ startInd ]
      endVal   = temp[ endInd   ]
      xx = numpy.asarray(list( range(startInd, endInd+1)) )
      yy = startVal + (endVal - startVal) * (xx - startInd) / 1.0 / (endInd - startInd)
      temp[startInd:endInd] = yy[:-1]

    
    yCentres[:,z] = temp

  for z in range(startZ):
    yCentres[:,z] = yCentres[:,startZ]
    
  for z in range(endZ, zdim):
    yCentres[:,z] = yCentres[:,endZ-1]

  # Some smoothing
  temp = numpy.copy(yCentres)
  yCentres = ndimage.gaussian_filter(temp, 2)

  ##################################
    
  # Generate the output: This will be a two-D image that represents a non-
  # linear cross section through the body in a coronal sense approximately. It
  # is not truly coronal as we are not using a plane.
  
  outData = numpy.zeros( (xdim, zdim) )
  
  for k in range(zdim):
    for i in range(xdim):
      j = int( numpy.round(yCentres[i,k]) )
      outData[i,k] = imgData[i, j, k]
#      j = yCentres[i,k]
#      outData[i,k] = interpolate.interp2 ??? should interpolate better than NN really
      
      
  ##################################
    
  pilIm = Image.new("RGB", (xdim, zdim), "white")
  pixels = numpy.array(pilIm)
  
  temp = numpy.flipud(outData.T)
  temp = 255.0 * temp / numpy.max(temp[:])
  
  for i in range(3):
    pixels[:,:,i] = temp

  pilIm2 = Image.fromarray(pixels)
  
  # Scale the pixel dimensions so that the aspect ratio is roughly correct.
  
  h = img.get_header()
  pixDims = h['pixdim']
  scale = int( numpy.round(pixDims[3] / pixDims[1]) )
  pilIm = pilIm2.resize((xdim, scale*zdim), Image.BILINEAR)
  
  if outputSuffix == '.jpg':
    pilIm.save(outputImgName, "JPEG")
  else:
    pilIm.save(outputImgName, "PNG")
    
  exit(0)


  ###############  

  
  # IRTK tools for morphological cleaning.
#  # Save to a temporary file, clean up a bit.  
#  tmpImgName = 'temp-' + str(numpy.random.randint(10000, 99999)) + '.nii'
#  outImg = nib.Nifti1Image(tempImgData, img.get_affine())
#  nib.save(outImg, tmpImgName)
#  
#  cmd = ['erosion' , tmpImgName, tmpImgName]
#  print('Eroding threshold mask')
#  printCommand(cmd)
#  output = subprocess.check_output(cmd)
#  print(output)
#  print('Dilating threshold mask')
#  cmd = ['dilation' , tmpImgName, tmpImgName]
#  printCommand(cmd)
#  output = subprocess.check_output(cmd)
#  print(output)
#  # Load cleaned threshold mask back in   
#  maskImg = nib.load(tmpImgName)
#  mask = maskImg.get_data()


#####################################################################     

if __name__ == '__main__':
  sys.exit(main(*sys.argv))
  

