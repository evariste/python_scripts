import os
import sys
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
import nibabel as nib
import numpy
import argparse


def main(*args):

  
  helpText = "   Split the input image into slices. If the image grid is indexed by i, j and k, \
each slice is assumed to be indexed by a fixed value of k."
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "Input image to be split."
  parser.add_argument("input", type=str, help=helpText)

  helpText = "Prefix to use for output images, each will have a format 'prefix-NNN.nii.gz' "
  parser.add_argument("outputPrefix", help=helpText, type=str)
  
  helpText = "Indices (index) of particular slices (slice) to extract. \
    Slices are assumed to be zero-indexed."
  parser.add_argument("-indices", type=int, nargs='+', help=helpText, metavar='label')

  #############################################################
      
  args = parser.parse_args()

  
    
  inputFilename = args.input
  outputPrefix = args.outputPrefix

  img = nib.load(inputFilename)
  imgDType = img.get_data_dtype()

  imgData = img.get_data().astype(imgDType)
  
  
  zSlices = args.indices

  if zSlices is None:
    zSlices = range(imgData.shape[2])

    
  print parser.prog, ':'
  print '        input file    : {:s}'.format(inputFilename)
  print '        output prefix : {:s}'.format(outputPrefix)
  print '        Z slices      : ', zSlices


  dims = img.shape
  xdim = dims[0]
  ydim = dims[1]
  zdim = dims[2]

  if any(map(lambda n: n > zdim-1, zSlices)):
    print 'Chosen z-slice(s) out of range'
    exit(1)

  if any(map(lambda n: n < 0, zSlices)):
    print 'Chosen z-slice(s) out of range'
    exit(1)


  sliceShape = [1] * len(imgData.shape)
  sliceShape[0] = imgData.shape[0]
  sliceShape[1] = imgData.shape[1]
  currSlice = numpy.zeros(sliceShape)
  
  aff = img.get_affine()
  offset = numpy.zeros(aff.shape)
  offset[0:3, 3] = aff[0:3, 2]
  
  for i in range(len(zSlices)):
    z = zSlices[i]
    currSlice = numpy.reshape(imgData[:,:,z,...], sliceShape).astype(imgDType)
    
    outImg = nib.Nifti1Image(currSlice, aff + z * offset)
    outputName = outputPrefix + '{:03d}'.format(z) + '.nii.gz'
    outImg.set_data_dtype(imgDType)
    nib.save(outImg, outputName)

###############################################################


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


