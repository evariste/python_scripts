
import sys
import nibabel as nib
import numpy as np
from scipy.ndimage import convolve
from scipy.ndimage.interpolation import map_coordinates

sys.path.append('/Users/paulaljabar/work/scripts/python')
from geometryUtilsPA import matrix2paramsAffine, params2matrixAffine
from imageUtilsPythonPA import get3DKernelFrom1DKernel
np.set_printoptions(precision=2, suppress=True)


# TODO: The following should be arguments:
 
dataDir = '/Users/paulaljabar/work/sandpit/'
filename = dataDir + '/lr-resamp.nii.gz'
outputPrefix = dataDir + '/bla-'


img = nib.load(filename)
data = img.get_data().squeeze()

# TODO: kernel size could be optional ...
# Make a 3D binomial kernel
k = np.asarray( [1.0, 4.0, 6.0, 4.0, 1.0] )
k3 = get3DKernelFrom1DKernel(k)
k3 = k3 / np.sum(k3.ravel())


# TODO:
# perhaps add to dimensions of data so that we can divide by 2 more easily the required number of times.
# Number of levels including original.
nLevels = 3
pow2 = 2 ** (nLevels - 1)

dimx, dimy, dimz = data.shape

temp = pow2 - np.mod(data.shape, pow2)
temp[temp == pow2] = 0
newShape = temp + data.shape

dataBig = np.zeros(newShape)
dataBig[0:dimx, 0:dimy, 0:dimz] = data
# CURRENTLY IGNORED.



m = img.get_affine()

# Start off the pyramid
pyrData = [data,]
pyrMat = [m,]

# Repeat convolution and downsampling.
for i in range(nLevels - 1):
    currData = convolve(pyrData[-1], k3)
    currData = currData[0::2, 0::2, 0::2]
    
    currMat = pyrMat[-1]
    # tx ty tz rx ry rz sx sy sz sxy syz sxz
    ps = np.asarray(matrix2paramsAffine(currMat, array=True))
    ps[6:9] = 2.0 * ps[6:9]
    currMat = params2matrixAffine(ps)
    
    pyrData.append(currData)
    pyrMat.append(currMat)
    

for i in range(len(pyrMat)):
    imgOut = nib.Nifti1Image(pyrData[i], pyrMat[i])
    fileName = outputPrefix + str(i) + '.nii.gz'
    print fileName
    nib.save(imgOut, fileName)




