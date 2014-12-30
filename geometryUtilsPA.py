
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



def params2matrixAffine(params):
  # Parameters should be in order
  # translations, rotations, scales, shears. Particularly:
  # tx, ty, tz, rx, ry, rz, sx, sy, sz, sxy, syz, sxz
  # Rotations and shears should be expressed in radians
  tx = params[0]
  ty = params[1]
  tz = params[2]
  rx = params[3]
  ry = params[4]
  rz = params[5]
  sx = params[6]
  sy = params[7]
  sz = params[8]
  sxy = params[9]
  syz = params[10]
  sxz = params[11]

  mt = numpy.eye(4)
  mt[0:3, 3] = [tx, ty, tz]

  # mrx = [1       0       0        0 
  #        0       cos(rx) sin(rx)  0 
  #        0      -sin(rx) cos(rx)  0 
  #        0       0       0        1]
  mrx = numpy.eye(4)
  c = math.cos(rx)
  s = math.sin(rx)
  mrx[1,1] = c
  mrx[2,2] = c
  mrx[1,2] = s
  mrx[2,1] = -1.0 * s
  
  # mry = [cos(ry) 0       -sin(ry) 0 
  #        0       1       0        0 
  #        sin(ry) 0       cos(ry)  0 
  #        0       0       0        1]
  mry = numpy.eye(4)
  c = math.cos(ry)
  s = math.sin(ry)
  mry[0,0] = c
  mry[2,2] = c
  mry[0,2] = -1.0 * s
  mry[2,0] = s

  # mrz = [cos(rz) sin(rz) 0        0 
  #       -sin(rz) cos(rz) 0        0 
  #        0       0       1        0 
  #        0       0       0        1]
  mrz = numpy.eye(4)
  c = math.cos(rz)
  s = math.sin(rz)
  mrz[0,0] = c
  mrz[1,1] = c
  mrz[0,1] = s
  mrz[1,0] = -1.0 * s
  
  
  ms = numpy.eye(4)
  ms[0,0] = sx
  ms[1,1] = sy
  ms[2,2] = sz

  # msxy = [1 tan(sxy) 0 0 
  #         0 1        0 0 
  #         0 0        1 0 
  #         0 0        0 1]
  #
  # msxz = [1 0 tan(sxz) 0 
  #         0 1 0        0 
  #         0 0 1        0 
  #         0 0 0        1]
  #
  # msyz = [1 0 0        0 
  #         0 1 tan(syz) 0 
  #         0 0 1        0 
  #         0 0 0        1]

  msxy = numpy.eye(4)
  msxy[0,1] = math.tan(sxy)
  
  msxz = numpy.eye(4)
  msxz[0,2] = math.tan(sxz)
  
  msyz = numpy.eye(4)
  msyz[1,2] = math.tan(syz)
  
  sca = ms
  tra = mt
  ske = msyz.dot(msxz).dot(msxy)
  rot = mrx.dot(mry).dot(mrz)
  
  mat = tra.dot(rot).dot(ske).dot(sca)
  
  d = numpy.linalg.det(mat)
  if numpy.fabs(d) < 0.0000001:
    print 'Warning: params2matrixAffine - determinant close to zero'

  return mat


def randomRotationMatrix():
#  Julie C Mitchell, Sampling Rotation Groups by Successive Orthogonal
#  Image, SIAM J Sci comput. 30(1), 2008, pp 525-547
#  
#  Seek R = [u0 u1 u2] where the columns are the images of the unit axis
#  vectors under the rotation.
#  
#  u2 uniformly sampled from a sphere (see
#  http://mathworld.wolfram.com/SpherePointPicking.html)
  
  a = numpy.random.random_sample()
  phi = 2 * numpy.pi * a
  
  b = numpy.random.random_sample()
  theta = math.acos(2 * b - 1)
  
  u2 = numpy.zeros( (3,) )
  u2[0] = math.cos(phi) * math.sin(theta)
  u2[1] = math.sin(phi) * math.sin(theta)
  u2[2] = math.cos(theta)
  
  # Sample u1 uniformly from the circle that is the intersection of the unit
  # sphere with the plane through O and orthogonal to u2

  u20 = u2[0]
  u21 = u2[1]

  # Find a point w in the xy plane that is also in the plane orthogonal to u2
  # and is one unit from the origin.
  
  smallVal = numpy.spacing(1)
  w = numpy.zeros( (3,) )
  
  if numpy.fabs(u20) < smallVal:
    w[0] = 1
  elif numpy.fabs(u21) < smallVal:
    w[1] = 1
  else:
    w[0] = u21
    w[1] = -1.0 * u20
    w = w / math.sqrt(w.dot(w))

  # Rotate w by a random angle around the axis defined by u2

  theta_w = 2 * numpy.pi * numpy.random.random_sample()
  randRot = rotationGivenAxisAndAngle(u2, theta_w)

  u1 = randRot.dot(w)
  
  u0 = numpy.cross(u1, u2)
  
  R = numpy.vstack( (u0, u1, u2) ).T

  return R