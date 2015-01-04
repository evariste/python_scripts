
import sys
import subprocess

sys.path.append('/Users/paulaljabar/work/scripts/python')

from generalUtilsPythonPA import runCommand
from deformationLinear import *


x = DeformationLinear(2,3,4)
print x.dx

a,b = runCommand('ls *.vtk', shellVal=True)


print 'a ' + a

print 'b ' + b

