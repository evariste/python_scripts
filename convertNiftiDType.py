
import sys

sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')
import nibabel as nib

import numpy

# TODO : FINISH OFF currently only converts to uint8

def usage():
  print "Usage: "
  exit()


def main(*args):
  if len(args) < 3:
     usage()

  inputFileName = args[1]
  outputFileName = args[2]
  
  requiredDtype = numpy.uint8
  
  img = nib.load(inputFileName)
  imgData = img.get_data().astype(requiredDtype)
  
      
  newImg = nib.Nifti1Image(imgData, img.get_affine())
  newImg.set_qform(img.get_affine())
  newImg.set_data_dtype(requiredDtype)
  nib.save(newImg, outputFileName)




if __name__ == '__main__':
  sys.exit(main(*sys.argv))
