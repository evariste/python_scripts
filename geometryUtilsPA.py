
import numpy
import math


def angleBetweenVectors(v,w):
  a = numpy.dot(v,w)
  b = numpy.dot(v,v)
  c = numpy.dot(w,w)
  return math.acos(a / math.sqrt(b * c))



def skewSym(v):
  '''
  Return the skew symmetric matrix form of the vector v.
  
  v = (v0 v1 v2)^T
  
      [    0  -v2   v1  ]
  s = [   v2    0  -v0  ]
      [  -v1   v0    0  ]  
  
  '''

  if not v.shape == (3,):
    print 'skewSym: Error - must be a 3 vector'
    return None
  
  s = numpy.zeros( (3,3) )
  s[0,2] = v[1]
  s[1,0] = v[2]
  s[2,1] = v[0]
  
  return s - s.T
  


def rotationGivenAxisAndAngle(u, theta):
  '''
  
  Return rotation matrix for axis u and angle theta using Rodrigues' formula.
  
  Rotation is in anti-clockwise sense looking backwards along the axis of
  rotation in a right-handed frame.
  
  Rotation is in anti-clockwise sense looking forwards along the axis of
  rotation in a left-handed frame.

  '''

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
  '''
  
  Generate a matrix based on a given set of 6, 9 or 12 affine parameters.
  The parameters are the elements of input array.
  
  Parameters should be in order!
  
  translations, rotations, scales, shears. 
  
  Particularly:
  tx, ty, tz, rx, ry, rz, sx, sy, sz, sxy, syz, sxz
                          - - - - - - - - - - - - -
                          Optional 
                          
  Rotations and shears should be expressed in radians

  if 6 parameters are given scalings are assumed to be 1.0 and shears 0.
  
  If 9 parameters are given shears are set to zero.
  
  '''
  
  tx = params[0]
  ty = params[1]
  tz = params[2]
  rx = params[3]
  ry = params[4]
  rz = params[5]
  
  if len(params) > 6:
    sx = params[6]
    sy = params[7]
    sz = params[8]
  else:
    sx = 1.0
    sy = 1.0
    sz = 1.0
  
  if len(params) > 9:
    sxy = params[9]
    syz = params[10]
    sxz = params[11]
  else:
    sxy = 0.0
    syz = 0.0
    sxz = 0.0

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
  '''
  
  See Julie C Mitchell, Sampling Rotation Groups by Successive Orthogonal
  Image, SIAM J Sci comput. 30(1), 2008, pp 525-547
  
  Returns R = [u0 u1 u2] where the columns are the images of the unit axis
  vectors under the random rotation.
  
  u2 uniformly sampled from a sphere (see
  http://mathworld.wolfram.com/SpherePointPicking.html)
  
  '''
  
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



