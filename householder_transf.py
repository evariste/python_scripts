import numpy as np


from geometryUtilsPA import  *


np.set_printoptions(precision=2)

def getHouseholderTransform(x, y):
# function H = getHouseholderTransform(x, y)
# Find a householder transformation H such that
#   H x = |x| y
#
# Assumes, x, y are column vectors of same dimension.
# Returns square matrix of the right size for transforming x
#
# See http://www.cs.cornell.edu/~bindel/class/cs6210-f12/notes/lec16.pdf


    x = np.atleast_2d(x)
    y = np.atleast_2d(y)

    if x.shape[0] == 1:
        x = x.T

    if y.shape[0] == 1:
        y = y.T


    # dimension:
    d = np.size(x)

    # norm
    nx = np.sqrt(np.sum(x * x))

    u = x - nx * y

    nu = np.sqrt(np.sum(u * u))

    v = u / nu


    H = np.eye(d) - 2 * v.dot(v.T)


    return H


Z = np.zeros((3,1))
Z[2] = 1


N = np.ones((3,1))

H = getHouseholderTransform(N, Z)

print Z

print N


print H

ZZ = H.dot(Z)


print ZZ

print np.sqrt(np.sum(ZZ * ZZ))

print np.linalg.det(H)


HH = -1 * H.copy()


print HH
print np.linalg.det(HH)

ZZ = HH.dot(Z)


print ZZ



ax = np.asarray([1, -1, 0])

ang = -1*np.arctan(np.sqrt(2))

print ax
print ax.shape

print ang


R = rotationGivenAxisAndAngle(ax, ang)


print R

print R.dot(Z)


# % TODO: check dimensions.
#
# d = length(x);
#
# nx = norm(x);
#
# % TODO: check nx non-zero
#
# u = x - nx * y;
#
# nu = norm(u);
#
# % TODO: check nu non-zero
#
# v = u / nu;
#
# H = eye(d) - 2 * (v * v');
#
# end
