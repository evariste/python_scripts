# Script to generate a mesh at the middle cortical surface layer in the 40 week
# template.
# 
# Runs in a virtual python environment. Run command
# 
# source /Users/paulaljabar/work/scripts/python/pythonEnvs/surfaceAnalysis/bin/activate
# 
# before invoking this script


workingDir = '/Users/paulaljabar/work/sandpit'
irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'

# Where are the atlas data?
atlasDir = '/Users/paulaljabar/work/atlases/neo-nr-T1-T2-segs'

# Which atlas labels to use?
labelImgName = atlasDir + '/atlas-7/40.nii.gz'
labelGM = 2
labelOuterCSF = 1
labelNonBrain = 4
labelStemCerebellum = 6

# The end result.
outputMesh = atlasDir + '/atlas-7/cortex-mid-40-weeks.vtk'

# TODO: On error remove temporary files.

import nibabel as nib
import SimpleITK as sitk
import numpy as np
import tempfile
import os

import sys
sys.path.append('/Users/paulaljabar/work/scripts/python')
from generalUtilsPythonPA import runCommand


# Atlas labels
labelImg = sitk.ReadImage(labelImgName)
labelArray = sitk.GetArrayFromImage(labelImg)

print 'Finding largest GM component'

# Isolate grey matter
allGM = np.copy(labelArray)
allGM[allGM != labelGM] = 0
allGM[allGM > 0] = 1

# Find all components.
ccFilt = sitk.ConnectedComponentImageFilter()
img = sitk.GetImageFromArray(allGM)
gmLC = sitk.GetArrayFromImage(ccFilt.Execute(img))

# Isolate largest connected component.
gmLC[gmLC != 1] = 0

#############################################
print 'Getting two label map'

roiData = np.copy(labelArray)

# Get rid of what we are not interested in: outer csf, non-brain and
# cerebellum+stem
roiData[roiData == labelOuterCSF] = 0
roiData[roiData == labelNonBrain] = 0
roiData[roiData == labelStemCerebellum] = 0
roiData[roiData > 0] = 1

# Get a two label map contiaining the GM-lc and everything else we are
# interested in.
roiData[gmLC > 0] = 2

zDim, yDim, xDim = roiData.shape

#img = sitk.GetImageFromArray(roiData)
#img.CopyInformation(labelImg)
# tempFile0 = os.path.join(tempDir , 'tmp0.nii.gz' )
#sitk.WriteImage(img, tempFile0)
#del img

#############################################
print 'Estimating mid-line'

# Estimate mid-line by counting mass of voxels in a range of x-slices near the
# centre. We assume the the mid-line plane is already reasonably well
# approximated by the x = xDim/2, so search nearby.
xStart = xDim/2 - 5
xEnd   = xDim/2 + 5 + 1
xInds = range(xStart,xEnd)
voxelCount = np.zeros( (len(xInds),) )

for i in range(len(xInds)):
    v = roiData[:,:,xInds[i]]
    v = v.reshape( (-1,1) )
    voxelCount[i] = np.sum(v)

# Which plane has the smallest total? Assume this is the mid-line.
xMid = xInds[ np.argmin(voxelCount) ]

#############################################
print ' Splitting label data into left and right hemispheres'

hemiL = roiData.copy()
xRange = np.array(range(xMid))
hemiL[:,:,xRange] = 0

#imgHemiL = sitk.GetImageFromArray(hemiL)
#imgHemiL.CopyInformation(labelImg)
# tempFile1 = os.path.join(tempDir , 'tmp1.nii.gz' )
# sitk.WriteImage(imgHemiL, tempFile1)

hemiR = roiData.copy()
xRange = np.array(range(xMid,xDim))
hemiR[:,:,xRange] = 0

#imgHemiR = sitk.GetImageFromArray(hemiR)
#imgHemiR.CopyInformation(labelImg)
# tempFile2 = os.path.join(tempDir , 'tmp2.nii.gz' )
# sitk.WriteImage(imgHemiR, tempFile2)

#############################################################
print 'Generating kernel for Laplace smoothing'

kernel = np.zeros((3,3,3)).astype(np.float64)
kernel[0,1,1] = 1
kernel[2,1,1] = 1
kernel[1,0,1] = 1
kernel[1,2,1] = 1
kernel[1,1,0] = 1
kernel[1,1,2] = 1
kernel = kernel / 6.0

imgKernel = sitk.GetImageFromArray(kernel)

#############################################################

print 'Running Laplace solver to get 50% contour of GM'

print 'Left ...',

# Now run laplace eqn solver on wm + interior + gm bits as the inside and 
# csf/outer gm as the outside

# image with boundary and initial conditions
laplaceData = hemiL.copy().astype(np.float64)

laplaceData[hemiL == 0] = 10000
laplaceData[hemiL == 1] = 0
# Intermediate value in GM
laplaceData[hemiL == 2] = 5000

