import sys
import argparse
import numpy as np

import vtk

from matplotlib import pyplot as plt

from scipy.ndimage.filters import gaussian_filter




#############################################################

def main(*args):

    helpText = ' Help! '

    parser = argparse.ArgumentParser(description=helpText)

    # helpText = "Image in: filename.nii.gz"
    # parser.add_argument('imageIn', type=str, help=helpText)

    args = parser.parse_args()
    # imgFileIn = args.imageIn


    rows, cols, slices = 50,100,50


    np_dat = np.zeros((slices, cols, rows))


    pad = 10
    ii = np.arange(pad, rows-pad)
    jj = np.arange(pad, cols-pad)
    kk = np.arange(pad, slices-pad)
    ijk = np.ix_(ii,jj,kk)

    sz = (slices-2*pad, cols-2*pad, rows-2*pad)
    np_dat[ijk] = np.random.randint(0, 255, sz).astype(np.float32)


    contour_value = np.median(np_dat[ijk])


    np_dat = gaussian_filter(input=np_dat, sigma=3)



    im_dat = vtk.vtkImageData()
    im_dat.SetDimensions(rows, cols, slices)

    im_dat.AllocateScalars(vtk.VTK_FLOAT, 1)

    for k in range(slices):
        for j in range(cols):
            for i in range(rows):
                val = np_dat[k, j, i]
                im_dat.SetScalarComponentFromFloat(i, j, k, 0, val)


    print('x')


    iso_xy = vtk.vtkMarchingSquares()
    iso_xy.SetNumberOfContours(1)
    iso_xy.SetValue(0, contour_value)
    iso_xy.SetInputData(im_dat)


    k_cont = 25

    iso_xy.SetImageRange(0,rows-1,0,cols-1,k_cont,k_cont)
    iso_xy.Update()


    pts = iso_xy.GetOutput()
    pts.GetNumberOfPoints()

    show_dat = np_dat[k_cont] - contour_value
    z = (np.exp(show_dat) / (1 + np.exp(show_dat))) - 0.5

    plt.imshow(z , cmap='gray', interpolation='nearest')

    stripper = vtk.vtkStripper()
    stripper.SetInputData(pts)
    stripper.Update()

    polylines = stripper.GetOutput()

    N_cells = polylines.GetNumberOfCells()



    for l in range(N_cells):


        polyline = polylines.GetCell(l)

        if not polyline.IsA('vtkPolyLine'):
            continue


        xs = []
        ys = []

        pt_list = polyline.GetPointIds()

        for i in range(pt_list.GetNumberOfIds()):
            n = pt_list.GetId(i)
            p_n = polylines.GetPoint(n)
            xs.append(p_n[0])
            ys.append(p_n[1])


        xs = np.asarray(xs)
        ys = np.asarray(ys)
        ix = np.logical_or(np.isnan(xs), np.isnan(ys))
        ix = np.logical_not(ix)
        xs = xs[ix]
        ys = ys[ix]

        plt.plot(xs, ys, 'r')


        n_pts = polyline.GetNumberOfPoints()
        cc = vtk.vtkCellArray()

        cc.Allocate(n_pts - 1, 1000)
        cc.Initialize()

        for i in range(n_pts - 1):
            cc.InsertNextCell(2)
            cc.InsertCellPoint(i)
            cc.InsertCellPoint(i + 1)

        pd = vtk.vtkPolyData()
        pd.SetPoints(polyline.GetPoints())
        pd.SetLines(cc)

        deci = vtk.vtkDecimatePolylineFilter()
        deci.SetInputData(pd)
        deci.SetTargetReduction(0.5)
        deci.Update()

        pd2 = deci.GetOutput()
        pd2.GetNumberOfCells()
        pd2.GetNumberOfPoints()

        assert pd2.GetNumberOfCells() == 1
        assert pd2.GetCellType(0) == vtk.VTK_POLY_LINE


        pl = pd2.GetCell(0)



        xs = []
        ys = []

        pt_list = pl.GetPointIds()

        for i in range(pt_list.GetNumberOfIds()):
            n = pt_list.GetId(i)
            p_n = pd2.GetPoint(n)
            xs.append(p_n[0])
            ys.append(p_n[1])


        xs = np.asarray(xs)
        ys = np.asarray(ys)
        ix = np.logical_or(np.isnan(xs), np.isnan(ys))
        ix = np.logical_not(ix)
        xs = xs[ix]
        ys = ys[ix]

        plt.plot(xs, ys, 'g')


    #
    #
    #
    # deci = vtk.vtkDecimatePolylineFilter()
    # deci.SetInputData(polylines)
    # deci.SetTargetReduction(0.5)
    # deci.Update()
    # polyline_dec = deci.GetOutput()
    #
    # stripper2 = vtk.vtkStripper()
    # stripper2.SetInputData(polyline_dec)
    # stripper2.Update()
    # polylines2 = stripper2.GetOutput()
    #
    #
    #
    # N_cells_dec = polylines2.GetNumberOfCells()
    #
    # for l in range(N_cells_dec):
    #
    #
    #     polyline = polylines2.GetCell(l)
    #
    #     if not polyline.IsA('vtkPolyLine'):
    #         continue
    #
    #
    #     xs = []
    #     ys = []
    #
    #     pt_list = polyline.GetPointIds()
    #
    #     for i in range(pt_list.GetNumberOfIds()):
    #         n = pt_list.GetId(i)
    #         p_n = polylines2.GetPoint(n)
    #         xs.append(p_n[0])
    #         ys.append(p_n[1])
    #
    #
    #     xs = np.asarray(xs)
    #     ys = np.asarray(ys)
    #     ix = np.logical_or(np.isnan(xs), np.isnan(ys))
    #     ix = np.logical_not(ix)
    #     xs = xs[ix]
    #     ys = ys[ix]
    #
    #     plt.plot(xs, ys, 'g')
    #
    #
    #


    plt.show()

    print('x')


#############################################################

if __name__ == '__main__':
  sys.exit(main(*sys.argv))


