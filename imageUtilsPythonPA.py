

import struct
import numpy
import math


def angleBetweenVectors(v,w):
  a = numpy.dot(v,w)
  b = numpy.dot(v,v)
  c = numpy.dot(w,w)
  return math.acos(a / math.sqrt(b * c))



def skewSym(v):
  # Return the skew symmetric matrix form of the vector v.
  #
  #  v = (v0 v1 v2)^T
  #
  #     [  0  -v2  v1 ]
  # s = [  v2  0  -v0 ]
  #     [ -v1  v0  0  ]  

  if not v.shape == (3,):
    print 'skewSym: Error - must be a 3 vector'
    return None
  
  s = numpy.zeros( (3,3) )
  s[0,2] = v[1]
  s[1,0] = v[2]
  s[2,1] = v[0]
  
  return s - s.T
  


def rotationGivenAxisAndAngle(u, theta):
# Return rotation matrix for axis u and angle t
# Uses Rodrigues' formula
#
# Rotation is in anti-clockwise sense looking backwards along the axis of
# rotation in a right-handed frame.
#
# Rotation is in anti-clockwise sense looking forwards along the axis of
# rotation in a left-handed frame.


  if not u.shape == (3,):
    print "rotationGivenAxisAndAngle: Error - expecting a 3-vector"
    return None
  
  n = math.sqrt(numpy.dot(u,u))
  
  if n < 0.0000001:
    print "rotationGivenAxisAndAngle: Warning : given vector has very small magnitude"

  # Ensure unit
  u = u / n
  
  # Outer product
  uut = numpy.outer(u, u)
  
  I3 = numpy.eye(3)
  
  R = uut
  R = R + (math.cos(theta) * (I3 - uut))
  R = R + math.sin(theta) * skewSym(u)
  
  return R

  
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
