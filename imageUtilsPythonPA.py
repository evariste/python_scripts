

import struct
import numpy
import math


  
def writeIRTKMatrix(filename, m):  
  # m       : numpy array (2D)
  # filename: name of file to write the data in   m   to.
  
  r, c = m.shape
  f = open(filename, 'w')
  f.write('irtkMatrix {:d} x {:d}\n'.format(r, c))
  
  # Column-wise reshape:
  mm = m.T.reshape( (-1,1) )
  
  # > means bigendian then ddddddd... for as many elements as we need. 
  formatStr = '>' + 'd'*(r*c)
  
  data = struct.pack(formatStr, *mm)
  f.write( data )
  f.close()
