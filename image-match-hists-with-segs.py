import sys
import nibabel as nib
import numpy
import argparse


def main(*args):


  helpText = "   Match the histogram of an image to the histogram of a reference image using information " \
             "from their segmentations."
  parser = argparse.ArgumentParser(description=helpText)

  helpText = "Reference image"
  parser.add_argument("ref", type=str, help=helpText)

  helpText = "Source image"
  parser.add_argument("src", type=str, help=helpText)

  helpText = "Reference segmentation"
  parser.add_argument("refSeg", type=str, help=helpText)

  helpText = "Source segmentation"
  parser.add_argument("srcSeg", type=str, help=helpText)

  helpText = "Output image"
  parser.add_argument("output", type=str, help=helpText)

  helpText = "ventricle label (default 5)"
  parser.add_argument("-ventLabel", type=int, help=helpText)

  helpText = "GM label (default 3)"
  parser.add_argument("-gmLabel", type=int, help=helpText)

  helpText = "WM label (default 2)"
  parser.add_argument("-wmLabel", type=int, help=helpText)

  helpText = "CSF label (default 1)"
  parser.add_argument("-csfLabel", type=int, help=helpText)


  #############################################################

  args = parser.parse_args()

  refImgName = args.ref
  srcImgName = args.src

  refSegName = args.refSeg
  srcSegName = args.srcSeg

  outImgName = args.output

  ventLabel = args.ventLabel
  gmLabel = args.gmLabel
  wmLabel = args.wmLabel
  csfLabel = args.csfLabel

  if ventLabel == None:
    ventLabel = 5
  if gmLabel == None:
    gmLabel = 3
  if wmLabel == None:
    wmLabel = 2
  if csfLabel == None:
    csfLabel = 1


  refImg = nib.load(refImgName)
  srcImg = nib.load(srcImgName)


  refImgData = refImg.get_data().squeeze()
  srcImgData = srcImg.get_data().squeeze()

  srcMin = numpy.min(srcImgData)
  srcMax = numpy.max(srcImgData)


  refMin = numpy.min(refImgData)
  refMax = numpy.max(refImgData)

  outImgData = srcImgData.copy()



  refSegImg = nib.load(refSegName)
  refSeg = refSegImg.get_data().squeeze()
  if not (refSeg.shape == refImgData.shape):
    raise Exception('Reference and its segmentation have different shapes')


  srcSegImg = nib.load(srcSegName)
  srcSeg = srcSegImg.get_data().squeeze()
  if not (srcSeg.shape == srcImgData.shape):
    raise Exception('Source image and its segmentation have different shapes')


  srcPts = [srcMin, srcMax]
  refPts = [refMin, refMax]

  # low and high percentiles
  vs = numpy.percentile(srcImgData, [1,99])
  srcPts = srcPts + list(vs)
  vs = numpy.percentile(refImgData, [1,99])
  refPts = refPts + list(vs)

  # CSF
  vs = srcImgData[ numpy.logical_or(srcSeg == csfLabel, srcSeg == ventLabel)]
  srcPts.append(numpy.mean(vs))
  vs = refImgData[numpy.logical_or(refSeg == csfLabel, refSeg == ventLabel)]
  refPts.append(numpy.mean(vs))

  # GM
  vs = srcImgData[srcSeg == gmLabel]
  srcPts.append(numpy.mean(vs))
  vs = refImgData[refSeg == gmLabel]
  refPts.append(numpy.mean(vs))

  # WM
  vs = srcImgData[srcSeg == wmLabel]
  srcPts.append(numpy.mean(vs))
  vs = refImgData[refSeg == wmLabel]
  refPts.append(numpy.mean(vs))


  ix = numpy.argsort(srcPts)
  srcPts = numpy.asarray(srcPts)[ix]
  refPts = numpy.asarray(refPts)[ix]


  x = numpy.ravel(srcImgData)

  y = numpy.interp(x, srcPts, refPts)

  y = numpy.reshape(y, srcImgData.shape)

  aff = srcImg.get_affine()
  outImg = nib.Nifti1Image(y, aff)
  nib.save(outImg, outImgName)


###############################################################


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


