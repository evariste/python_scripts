
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
  parser.add_argument("-xMax", type=float, help=helpText, default=None)

  helpText = 'Minimum on x-axis'
  parser.add_argument("-xMin", type=float, help=helpText, default=None)

  helpText = 'Maximum on y-axis'
  parser.add_argument("-yMax", type=float, help=helpText, default=None)

  helpText = 'Minimum on y-axis'
  parser.add_argument("-yMin", type=float, help=helpText, default=None)


  helpText = 'Output: Don\'t show plot, save it to a file with given name.'
  parser.add_argument('-output', type=str, help=helpText, default=None)

  args = parser.parse_args()

  #############################################################

  inputFilename = args.input
  threshold = args.threshold
  nBins = args.bins
  outputName = args.output
  xMax = args.xMax
  xMin = args.xMin
  yMax = args.yMax
  yMin = args.yMin


  img = nib.load(inputFilename)
  imgDType = img.get_data_dtype()

  imgData = img.get_data().astype(imgDType)
  
  pyplot.hist(imgData[imgData > threshold], bins=nBins)
  lims = pyplot.axis()

  if not (xMax == None):
    print 'setting max x value to ', xMax
    temp, _ = pyplot.xlim()
    pyplot.xlim( (temp, xMax) )

  if not (xMin == None):
    print 'setting min x value to ', xMin
    _, temp = pyplot.xlim()
    pyplot.xlim( (xMin, temp) )

  if not (yMax == None):
    print 'setting max y value to ', yMax
    temp, _ = pyplot.ylim()
    pyplot.ylim( (temp, yMax) )

  if not (yMin == None):
    print 'setting min x value to ', yMin
    _, temp = pyplot.ylim()
    pyplot.ylim( (yMin, temp) )

  if outputName == None:
    pyplot.show()
  else:
    pyplot.savefig(outputName)

###############################################################


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


