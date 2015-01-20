
# coding: utf-8

# Runs in a virtual python environment. Run command
# 
# source /Users/paulaljabar/work/scripts/python/pythonEnvs/surfaceAnalysis/bin/activate
# 
# before invoking this script
# 
# This script uses a mesh in the subject's fMRI space (see fmri-surface-analysis-2).
# 
# It assigns a time series to each vertex in the mesh based on a local
# average of the time series for the fMRI voxels in the neighbourhood (weighted
# by a distance decreasing gaussian).
# 
# The array representing the mesh vertices' time series is then saved to a
# 4D Nifti file for use in FEAT/MELODIC - the final commands to do this 
# are to be done using system calls.
# 
# The 4D nifti file should contain more voxels than the number of mesh vertices. The time series 
# for the vertices are just copied 'in order' into the voxels of the image, i.e. the first voxel gets
# the time series for the first vertex mesh (in memory order) and so on.
# 

# In[1]:

import nibabel as nib
import SimpleITK as sitk
import math
import numpy as np
import sys
sys.path.append('/Users/paulaljabar/work/scripts/python')
from generalUtilsPythonPA import runCommand
import geometryUtilsPA

import vtk


# In[2]:

dataDir = '/Users/paulaljabar/work/cdb/e-prime/from-peridata/EPRIME'
scanID = 'EP5046'

workingDir = '/Users/paulaljabar/work/sandpit'

scanDir = dataDir + '/' + scanID 

scanT2Dir  = scanDir + '/003_volumetric_data'
scanSegDir = scanT2Dir + '/segmentations'
scanFuncDir = scanDir + '/002_functional_data' 
scanICADir = (scanFuncDir + '/' + scanID + '_rs_fMRI.ica')

tissueSegImg = scanSegDir + '/' + scanID + '_tissue_labels.nii.gz'

atlasDir = '/Users/paulaljabar/work/atlases/neo-nr-T1-T2-segs'

irtkDir = '/Users/paulaljabar/work/packages/irtk/build/bin'

funcDataFile = scanFuncDir + '/EP5046_clean_rs_fMRI.nii.gz'

# mapping mesh to individual fmri data
dofFunc2HiRes = workingDir + '/func2highres.dof'
inputMeshFile = workingDir + '/temp-func.vtk'

outputImageFile = workingDir + '/mesh-series-data-as-image-0.75.nii.gz'

# In[3]:

# Mapping atlas mesh to individual T2 image

atlasMesh = atlasDir + '/atlas-7/cortex-mid-40-weeks.vtk'
t2Mesh = workingDir + '/temp.vtk'
dofFileT2toTemplate = scanDir + '/003_volumetric_data/'
dofFileT2toTemplate = dofFileT2toTemplate +  scanID + '_T2_to_template.dof'
cerebrumShrinkT2 = workingDir + '/cerebrum-temp.nii.gz'
resizeDof = workingDir + '/resize-temp.dof'


# In[4]:

# Load the functional data from 4D nifti file.
funcImg = nib.load(funcDataFile)
funcData = funcImg.get_data()


# In[5]:

# Storage for world coordinates of functional data voxels
funcI2W = funcImg.get_affine()

dimI, dimJ, dimK, dimT = funcData.shape

# The ranges for the voxel coordinates
i = np.arange(dimI)
j = np.arange(dimJ)
k = np.arange(dimK)

# View them as 3D arrays with singleton dimensions.
ii = i[:, None, None]
jj = j[None, :, None]
kk = k[None, None, :]

# Get a full set of voxel indices with the same shape 
# as the 3D field of view (equivalent to MatLab meshgrid function)
iii,jjj,kkk = np.broadcast_arrays(ii,jj,kk)

# View as 4D arrays with a singleton dimension and add an
# array of ones so we can treat as homogeneous coordinates.
iii = iii[:,:,:,None]
jjj = jjj[:,:,:,None]
kkk = kkk[:,:,:,None]
lll = np.ones(kkk.shape)

# Stack into a single 4D array, each slice along the last 
# axis contains the voxel coordinates for a particular voxel.
temp = np.concatenate((iii,jjj,kkk,lll), axis=3)

# Hit on the right with the transposed I2W matrix to generate
# the world coordinates for all voxels in a single 4D array.
worldCoords = np.dot(temp, funcI2W.T)

# worldCoords[indexI,indexJ,indexK,0:3] gives conversion from image indices to world coords


# In[6]:

