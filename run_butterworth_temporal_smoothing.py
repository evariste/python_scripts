import os, sys
import nibabel as nib
import numpy as np
import argparse
from scipy.signal import buttord, butter, lfilter





def main():

  helpText = """ Run a butterworth filter along temporal dimension on 
  fMRI time series data """
  parser = argparse.ArgumentParser(description=helpText)
  
  helpText = "Input image to be smoothed."
  parser.add_argument("input", type=str, help=helpText)

  helpText = "Output image"
  parser.add_argument("output", help=helpText, type=str)
  
  helpText = "Frequency cut-off (Hz)"
  parser.add_argument("-f", type=float, help=helpText, metavar='frequency')

  args = parser.parse_args()

  inputName = args.input
  outputName = args.output

  fmriImg = nib.load(inputName)
  fmriData = fmriImg.get_data()
  nVols = fmriData.shape[3]
  hdr = fmriImg.get_header()

  freqCutoff = args.f
  if freqCutoff is None:
    freqCutoff = 0.1 # Hz.



  if nVols < 2:
    print 'Input image is not 4-dimensional. Exiting'
    sys.exit(1)


  outData = np.zeros(fmriData.shape)


  tr = hdr['pixdim'][4] # Repetition time.
  fs = 1.0/tr      # Sampling frequency.
  half_fs = fs/2.0 # Nyquist frequency.

  # Freq cut off for digital data.
  loFreq = freqCutoff / half_fs
  cornerFreq = 1.5 * loFreq

  # What order filter required for the required cut-off behaviour?
  filterOrder, wn = buttord(wp=loFreq, ws=cornerFreq, gpass=0.1, gstop=3)

  # Coefficients of filter in the form of polynomials in a rational expression in the Laplace domain.
  b, a = butter(filterOrder, wn, btype='low')
  

  pad = 2*filterOrder

  for k in range(fmriData.shape[2]):
    for j in range(fmriData.shape[1]):
      for i in range(fmriData.shape[0]):
        temp = lfilter(b, a, fmriData[i,j,k,:])
        
        outData[i,j,k,:-filterOrder] = temp[filterOrder:]

  outData[:,:,:,:filterOrder] = 0

  imgDType = fmriImg.get_data_dtype()
  aff = fmriImg.get_affine()

  outImg = nib.Nifti1Image(outData, aff)
  outImg.set_data_dtype(imgDType)
  nib.save(outImg, outputName)



if __name__ == '__main__':
  sys.exit(main())


