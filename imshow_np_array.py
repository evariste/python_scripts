import numpy as np
from matplotlib import pyplot as plt

import sys

if len(sys.argv) < 2:
    sys.exit(1)

fileA = sys.argv[1]

a = np.load(fileA)



plt.imshow(a, cmap=plt.get_cmap('gray'), interpolation='nearest')
plt.colorbar()

titleStr=fileA
if len(titleStr)>50:
    titleStr = '...' + titleStr[-50:]
plt.title(titleStr)

plt.show()

