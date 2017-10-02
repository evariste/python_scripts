import vtk



import numpy as np


def mkVtkIdList(it):
    vil = vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil


outputName = 'cuboctahedron.vtk'

r = np.sqrt(2)

v0 = (r, 0, -r)
v1 = (0, r, -r)
v2 = (-r, 0, -r)
v3 = (0, -r, -r)

v4 = (r,r,0)
v5 = (r, -r, 0)
v6 = (-r, -r, 0)
v7 = (-r, r, 0)

v8 = (r, 0, r)
v9 = (0, r, r)
v10 = (-r, 0, r)
v11 = (0, -r, r)


w0 = (1, 1, 0)
w1 = (1, 0, 1)


vs = [v0, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11]

pts = vtk.vtkPoints()

nPoints = 12

pts.SetNumberOfPoints(nPoints)
for k, v in enumerate(vs):
    pts.InsertPoint(k, v)


pd = vtk.vtkPolyData()
pd.Allocate(nPoints, nPoints)

pd.SetPoints(pts)
pd.Squeeze()

cellpts = [
    (0,1,2,3),
    (8,9,10,11),
    (0,4,8,5),
    (2,6,10,7),
    (1,4,9,7),
    (3,5,11,6),
    (4,0,1),
    (5,0,3),
    (6,2,3),
    (7,2,1),
    (4, 8, 9),
    (5, 8, 11),
    (6, 10, 11),
    (7, 10, 9)
]
cells = vtk.vtkCellArray()

for k,c in enumerate(cellpts):
    cells.InsertNextCell(mkVtkIdList(c))

# cells.Initialize()
# cells.Allocate(cells.EstimateSize(24, 4), 100)
# cells.InitTraversal()


# cells.InsertNextCell(5)
# cells.InsertCellPoint(0)
# cells.InsertCellPoint(1)
# cells.InsertCellPoint(2)
# cells.InsertCellPoint(3)
# cells.InsertCellPoint(0)


# cells.InsertNextCell(2)
# cells.InsertCellPoint(0)
# cells.InsertCellPoint(1)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(1)
# cells.InsertCellPoint(2)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(2)
# cells.InsertCellPoint(3)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(3)
# cells.InsertCellPoint(0)

#

# cells.InsertNextCell(5)
# cells.InsertCellPoint(8)
# cells.InsertCellPoint(9)
# cells.InsertCellPoint(10)
# cells.InsertCellPoint(11)
# cells.InsertCellPoint(8)


# cells.InsertNextCell(2)
# cells.InsertCellPoint(8)
# cells.InsertCellPoint(9)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(9)
# cells.InsertCellPoint(10)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(10)
# cells.InsertCellPoint(11)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(11)
# cells.InsertCellPoint(8)

#

# cells.InsertNextCell(5)
# cells.InsertCellPoint(0)
# cells.InsertCellPoint(4)
# cells.InsertCellPoint(8)
# cells.InsertCellPoint(5)
# cells.InsertCellPoint(0)


# cells.InsertNextCell(2)
# cells.InsertCellPoint(0)
# cells.InsertCellPoint(4)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(0)
# cells.InsertCellPoint(5)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(8)
# cells.InsertCellPoint(4)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(8)
# cells.InsertCellPoint(5)

#

# cells.InsertNextCell(5)
# cells.InsertCellPoint(2)
# cells.InsertCellPoint(6)
# cells.InsertCellPoint(10)
# cells.InsertCellPoint(7)
# cells.InsertCellPoint(2)

# cells.InsertNextCell(2)
# cells.InsertCellPoint(2)
# cells.InsertCellPoint(6)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(2)
# cells.InsertCellPoint(7)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(10)
# cells.InsertCellPoint(6)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(10)
# cells.InsertCellPoint(7)

#

# cells.InsertNextCell(5)
# cells.InsertCellPoint(1)
# cells.InsertCellPoint(4)
# cells.InsertCellPoint(9)
# cells.InsertCellPoint(7)
# cells.InsertCellPoint(1)

# cells.InsertNextCell(2)
# cells.InsertCellPoint(1)
# cells.InsertCellPoint(4)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(1)
# cells.InsertCellPoint(7)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(9)
# cells.InsertCellPoint(4)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(9)
# cells.InsertCellPoint(7)

#

# cells.InsertNextCell(5)
# cells.InsertCellPoint(3)
# cells.InsertCellPoint(5)
# cells.InsertCellPoint(11)
# cells.InsertCellPoint(6)
# cells.InsertCellPoint(3)


# cells.InsertNextCell(2)
# cells.InsertCellPoint(3)
# cells.InsertCellPoint(5)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(3)
# cells.InsertCellPoint(6)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(11)
# cells.InsertCellPoint(5)
#
# cells.InsertNextCell(2)
# cells.InsertCellPoint(11)
# cells.InsertCellPoint(6)

# cells.Squeeze()

pd.SetPolys(cells)

ptData = vtk.vtkFloatArray()

ptData.SetNumberOfComponents(3)
ptData.SetNumberOfTuples(nPoints)
for i in range(nPoints):
    v = vs[i]
    ptData.SetTuple3(i,v[0], v[1], v[2])
ptData.SetName('coords')

pd.GetPointData().AddArray(ptData)


# Finish off.
pdWriter = vtk.vtkPolyDataWriter()
pdWriter.SetFileName(outputName)
pdWriter.SetInputData(pd)
pdWriter.Update()


print('x')


