import numpy as np
from struct import unpack_from

import graph_tool as gt


def readRawData(filename, symmetric=True):
  ''' 
  Read output file from a tractography run.
  Return a symmetrised matrix unless non-symmetric is specifically requested.
  Raise exception if file does not represent a square matrix.
  '''
  f = open(filename)
  b = f.read()
  f.close()

  r,c = unpack_from('2i', b)
  
  if not r == c:
    raise Exception('readRawData: Expecting a square matrix.')
  
  fmt = str(r*c) + 'd'

  data =  np.asarray(unpack_from(fmt, b, offset=8))

  data = data.reshape((r,c))
    
  if symmetric:
    data = 0.5 * (data + data.T)
  
  return data


def matrixToGraph(data):
  '''
  Return a graph object based on a edge property map called 'weight'. Edge 
  weights given in matrix 'data'
  Raise exception if matrix is not square
  '''
  
  if not len(data.shape) == 2:
    raise Exception('matrixToGraph: Expecting a 2D array.')
  
  r,c = data.shape

  if not r == c:
    raise Exception('matrixToGraph: Expecting a square matrix.')
  

  G = gt.Graph(directed=False)
  _ = G.add_vertex(r)

  ix,jx = np.where(data > 0)
  st = zip(ix,jx)
  st = filter(lambda (x,y): x < y, st)
  G.add_edge_list(st)

  eWeights = G.new_edge_property('double')

  for e in G.edges():
    eWeights[e] = data[e.source(), e.target()]
  
  G.edge_properties['weight'] = eWeights

  return G



