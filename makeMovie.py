
# See
# http://docs.opencv.org/modules/highgui/doc/reading_and_writing_images_and_video.html

import sys


import glob

import cv2

import numpy

from PIL import Image



if len(sys.argv) < 2:
  print ''
  print 'Usage : python', sys.argv[0], ' [output]  [prefix]'
  print ''
  print 'Convert a set of still images to a movie'
  print 'E.g. if all the images are in a subfolder called \'frames\''
  print 'with names fr-XXX.png, where XXX is a number, then call like this'
  print '   python', sys.argv[0], 'output.mov frames/fr- '
  print ''
  sys.exit(1)


outputFile = sys.argv[1]
prefix = sys.argv[2]

displayOn = True

files = glob.glob(prefix + '*')

print 'found {:d} files ...'.format(len(files))


f = files[0]
im = Image.open(f)
w, h = im.size

fps = 10
# w = 640
# h = 480


#codecStrOut = 'X264'
codecStrOut = '8BPS'

codecOut = cv2.cv.CV_FOURCC(*codecStrOut)
print 'codec out : ', codecOut, ' = ' , codecStrOut


outWriter = cv2.VideoWriter(outputFile, codecOut, fps, (w,h) )

print 'Writer set'

for f in files:
  print f
  im = Image.open(f)
  # im = im.resize( (w,h) , Image.BILINEAR)
  f = numpy.asarray(im)

  if displayOn:
    cv2.imshow('frame', f)
    cv2.waitKey(100)

  del im


  outWriter.write(f)


if displayOn:
  cv2.destroyAllWindows()


outWriter.release()


