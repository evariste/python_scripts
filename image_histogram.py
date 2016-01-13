
import sys
import nibabel as nib
import numpy
import argparse
from matplotlib import pyplot

def main(*args):

  
  helpText = (" Display a histogram of an image. Can specify a threshold and/or \
  the number of bins. If an output file is given, plot is saved rather than displayed.")
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "Input image"
  parser.add_argument("input", type=str, help=helpText)

  helpText = 'Threshold: default = -1.0'
  parser.add_argument("-threshold", type=float, help=helpText, default=-1.0)

  helpText = 'Number of bins: default = 30'
  parser.add_argument("-bins", type=int, help=helpText, default=30)

  helpText = 'Maximum on x-axis'
  parser.add_argument("-xMax", type=int, help=helpText, default=30)
  
  helpText = 'Output: Don\'t show plot, save it to a file with given name.'
  parser.add_argument('-output', type=str, help=helpText, default=None)

  args = parser.parse_args()

  #############################################################

  inputFilename = args.input
  threshold = args.threshold
  nBins = args.bins
  outputName = args.output
  xMax = args.xMax


  img = nib.load(inputFilename)
  imgDType = img.get_data_dtype()

  imgData = img.get_data().astype(imgDType)
  
  pyplot.hist(imgData[imgData > threshold], bins=nBins)
  lims = pyplot.axis()

  if not (xMax == None):
    xmin, oldXMax = pyplot.xlim()
    pyplot.xlim( (xmin, xMax) )

  if outputName == None:
    pyplot.show()
  else:
    pyplot.savefig(outputName)

###############################################################


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