maxReps = 100
epsilon = 50
diff = epsilon + 1
i = 0
while i < maxReps and diff > epsilon:
# for i in range(maxReps):
    i = i + 1
    dataStored = laplaceData.copy()
    # Run the filter.
    imgIn = sitk.GetImageFromArray(laplaceData)
    lapSmoothingFilt = sitk.ConvolutionImageFilter()
    imgOut = lapSmoothingFilt.Execute(imgIn, imgKernel)
    laplaceData = sitk.GetArrayFromImage(imgOut)
    # Replace the boundary values.
    laplaceData[hemiL == 0] = 10000
    laplaceData[hemiL == 1] = 0
    
    diff = np.abs(laplaceData - dataStored).reshape( (-1,1) )
    diff = np.max(diff)
    
imgOut.CopyInformation(labelImg)



tempDir = tempfile.gettempdir()
tempPID = str(os.getpid())

tempFileLaplacianResult = os.path.join(tempDir , 'tmp-lap.nii.gz' )
tempFileHemiLeft = os.path.join(tempDir , 'hemi-left.vtk' )
tempFileHemiRight = os.path.join(tempDir , 'hemi-right.vtk' )
tempFileBothMeshes = os.path.join(tempDir , 'hemi-both.vtk' )

sitk.WriteImage(imgOut, tempFileLaplacianResult)

# Extract surface 
cmd = (irtkDir + '/mcubes'
       + ' ' + tempFileLaplacianResult
       + ' ' + tempFileHemiLeft
       + ' ' + '5000')
_,_ = runCommand(cmd, quiet=True)

cmd = (irtkDir + '/polydatalcc' 
       + ' ' + tempFileHemiLeft 
       + ' ' + tempFileHemiLeft)
_,_ = runCommand(cmd, quiet=True)


cmd = (irtkDir + '/polydatadecimate' 
       + ' ' + tempFileHemiLeft 
       + ' ' + tempFileHemiLeft 
       + ' ' + '-preserveTopology -target 20000')
_,_ = runCommand(cmd, quiet=True)

cmd = (irtkDir + '/polydatarecalculatenormals' 
       + ' ' + tempFileHemiLeft 
       + ' ' + tempFileHemiLeft 
       + ' ' + '-auto')
_,_ = runCommand(cmd, quiet=True)

print 'done'


print 'Right ...',

# image with boundary and initial conditions
laplaceData = hemiR.copy().astype(np.float64)

laplaceData[hemiR == 0] = 10000
laplaceData[hemiR == 1] = 0
# Intermediate value in GM
laplaceData[hemiR == 2] = 5000

maxReps = 100
epsilon = 50
diff = epsilon + 1
i = 0
while i < maxReps and diff > epsilon:
# for i in range(maxReps):
    i = i + 1
    dataStored = laplaceData.copy()
    imgIn = sitk.GetImageFromArray(laplaceData)
    lapSmoothingFilt = sitk.ConvolutionImageFilter()
    imgOut = lapSmoothingFilt.Execute(imgIn, imgKernel)
    laplaceData = sitk.GetArrayFromImage(imgOut)
    laplaceData[hemiR == 0] = 10000
    laplaceData[hemiR == 1] = 0
    diff = np.abs(laplaceData - dataStored).reshape( (-1,1) )
    diff = np.max(diff)
    
imgOut.CopyInformation(labelImg)
sitk.WriteImage(imgOut, tempFileLaplacianResult)


# In[18]:

# Extract surface 
cmd = (irtkDir + '/mcubes' 
       + ' ' + tempFileLaplacianResult 
       + ' ' + tempFileHemiRight 
       + ' ' + '5000')
_,_ = runCommand(cmd, quiet=True)

cmd = (irtkDir + '/polydatalcc' 
       + ' ' + tempFileHemiRight 
       + ' ' + tempFileHemiRight)
_,_ = runCommand(cmd, quiet=True)

cmd = (irtkDir + '/polydatadecimate' 
       + ' ' + tempFileHemiRight 
       + ' ' + tempFileHemiRight 
       + ' ' + '-preserveTopology -target 20000')
_,_ = runCommand(cmd, quiet=True)

cmd = (irtkDir + '/polydatarecalculatenormals' 
       + ' ' + tempFileHemiRight 
       + ' ' + tempFileHemiRight 
       + ' ' + '-auto')
_,_ = runCommand(cmd, quiet=True)

print 'done'


##############################################

print 'Appending both hemisphere meshes into the single mesh ', outputMesh

cmd = (irtkDir + '/polydataappend' 
       + ' 2 ' + tempFileHemiRight
       + ' ' + tempFileHemiLeft
       + ' ' + tempFileBothMeshes)
_,_ = runCommand(cmd, quiet=True)


cmd = ('cp'
       + ' ' + workingDir + '/cortex-mid-40-weeks.vtk'
       + ' ' + outputMesh)
_,_ = runCommand(cmd, quiet=True)

##########################################################
print 'Remove temporary files.'
fileList = [tempFileLaplacianResult,  tempFileHemiLeft, tempFileHemiRight, tempFileBothMeshes]
for f in fileList:
  os.remove(f)


