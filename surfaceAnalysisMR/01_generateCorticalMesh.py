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
labelOuterCSF       = 1
labelNonBrain       = 4
labelStemCerebellum = 6
labelDGM            = 7
labelVentricle      = 5
labelWM             = 3

# The end result.
outputMesh = atlasDir + '/atlas-7/cortex-mid-40-weeks.vtk'

# TODO: On error remove temporary files.

import nibabel as nib
import numpy as np
import tempfile
import os
from scipy.ndimage import label as connComp
from scipy.ndimage import convolve

import sys
sys.path.append('/Users/paulaljabar/work/scripts/python')
from generalUtilsPythonPA import runCommand


# Atlas labels
labelImg = nib.load(labelImgName)
labelArray = labelImg.get_data().squeeze()

print 'Finding largest GM component'

# Isolate grey matter
allGM = np.copy(labelArray)
allGM[allGM != labelGM] = 0
allGM[allGM > 0] = 1

gmLC = connComp(allGM)[0]
# Retain largest component
gmLC[gmLC > 1] = 0


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

xDim, yDim, zDim = roiData.shape


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
hemiL[xRange,:,:] = 0

hemiR = roiData.copy()
xRange = np.array(range(xMid,xDim))
hemiR[xRange,:,:] = 0


#############################################################
print 'Generating kerLap for Laplace smoothing'

kerLap = np.zeros((3,3,3)).astype(np.float64)
kerLap[0,1,1] = 1
kerLap[2,1,1] = 1
kerLap[1,0,1] = 1
kerLap[1,2,1] = 1
kerLap[1,1,0] = 1
kerLap[1,1,2] = 1
kerLap = kerLap / 6.0


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
    laplaceData = convolve(laplaceData, kerLap)

    # Replace the boundary values.
    laplaceData[hemiL == 0] = 10000
    laplaceData[hemiL == 1] = 0
    
    diff = np.abs(laplaceData - dataStored).reshape( (-1,1) )
    diff = np.max(diff)
    


tempDir = tempfile.gettempdir()
tempPID = str(os.getpid())

tempFileLaplacianResult = os.path.join(tempDir , 'tmp-lap.nii.gz' )
tempFileHemiLeft = os.path.join(tempDir , 'hemi-left.vtk' )
tempFileHemiRight = os.path.join(tempDir , 'hemi-right.vtk' )
tempFileBothMeshes = os.path.join(tempDir , 'hemi-both.vtk' )

imgOut = nib.Nifti1Image(laplaceData, labelImg.get_affine())
nib.save(imgOut, tempFileLaplacianResult)

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
    
    laplaceData = convolve(laplaceData, kerLap)

    laplaceData[hemiR == 0] = 10000
    laplaceData[hemiR == 1] = 0
    diff = np.abs(laplaceData - dataStored).reshape( (-1,1) )
    diff = np.max(diff)
    
imgOut = nib.Nifti1Image(laplaceData, labelImg.get_affine())
nib.save(imgOut, tempFileLaplacianResult)


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


