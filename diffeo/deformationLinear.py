import numpy

import sys
sys.path.append('/Users/paulaljabar/Python/nibabel-1.3.0-py2.7.egg')

import nibabel

class DeformationLinear:
  """ 
  A class for deformations defined over a grid of points 
  with continuity given by linear interpolation.
  """
  

  def __init__(self, dimx, dimy, dimz):
    print 'DeformationLinear overloaded __init__'
    shape = (dimx, dimy, dimz)
    self.dx = numpy.zeros(shape)
    self.dy = numpy.zeros(shape)
    self.dz = numpy.zeros(shape)
    
  def Read(self, imageName):
    """
    Load displacement data from an image
    """
    img = nibabel.load(inputFilename)
    imgData = img.get_data()
    
    if not len(x.shape) == 4:
      raise Exception('DeformationLinear.Read : Image data must be 4D')
    
    nx,ny,nz,nVols = x.shape
    
    if not nVols == 3:
      raise Exception('DeformationLinear.Read : Image data must \
      contain three volumes, one each for x, y and z displacements.')
    
    self.dx = imgData[:,:,:,0]
    self.dy = imgData[:,:,:,1]
    self.dz = imgData[:,:,:,2]
    
    
    