# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 17:36:06 2016

@author: paulaljabar
"""

import sys
import nibabel as nib
import numpy as np
import argparse
# from matplotlib import pyplot


def main(*args):
    helpText = ("XXX")
    parser = argparse.ArgumentParser(description=helpText)

    helpText = "Input image [filename]"
    parser.add_argument("input", type=str, help=helpText)

    helpText = "Output image [filename]"
    parser.add_argument("output", type=str, help=helpText)

    helpText = "References"
    parser.add_argument("-refs", type=str, nargs='*', help=helpText)

    helpText = 'Mask image [filename] (dimensions must match input image)'
    parser.add_argument("-mask", type=str, help=helpText, default=None)

    args = parser.parse_args()

    #############################################################

    inputFilename = args.input
    maskFilename = args.mask
    outputName = args.output
    refs = args.refs

    if (refs == None) or len(refs) == 0:
        print 'Please specify reference images'
        sys.exit(1)


    img = nib.load(inputFilename)
    imgData = img.get_data()
    imgData = imgData.squeeze()

    dims = imgData.shape

    nChannels = 1
    if len(dims) > 3:
        nChannels = dims[3]
    else:
        # Ensure 4D with singleton dimension at end
        imgData = np.expand_dims(imgData, axis=3)



    if maskFilename == None:
        mask = np.ones(shape=dims[:3])
    else:
        maskImg = nib.load(maskFilename)
        mask = maskImg.get_data().squeeze()
        if np.any(mask.shape != dims[:3]):
            raise Exception('Error: Image and mask mismatch.')


    nVoxels = np.count_nonzero(mask)

    nRefs = len(refs)

    # Read the reference images' data
    allRefData = np.zeros(shape=(nRefs, nChannels, nVoxels))

    for r, ref in enumerate(refs):
        refImg = nib.load(ref)
        refData = refImg.get_data()

        for c in range(nChannels):
            allRefData[r, c, :] = np.ravel(refData[mask > 0, c])



    # Size: nVoxels x nChannels
    inputData = imgData[mask > 0, :]
    outData = np.zeros(shape=(nVoxels,))

    for v in range(nVoxels):

        currData = allRefData[:, :, v].squeeze()
        C = np.cov(currData.T)

        if np.linalg.det(C) < 0.0001:
            continue

        mu = np.mean(currData, axis=0, keepdims=True)
        x = inputData[np.newaxis, v, :]
        d = x - mu
        iC = np.linalg.inv(C)

        outData[v] = np.sqrt( d.dot(iC).dot(d.T) )


    # Save a 3D map of the scores.
    imgDataOut = np.zeros(mask.shape)

    imgDataOut[mask > 0] = outData
    imgOut = nib.Nifti1Image(imgDataOut,
                             img.get_affine())
    nib.save(imgOut, outputName)




    print 'x'


###############################################################


if __name__ == '__main__':
    sys.exit(main(*sys.argv))


