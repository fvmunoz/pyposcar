"""General lattice related utilities.

-distances(positions, lattice=None, verbose=False):
 calculates the PBC-aware distances among all positions.



"""
import  numpy as np


def distances(positions, lattice=None, verbose=False):
  """The positions have to be in cartesian""" 
  
  # I will calculate the whole distance matrix, first I need to expand
  # the arrays by replicating the data
  
  pbc_list = []
  if lattice is not None:
    for i in [-1, 0, 1]:
      for j in [-1, 0, 1]:
        for k in [-1, 0, 1]:
          pbc_list.append(i*lattice[0] + j*lattice[1] + k*lattice[2])
  else:
    pbc_list = [np.array([0,0,0])]
  pbc_list = np.array(pbc_list)
  if verbose:
    print('PBC lists:')
    print(pbc_list)
    
  N = len(positions)
  if verbose:
    print('positions')
    print(positions, positions.shape)
    
  # d is a list of NxN distance-matrices (one per pbc_list)
  d = []
  for vector in pbc_list:
    # rows have the position in the central cell
    rows = positions.repeat(N,axis=0)
    rows.shape = (N, N, 3)
    # columns have position on the extended cells
    npos = positions + vector
    columns = npos.repeat(N,axis=0)
    columns.shape = (N, N, 3)
    columns = np.transpose(columns, axes=(1,0,2))
    if verbose:
      print('rows[0]')
      print(rows[0], rows.shape)
      print('columns[0]')
      print(columns[0], columns.shape)
      # calculating the distance
    d.append( np.linalg.norm(rows-columns, axis=2) )
    
  # lets assume the first distance is the minimum distance
  dist = d.pop(0)
  for matrix in d:
    # np.minimum is element-wise
    dist = np.minimum(dist, matrix)
  if verbose:
    print('distances')
    print(dist, dist.max())
  return dist

