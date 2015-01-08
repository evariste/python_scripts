

import sys, os
# for debugging
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
import nibabel as nib
from numpy import linalg as LA
import argparse

import numpy
import tempfile

import imageUtilsPythonPA

irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'
sys.path.append(irtkDir)

import subprocess

def main(*args):
  
  helpText = "   Get an affine transformation between two images based on their \
  header information. The resulting transformation will define correspondence \
  between voxels with the same image coordinates (indices) in each image. This \
  can be useful if two images same grid but different orientations, for example."
  
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "Target Image: filename.nii.gz"
  parser.add_argument("targetImage", type=str, help=helpText)

  helpText = "Source Image: filename.nii.gz"
  parser.add_argument("sourceImage", help=helpText, type=str)
  
  helpText = "Transformation: name.dof"
  parser.add_argument("dofout", help=helpText, type=str)
  
#  helpText = "Optional argument"
#  parser.add_argument("-opt", type=int, nargs='+', help=helpText, metavar='label')

  #############################################################
      
  args = parser.parse_args()
  
  
  imgTgt = nib.load(args.targetImage)
  imgSrc = nib.load(args.sourceImage)

  i2w_Tgt = imgTgt.get_affine()
  i2w_Src = imgSrc.get_affine()
  
  w2i_Tgt = LA.inv(i2w_Tgt)
  
  matTgt2Src = numpy.dot(i2w_Src, w2i_Tgt)

  tempMatFile = os.path.join( tempfile.gettempdir() , 'tmp-' + str(os.getpid()) + '.mat' )

  imageUtilsPythonPA.writeIRTKMatrix(tempMatFile, matTgt2Src)
  
  mat2dofExe = os.path.join(irtkDir, 'mat2dof')
   
  cmd = [mat2dofExe, tempMatFile, args.dofout]
  output = subprocess.check_output(cmd)
  
  print 'Matrix and transformation parameters:'
  print
  print output
  print
  
  os.remove(tempMatFile)
  
if __name__ == '__main__':
  sys.exit(main(*sys.argv))


