import numpy as np
from matplotlib import pyplot as plt

import sys

if len(sys.argv) < 2:
    sys.exit(1)

fileA = sys.argv[1]

a = np.load(fileA)



plt.imshow(a, cmap=plt.get_cmap('gray'), interpolation='nearest')
plt.colorbar()
plt.title(fileA)
plt.show()

