

import numpy as np
import poscar
import latticeUtils

class Clusters:
  def __init__(self, poscar, verbose=False, neighbors=None, marked=None):
    """Class to find and define clusters. There are "marked atoms",
    defined by the used, and the idea is to find, create, increase a
    cluster respect to the marked atoms. Always, the marked atoms
    belongs to a host lattice

    `poscar` is an instance of the class `poscar.Poscar`
    `neighbors` is an instance of `latticeUtils.neighbors`
    `marked` what atoms are marked. If absent, it implies all atoms

    """
    self.p = poscar
    self.clusters = [] # it a list of lists. One list by each cluster
    self.verbose = True # verbose
    # calculating the neighbors can be demanding, using them if given
    self.neighbors = neighbors
    if self.neighbors is None:
      self.neighbors = latticeUtils.Neighbors(self.p, verbose=False)
    self.marked = marked
    if self.marked is None:
      self.marked = list(range(self.p.Ntotal))
    if self.verbose:
      print('\n\nclusters.Clusters.__init__():')
      print('atoms marked', self.marked)
    self.find_clusters()
    return


  def find_clusters(self):
    """
    
    """
    # I will start assuming every atom has its own cluster, the
    # interaction will join the sets
    clusters = [set([i]) for i in self.marked]
    nn_list = self.neighbors.nn_list

    # In the main iteration I will modify the contents of `clusters`,
    # then I need to loop over another, immutable object.
    
    # which atoms are connected to atom 0
    for atom in self.marked:
      # I need to search for all the pairs of interacctions
      neighbors = nn_list[atom]
      for neighbor in neighbors:
        # print(atom, neighbor)
        # finding the clusters with 'atom' and 'neighbor', removing
        # them and then appending its union.
        # The las term in the if is to avoid checking: 1<->2, 2<->1
        if neighbor in self.marked and neighbor < atom:
          for c in clusters:
            if atom in c:
              c1 = c
            if neighbor in c:
              c2 = c
          # I am going to append `c1` (perhaps united to `c2`) to
          # `clusters` later
          clusters.remove(c1)
          if c1 != c2:
            clusters.remove(c2)
          clusters.append(c1.union(c2))
          # print(atom, neighbor, clusters)
    self.clusters = [list(x) for x in clusters]
    if self.verbose:
      print('clusters:', clusters)
    # self._set_nn_clusters()
    return

