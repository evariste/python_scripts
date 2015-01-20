
import sys
import nibabel as nib
import numpy as np
from scipy.ndimage import gaussian_filter

np.set_printoptions(precision=2, suppress=True)

"""
run gaussian smoothing
"""

# TODO: Make the following into arguments.
dataDir = '/Users/paulaljabar/work/sandpit/'
filename = dataDir + '/lr-resamp.nii.gz'

blurredImageName = dataDir + '/blur.nii.gz'

# Isotropic smoothing in mm (world) coordinates
sigma = 2.0




# Start work:

img = nib.load(filename)
data = img.get_data().squeeze()


m = img.get_affine()
hdr = img.get_header()
pixdims = hdr['pixdim'][1:4]


# TODO: allow anisotropic blurring.
sigma = np.ones((3,)) * sigma
# Convert sigma to image coordinates
sigma = sigma / pixdims

sigma = sigma[:, None]

blurredData = gaussian_filter(data, sigma)

img2 = nib.Nifti1Image(blurredData, m)
nib.save(img2, blurredImageName)





