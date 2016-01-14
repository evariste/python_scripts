import sys
import nibabel as nib
import numpy
import argparse


from matplotlib import pyplot as plt




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

  N = 200

  ps = numpy.linspace(0, 100, N+1)

  srcPts = numpy.percentile(srcImgData, ps)
  refPts = numpy.percentile(refImgData, ps)

  if (srcPts[-1] < srcMaxGlobal) or (refPts[-1] < refMaxGlobal):
    srcPts = numpy.append(srcPts, srcMaxGlobal)
    refPts = numpy.append(refPts, refMaxGlobal)

  if (srcPts[0] > srcMinGlobal) or (refPts[0] > refMinGlobal):
    srcPts = numpy.insert(srcPts, 0, srcMinGlobal)
    refPts = numpy.insert(refPts, 0, refMinGlobal)


  # Can have multiple repeated values at low end (most voxels are zero).
  # Make the values ramp up linearly to the first non-minimim (0) intensity.
  i = 0
  while srcPts[i] == srcMinGlobal:
    i += 1

  if i > 1:
    for j in range(1, i):
      srcPts[j] = j * srcPts[i] / i

  i = 0
  while refPts[i] == refMinGlobal:
    i += 1

  if i > 1:
    for j in range(1, i):
      refPts[j] = j * refPts[i] / i



  outShape = outImgData.shape

  v = numpy.ravel(outImgData)

  outImgData = numpy.interp(v, srcPts, refPts)

  outImgData = numpy.reshape(outImgData, outShape)

  aff = srcImg.get_affine()
  outImg = nib.Nifti1Image(outImgData, aff)
  nib.save(outImg, outImgName)


###############################################################


if __name__ == '__main__':
  sys.exit(main(*sys.argv))


