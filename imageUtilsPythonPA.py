

import struct
import numpy as np
import math

def get2DKernelFrom1DKernel(ker1d):
  """
  Given a 1-D kernel construct and return the equivalent 2-D separable kernel
  """

  ker1d = np.asarray( ker1d )

  if len(ker1d.shape) > 1:
    raise Exception('get2DKernelFrom1DKernel: Expecting a 1-D kernel')

  k2 = np.atleast_2d( ker1d )
  k2 = k2.T.dot(k2)
  return k2


def get3DKernelFrom1DKernel(ker1d):
  """
  Given a 1-D kernel construct and return the equivalent 3-D separable kernel
  """

  ker1d = np.asarray( ker1d )

  if len(ker1d.shape) > 1:
    raise Exception('get3DKernelFrom1DKernel: Expecting a 1-D kernel')

  k2 = get2DKernelFrom1DKernel(ker1d)

  k2 = k2[:,:,None]
  k3 = k2.dot(  np.atleast_2d(ker1d ) )
  return k3


def getBoxIntegral(integralImage, corner0, corner1):
  """
  Get the integral of values inside a cuboid in a 3D array for which the integral image is given
  defined by corner0 and corner1.

  integralImage: Summed area (volume!) table for some 3D array (a.k.a. integral image)

  corner0, corner1 : length 3 array-like to define the corners of the cuboid in the array.
                     Will not work if any of the indices are zero.

  Sum is inclusive, i.e. includes both array elements at corners. I.e. if M was the original
  array for which the integralImage is given, we return the value of S in the following

  S = 0
  for i in range(x1, x2+1):
   for j in range(y1, y2+1):
    for k in range(z1, z2+1):
      S = S + M[i,j,k]

  """

  # Shorter name.
  m = integralImage

  corner0 = list(corner0)
  corner1 = list(corner1)
  corners = np.vstack((corner0, corner1))

  c0 = np.min(corners, axis=0)
  c1 = np.max(corners, axis=0)

  if np.any(c0 == 0):
    raise Exception('getBoxIntegral: Zero indices not implemented')

  if np.any(c1 >= m.shape):
    raise Exception('getBoxIntegral: indices exceed array size')

  x0, y0, z0 = c0
  x1, y1, z1 = c1

  x0, y0, z0 = x0 - 1, y0 - 1, z0 - 1

  S = (  m[x1, y1, z1]
       - m[x1, y1, z0]
       - m[x1, y0, z1]
       - m[x0, y1, z1]
       + m[x0, y0, z1]
       + m[x0, y1, z0]
       + m[x1, y0, z0]
       - m[x0, y0, z0])

  return S


def getIntegralArray(m, pad=False):
  """
Get an array version of the 'integral image. used in image processing.
For a voxel at position (I,J,K) the value in the output equals the sum
of all voxel values in the input for all (i,j,k) where i <= I, j <= J, k <= K.

   pad : set to True if zero padding required on faces with a zero index.
         (default False). Padding can be useful when integrating between indices
         inclusively (i.e. the indices at the corners are included in the
         integral for a box.
"""

  # TODO: check dimension of m

  dimI, dimJ, dimK = m.shape

  out = m.copy()

  # Corner edges
  for i in range(1, dimI):
    out[i, 0, 0] = out[i, 0, 0] + out[i - 1, 0, 0]

  for j in range(1, dimJ):
    out[0, j, 0] = out[0, j, 0] + out[0, j - 1, 0]

  for k in range(1, dimK):
    out[0, 0, k] = out[0, 0, k] + out[0, 0, k - 1]


  # Corner faces

  for i in range(1, dimI):
    for j in range(1, dimJ):
      out[i, j, 0] = (out[i, j, 0] +
                    out[i - 1, j, 0] +
                    out[i, j - 1, 0] -
                    out[i - 1, j - 1, 0])

  for j in range(1, dimJ):
    for k in range(1, dimK):
      out[0, j, k] = (out[0, j, k] +
                    out[0, j - 1, k] +
                    out[0, j, k - 1] -
                    out[0, j - 1, k - 1])

  for i in range(1, dimI):
    for k in range(1, dimK):
      out[i, 0, k] = (out[i, 0, k] +
                    out[i - 1, 0, k] +
                    out[i, 0, k - 1] -
                    out[i - 1, 0, k - 1])

  for i in range(1, dimI):
    for j in range(1, dimJ):
      for k in range(1, dimK):

        out[i, j, k] = (out[i, j, k] +
                      out[i - 1, j, k] +
                      out[i, j - 1, k] +
                      out[i, j, k - 1] -
                      out[i - 1, j - 1, k] -
                      out[i - 1, j, k - 1] -
                      out[i, j - 1, k - 1] +
                      out[i - 1, j - 1, k - 1])


  if pad:
    i, j, k = out.shape
    i, j, k = i + 1, j + 1, k + 1
    temp = np.zeros((i, j, k))
    temp[1:, 1:, 1:] = out
    return temp
  else:
    return out

def writeIRTKMatrix(filename, m):
  """
Write the contents of a numpy array to an IRTK matrix (.mat) format file.

 m       : numpy array (2D)
 filename: name of file to write the data in   m   to.
"""
  r, c = m.shape
  f = open(filename, 'w')
  f.write('irtkMatrix {:d} x {:d}\n'.format(r, c))

  # Column-wise reshape:
  mm = m.T.reshape((-1, 1))

  # > means bigendian then ddddddd... for as many elements as we need.
  formatStr = '>' + 'd' * (r * c)

  data = struct.pack(formatStr, *mm)
  f.write(data)
  f.close()
