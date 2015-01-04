
import sys
import subprocess

sys.path.append('/Users/paulaljabar/work/scripts/python')

from generalUtilsPythonPA import runCommand
from deformationLinear import *


x = DeformationLinear(2,3,4)
print x.dx


s = """
a b

c d

1 2 3 

"""

print s