# Mask for functional data at 1% of absolute total across time series.
mask = np.sum(np.fabs(funcData), axis=3)
posData = mask[mask > 0]
thresh = np.percentile(posData, 1)
mask[mask < thresh] = 0
mask[mask > 0] = 1

# tempImg = nib.Nifti1Image(mask, funcI2W)
# nib.save(tempImg, workingDir + '/bla.nii.gz')


# In[7]:

# Read the mesh in the subject's fMRI space (and build a locator object for use later.)
pd_reader = vtk.vtkPolyDataReader()
pd_reader.SetFileName(inputMeshFile)
pd_reader.Update()
pdFuncMesh = pd_reader.GetOutput()

kdTree = vtk.vtkKdTreePointLocator()
kdTree.SetDataSet(pdFuncMesh)
kdTree.BuildLocator()
kdTree.Update()


# In[8]:

# Exclude all voxels more than a specified distance threshold from the mesh.

distThresh = 6 # mm

# Work with mask in a linear form
m = mask.ravel()
inds = np.where(m > 0)[0]
print inds.size, ' mask voxels'

count = inds.size

idList = vtk.vtkIdList()

for c in range(count):
    ind = inds[c]
    indI, indJ, indK = np.unravel_index(ind, mask.shape)
    maskPt = tuple(worldCoords[indI, indJ, indK, :][0:3])
    kdTree.FindPointsWithinRadius(distThresh, maskPt, idList)
    if idList.GetNumberOfIds() < 1:
        mask[indI, indJ, indK] = 0

# Update linear indices of positive mask voxels
m = mask.ravel()
inds = np.where(m > 0)[0]
print inds.size, ' mask voxels'


# In[9]:

# Now loop over each of the remaining voxels (i.e. those within the distance threshold)
# Find the mesh vertices that they canncontribute to and 'contribute' the voxel's (weighted) 
# time series to each vertex.

count = inds.size
print 'looping over ', count , ' mask voxels'

nMeshPts = pdFuncMesh.GetNumberOfPoints()
nTimePts = funcData.shape[3]

weightTotals = np.zeros((nMeshPts,))
sigma=0.75
sigma2 = sigma * sigma

seriesData = np.zeros( (nMeshPts, nTimePts) ) 

for c in range(count):
    ind = inds[c]
    indI, indJ, indK = np.unravel_index(ind, mask.shape)
    
    maskPt = worldCoords[indI, indJ, indK, :][0:3]
    tSeries = funcData[indI, indJ, indK, :]

    kdTree.FindPointsWithinRadius(distThresh, tuple(maskPt), idList)
    
    for cc in range(idList.GetNumberOfIds()):
        meshInd = idList.GetId(cc)
        meshPt = np.asarray(pdFuncMesh.GetPoint(meshInd))
        d = meshPt - maskPt
        w = math.exp(-1.0 * np.dot(d,d) / sigma2)
        weightTotals[meshInd] = weightTotals[meshInd] + w
        seriesData[meshInd, :] = seriesData[meshInd, :] + w * tSeries
        
# Normalise the weights to one.
for meshInd in range(nMeshPts):
    seriesData[meshInd, :] = seriesData[meshInd, :] / weightTotals[meshInd]
    


# In[10]:

# Store the image data in a 4D nifiti file that we can run FEAT/MELODIC on

# TODO: Size of output image as an optional argument.
N = 50
data = np.zeros((N,N,N, nTimePts))

nSpatialVoxels = N*N*N

if nMeshPts > nSpatialVoxels:
  raise Exception('More mesh points than voxels available in output image. Exiting')

for c in range(nMeshPts):
    indI, indJ, indK = np.unravel_index(c, (N,N,N))
    data[indI, indJ, indK, :] = seriesData[c, :]
    
imageStorage = nib.Nifti1Image(data, np.eye(4))

imageStorageName = outputImageFile
nib.save(imageStorage, imageStorageName)



# Next run in a terminal:

cmd1 = 'cd /Users/paulaljabar/work/cdb/melodic-scripts'

icaDir = '/Users/paulaljabar/work/sandpit/icaOutput'
cmd2 = ('python generate_melodic_design_file_single_subject.py' +
        ' ' + imageStorageName + 
        ' ' + icaDir)
# Redirect output of last command to the design file, e.g.

designFileName = workingDir + '/melodic-design-single.fsf'

featScript = '/Users/paulaljabar/work/cdb/melodic-scripts/run_melodic.sh'

# Then run the commands

cmd3 = (featScript + ' ' + designFileName)


_,_ = runCommand(cmd3)

# This will generate ICA spatial maps, time series and statistic maps.


# In[10]:


