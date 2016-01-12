

import os
import sys
import nibabel as nib
import numpy
import argparse


def main(*args):


  helpText = "   Match the histogram of an image to the histogram of a reference image."
  parser = argparse.ArgumentParser(description=helpText)

  helpText = "Reference image"
  parser.add_argument("ref", type=str, help=helpText)

  helpText = "Source image"
  parser.add_argument("src", type=str, help=helpText)

  helpText = "Output image"
  parser.add_argument("output", type=str, help=helpText)

  helpText = "Reference mask"
  parser.add_argument("-refMask", type=str, help=helpText)

  helpText = "Source mask"
  parser.add_argument("-srcMask", type=str, help=helpText)



  #############################################################

  args = parser.parse_args()

  refImgName = args.ref
  srcImgName = args.src
  outImgName = args.output

  refMaskName = args.refMask
  srcMaskName = args.srcMask


  refImg = nib.load(refImgName)
  srcImg = nib.load(srcImgName)


  refImgData = refImg.get_data().squeeze()
  srcImgData = srcImg.get_data().squeeze()


  srcMinGlobal = numpy.min(srcImgData)
  srcMaxGlobal = numpy.max(srcImgData)


  refMinGlobal = numpy.min(refImgData)
  refMaxGlobal = numpy.max(refImgData)


  outImgData = srcImgData.copy()


  if not refMaskName == None:
    refMaskImg = nib.load(refMaskName)
    refMask = refMaskImg.get_data().squeeze()
    if not (refMask.shape == refImgData.shape):
      raise Exception('Reference and its mask different shapes')
    refImgData = refImgData[refMask > 0]

  if not srcMaskName == None:
    srcMaskImg = nib.load(srcMaskName)
    srcMask = srcMaskImg.get_data().squeeze()
    if not (srcMask.shape == srcImgData.shape):
      raise Exception('Source image and its mask different shapes')
    srcImgData = srcImgData[srcMask > 0]


  nBins = 100

  srcHist, srcBinEdges = numpy.histogram(srcImgData,bins=nBins)
  srcCumFreq = numpy.cumsum(srcHist)
  nSrcVoxels = srcCumFreq[-1]
  srcBinCentiles = 100.0 * srcCumFreq / nSrcVoxels

  refHist, refBinEdges = numpy.histogram(refImgData, bins=nBins)
  refCumFreq = numpy.cumsum(refHist)
  nRefVoxels = refCumFreq[-1]
  refBinCentiles = 100.0 * refCumFreq / nRefVoxels

  # Make the centiles match the bin edges in size
  srcBinCentiles = numpy.hstack((0, srcBinCentiles))
  refBinCentiles = numpy.hstack((0, refBinCentiles))

  srcMinMasked = srcBinEdges[0]
  srcMaxMasked = srcBinEdges[-1]
  refMinMasked = refBinEdges[0]
  refMaxMasked = refBinEdges[-1]



  outShape = outImgData.shape

  outImgData = numpy.ravel(outImgData)

  nOutVoxels = len(outImgData)

  srcBinWidth = srcBinEdges[1]
  refBinWidth = refBinEdges[1]

  for n in range(nOutVoxels):
    v = outImgData[n]

    if v < srcMinMasked:
      vOut = refMinGlobal + (refMinMasked - refMinGlobal) * (v - srcMinGlobal) / (srcMinMasked - srcMinGlobal)
      outImgData[n] = vOut
      continue

    if v > srcMaxMasked:
      vOut = refMaxMasked + (refMaxGlobal - refMaxMasked) * (v - srcMaxMasked) / (srcMaxGlobal - srcMaxMasked)
      outImgData[n] = vOut
      continue

    i = int(v/srcBinWidth)

    i = min(i,nBins-2)

    pctile = srcBinCentiles[i] + (srcBinCentiles[i+1] - srcBinCentiles[i]) * (v - i * srcBinWidth) / srcBinWidth

    i = 0
    while (i < nBins) and (refBinCentiles[i] <= pctile):
      i = i + 1

    i = min(i, nBins-1)

    vOut = (i-1) * refBinWidth + refBinWidth * (pctile - refBinCentiles[i-1]) / (refBinCentiles[i] - refBinCentiles[i-1])

    outImgData[n] = vOut


  # Restore shape and save.
  outImgData = numpy.reshape(outImgData, outShape)

  aff = srcImg.get_affine()
  outImg = nib.Nifti1Image(outImgData, aff)
  nib.save(outImg, outImgName)


###############################################################


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