def matrix2paramsAffine(m):
  '''
  
  Return a dictionary of parameters for a decomposition of matrix m into four
  matrices
  
  m = T R K S 
  
  where T is a translation matrix, R is a rotation matrix, K is a shear matrix
  and S is a scaling matrix
  
  Dictionary keys are 12 strings: 
  
  ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'sxy', 'sxz', 'syz']
 
  '''
  
  if not m[3,3] == 1:
    print 'matrix2paramsAffine: Matrix entry in lower right must equal 1'
    return None
  
  uleft = m[0:3, 0:3]
  
  smallVal = numpy.spacing(1)
  d = numpy.fabs(numpy.linalg.det(uleft))
  if d < smallVal:
    print 'matrix2paramsAffine: matrix is singular'
    return None
  
  
  pars = {'tx': m[0,3], 
          'ty': m[1,3],
          'tz': m[2,3]}
  
  
  c0 = m[0:3, 0].copy()
  c1 = m[0:3, 1].copy()
  c2 = m[0:3, 2].copy()

  n = numpy.linalg.norm(c0)
  pars['sx'] = n
  c0 = c0 / n
  
  tansxy = c0.dot(c1)
  c1 = c1 - tansxy * c0
  
  n = numpy.linalg.norm(c1)
  pars['sy'] = n
  c1 = c1 / n

  tansxy = tansxy / pars['sy']

  tansxz = c0.dot(c2)
  c2 = c2 - tansxz * c0
  
  tansyz = c1.dot(c2)
  c2 = c2 - tansyz * c1

  n = numpy.linalg.norm(c2)
  pars['sz'] = n
  c2 = c2 / n

  tansxz = tansxz / pars['sz']  
  tansyz = tansyz / pars['sz']

  if c0.dot(numpy.cross(c1, c2)) < 0:
    pars['sx'] = pars['sx'] * -1.0
    pars['sy'] = pars['sy'] * -1.0
    pars['sz'] = pars['sz'] * -1.0
    c0 = c0 * -1.0
    c1 = c1 * -1.0
    c2 = c2 * -1.0
    
  ry = math.asin(-1 * c2[0])
  
  if math.fabs( math.cos(ry) ) > smallVal:
    rx = math.atan2(c2[1], c2[2])
    rz = math.atan2(c1[0], c0[0])
  else:
    rx = atan2(-1.0 * c2[0] * c0[1], -1.0 * c2[0] * c0[2])
    rz = 0.0
    
  pars['rx'] = rx
  pars['ry'] = ry
  pars['rz'] = rz
  
  pars['sxy'] = math.atan(tansxy)
  pars['sxz'] = math.atan(tansxz)
  pars['syz'] = math.atan(tansyz)

  return pars

def randomAffineMatrix(forceSimilarity=False, useShears=True, limTrans=20, limScale=2.0, limShear=0.2):
  '''
  
  Get a random affine matrix with a number of options
  
   forceSimilarity : Set to True if all scaling should be isotropic
   
   useShears : Default True. Set to False if not required.
   
   limTrans : Value to determine range from which random translation components are drawn
              [-limTrans , limTrans]
   
   limScale : Value to determine range of (multiplicative) scale components
              [1/limScale, limScale] . Must be positive.
   
   limShear : Determines shear angle range.  [-limShear*pi limShear*pi]
   '''

  nPts = 101
  ii = numpy.random.randint(0, nPts, size=9)
  
  tRange = numpy.linspace(-1*limTrans, limTrans, nPts)
  tx = tRange[ii[0]]
  ty = tRange[ii[1]]
  tz = tRange[ii[2]]
  
  logLimScale = math.log10(limScale)
  sRange = numpy.logspace(-1.0*logLimScale, logLimScale, nPts)
  sx = sRange[ii[3]]
  sy = sRange[ii[4]]
  sz = sRange[ii[5]]
  
  if forceSimilarity:
    sy = sx
    sz = sx

  if useShears:
    kRange = numpy.linspace(-1.0*limShear*math.pi, limShear*math.pi, nPts)
    sxy = kRange[ii[6]] 
    syz = kRange[ii[7]] 
    sxz = kRange[ii[8]] 
  else:
    sxy = 0.0 
    syz = 0.0 
    sxz = 0.0 
  
  tra = numpy.eye(4)
  sca = numpy.eye(4)
  msxy = numpy.eye(4)
  msxz = numpy.eye(4)
  msyz = numpy.eye(4)
  rot = numpy.eye(4)

  
  tra[0:3, 3] = [tx, ty, tz] 
  
  sca[0,0] = sx
  sca[1,1] = sy
  sca[2,2] = sz

  msxy[0,1] = math.tan(sxy)
  
  msxz[0,2] = math.tan(sxz)
  
  msyz[1,2] = math.tan(syz)
  
  ske = msyz.dot(msxz).dot(msxy)
  
  r = randomRotationMatrix()
  rot[0:3,0:3] = r

  m = tra.dot(rot).dot(ske).dot(sca)
  
  if math.fabs(numpy.linalg.det(m)) < 0.000001:
    print 'randomAffineMatrix: Danger! Determinant close to zero'
    
  return m

