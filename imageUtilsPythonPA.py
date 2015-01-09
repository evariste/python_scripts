

import struct
import numpy as np
import math

def getBoxIntegral(integralImage, corner0, corner1):
  """
  Get the integral of values inside a cuboid in a 3D array for which the integral image is given
  defined by corner0 and corner1.
  Sum is inclusive, i.e. includes both corner
  """

  # TODO: check dimension of m, and corners.

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

  x1, y1, z1 = c0
  x2, y2, z2 = c1

  x1, y1, z1 = x1 - 1, y1 - 1, z1 - 1

  return (m[x2, y2, z2] -
          m[x2, y2, z1] -
          m[x2, y1, z2] -
          m[x1, y2, z2] +
          m[x1, y1, z2] +
          m[x1, y2, z1] +
          m[x2, y1, z1] -
          m[x1, y1, z1])



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
