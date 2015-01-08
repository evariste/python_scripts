

import sys
# import os
# import subprocess
import nibabel as nib
import numpy

irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'
sys.path.append(irtkDir)

maxLabels = 100


def usage(scriptName):
  print "Usage: "
  print "   python " + scriptName + " [input] [outputPrefix] <outValue>"
  print ""
  print " Generate a different binary image for each label in the"
  print " input image. The value of voxels with the label can be"
  print " set with the optional argument <outValue> (default 1000)."
  exit()


def main(*args):
  if len(args) < 3:
     usage(args[0])

  inputFileName = args[1]
  outputPattern = args[2]
  
  if len(args) > 3:
    outVal = int(args[3])
  else:
    outVal = 1000
  
  
  img = nib.load(inputFileName)
  imgData = img.get_data()

  # Get unique non-zero labels  
  vals = numpy.unique(imgData)
  vals = vals[vals > 0]
  
     
  if len(vals) > maxLabels:
    print 'Number of labels (%u) exceeds maximum (%u). Quitting' % (len(vals), maxLabels)
    return

  for v in vals:
    outName = outputPattern + '-{:02d}.nii.gz'.format(v)
    print '  Writing file ' + outName
    temp = numpy.zeros(imgData.shape, dtype=numpy.int16)
    temp[ imgData == v ] = outVal
    newImg = nib.Nifti1Image(temp, img.get_affine())
    newImg.set_data_dtype('int16')
    nib.save(newImg, outName)

if __name__ == '__main__':
  sys.exit(main(*sys.argv))

