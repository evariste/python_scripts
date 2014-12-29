

import sys, os

#from subprocess import STDOUT
# for debugging
sys.path.append('/Users/paulaljabar/Python/')
import dicom
import nibabel as nib
import argparse
import numpy as np
#import subprocess
#import glob

scriptDir = '/Users/paulaljabar/work/scripts/python'
irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'


def main(*args):
  
  helpText = "    stuff "
  
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "in: filename.dcm"
  parser.add_argument("inFile", type=str, help=helpText)
  
    
#  helpText = "Optional argument"
#  parser.add_argument("-opt", type=int, nargs='+', help=helpText, metavar='label')

  #############################################################
      
  args = parser.parse_args()
  
  inFileName = args.inFile


  plan = dicom.read_file(inFileName)
  
  print plan



if __name__ == '__main__':
  sys.exit(main(*sys.argv))


