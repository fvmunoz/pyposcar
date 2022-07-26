

import numpy as np
import poscar
import latticeUtils
import poscarUtils
import copy
import db

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
    # The poscar object should not be modified within this class. It
    # has info about the underlying lattice. The 'changes' are
    # virtual, in 'self.marked'
    self.p = copy.deepcopy(poscar)
    self.db = db.DB()
    self.clusters = [] # it a list of lists. One list by each cluster
    self.verbose = verbose
    # calculating the neighbors can be demanding, using them if given
    self.neighbors = neighbors
    if self.neighbors is None:
      self.neighbors = latticeUtils.Neighbors(self.p, verbose=False)
    self.marked = set(marked)
    if self.marked is None:
      self.marked = set(range(self.p.Ntotal))
    if self.verbose:
      print('\n\nclusters.Clusters.__init__():')
      print('atoms marked', self.marked)
    self.find_clusters()
    return


  def find_clusters(self):
    """It find the clusters (in the crystal's lattice) within the
    "marked" atoms

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
      print('clusters.Clusters.find_clusters(), clusters:', self.clusters)
    # self._set_nn_clusters()
    return

  def extend_clusters(self, n=1):
    """
    It 'marks' the first neighbors of a cluster (ie: they are added to
    the cluster). It is performed `n` times
    """
    # the self.marked object is going to be updated, so better to
    # create a new -static- object list(...)
    for i in range(n):
      if self.verbose:
        print('clusters.Clusters.extend_clusters()... Iteration', i)
      for atom in list(self.marked):
        for neighbor in self.neighbors.nn_list[atom]:
          self.marked.add(neighbor)
      self.find_clusters()
      if self.verbose:
        print('clusters.Clusters.extend_clusters()... clusters:', self.clusters)

  def write(self, filename):
    # the poscar object should not be modified
    pu = poscarUtils.poscar_modify(copy.deepcopy(self.p), verbose=False)
    # a set with all atoms
    to_remove = set(list(range(pu.p.Ntotal)))
    to_remove = list(to_remove - self.marked)
    if self.verbose:
      print('cluster.Cluster.write() ... atoms to remove')
      print(to_remove)
    pu.remove(to_remove)
    if self.verbose:
      print('cluster.Cluster.write() ... going to write ', filename)
    pu.write(filename)

  def smooth_edges(self, ignoreH=False, coordination=1):
    """It removes all the 'marked' atoms with coordination equal or lower
    than `coordination`. It is useful to invoke after
    Clusters.extend_clusters()

    `ignoreH`: If True, the H atoms with coordination 1 or larger
    won't be unmarked. Default: False

    """
    # creating a new poscar, only with selected atoms
    new_pu = poscarUtils.poscar_modify(copy.deepcopy(self.p))
    # a set with all atoms
    to_remove = set(list(range(new_pu.p.Ntotal)))
    to_remove = list(to_remove - self.marked)
    new_pu.remove(to_remove)
    new_poscar = new_pu.p
    
    cluster_neighbors = latticeUtils.Neighbors(new_poscar)
    new_nn_list = cluster_neighbors.nn_list
    if self.verbose:
      print(list(zip(self.marked,new_nn_list)))
    # the list(...) is to create an immutable object, I will modify
    # `self.marked`
    removed = []
    for atom, neighbors in list(zip(self.marked,new_nn_list)):
      if ignoreH is True and self.p.elm[atom] == 'H':
        cutoff = coordination
      else:
        cutoff = 1
        
      if len(neighbors) <= cutoff:
          self.marked.remove(atom)
          removed.append(atom)

    if self.verbose:
      print('clusters.Clusters.smooth_edges() ... atoms removed (dangling bonds)')
      print(removed)
          
  def hydrogenate(self):
    """It replaces a 'non-marked' nearest neighbor by of the lattice by a H atom.
    
    The angles (directions) of the bonds are the same of the
    underlying lattice, but the distances are scaled to better reflect
    the real distance (maybe inaccurate)

    """
    # first, detect what atoms need to be attached a H atom
    print('\n\nclusters.py -> Clusters.hydrogenate():...')
    # I need to iterate over static elements, so better to use a list
    # instead of a set.
    marked = list(self.marked)
    # the nearest neighbors need to be converted to sets. Only for
    # marked atoms.
    nn_set = [set(self.neighbors.nn_list[atom]) for atom in marked]
    print('marked atoms and their neigbors')
    print(list(zip(marked, nn_set)))
    # to use '-' marked needs to be a set. Anyways, mutability is not an issue here
    missing_atoms = [x - self.marked for x in nn_set]
    print('missing_atoms', missing_atoms)
    
    # second, adding the H atoms
    for atom, ma in zip(marked, missing_atoms):
      print(atom, ma)
      for i in ma:
        p0 = self.p.dpos[atom]
        p1 = self.p.dpos[i]
        # delta is the vector to put the H atom
        delta = p1-p0
        # It might happen that the neigbor atom belongs to a different
        # lattice (i.e. [0,0,0.1] and [0,0,0.9]) the H atom should be
        # at [0,0,0.1-delta], not in [0,0,0.1+delta]. Notice, it is
        # not necessary to compare all the 3*3*3 possibilities to get
        # the smallest distance. If the value of any coordinate,
        # |pos1_i-pos2_i|< 1/2, it is in the rigth cell. This is
        # because we are working in a large supercell and the error
        # for wrong PBCs is large too.
        for i in [1,2,3]:
          if delta[0] > 0.5:
            delta[0] = delta[0] - 1
          elif delta[0] < -0.5:
            delta[0] = delta[0] + 1
        # normalizing the direction delta:
        delta = delta/np.linalg.norm(delta)
        # bond_length
        bond_length = self.db.estimateBond(self.p.elm[atom], self.p.elm[i])
        print('adding H at', i, p0,p1, delta, bond_length)
        
          
        
