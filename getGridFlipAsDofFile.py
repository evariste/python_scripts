

import sys, os
# for debugging
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
import nibabel as nib
import argparse
import numpy
import tempfile
import imageUtilsPythonPA
from numpy import linalg as LA

irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'
sys.path.append(irtkDir)

import subprocess

def main(*args):
  
  helpText = "   help  \
  text \
  goes \
  here."
  
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "Input Image: filename.nii.gz"
  parser.add_argument("inputImage", type=str, help=helpText)

  helpText = "Flip type: [I / J / K]"
  parser.add_argument("flipType", help=helpText, type=str)

  helpText = "Output Image: filename.dof"
  parser.add_argument("outputDof", help=helpText, type=str)
    
#  helpText = "Optional argument"
#  parser.add_argument("-opt", type=int, nargs='+', help=helpText, metavar='label')

  #############################################################
      
  args = parser.parse_args()
  
  
  imgIn = nib.load(args.inputImage)
  
  flipType = args.flipType.upper()

  i2w = imgIn.get_affine()

  w2i = LA.inv(i2w)
  
  print i2w
    
  I,J,K,T = imgIn.get_shape()
  

  flipMat = numpy.eye(4)
  
  opts = {'I': 0, 'J': 1, 'K': 2}
  dims = {'I': I, 'J': J, 'K': K}
  
  try:
    n = opts[flipType]
    d = dims[flipType]
    flipMat[n,n] = -1
    flipMat[n,3] = d - 1
  except KeyError:
    print "No such flip type ", flipType
    sys.exit(1)

  # The main bit: output dof has matrix = i2w * flipMat * w2i
  outMat = numpy.dot(flipMat, w2i)
  outMat = numpy.dot(i2w, outMat)

  
  tempMatFile = os.path.join( tempfile.gettempdir() , 'tmp-' + str(os.getpid()) + '.mat' )
  imageUtilsPythonPA.writeIRTKMatrix(tempMatFile, outMat)
  
  
  mat2dofExe = os.path.join(irtkDir, 'mat2dof')
   
  cmd = [mat2dofExe, tempMatFile, args.outputDof]
  output = subprocess.check_output(cmd)
  
  print 'Matrix and transformation parameters:'
  print
  print output
  print
  
  os.remove(tempMatFile)
  
  
if __name__ == '__main__':
  sys.exit(main(*sys.argv))


