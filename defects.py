""" 
Defect-related utilities

class
FindDefect
- It tries to identify any defect by statistical means    


"""
import latticeUtils
import poscarUtils
import copy
import generalUtils

import numpy as np
try:
  from sklearn.neighbors.kde import KernelDensity
except:
  from sklearn.neighbors import KernelDensity

from scipy.signal import argrelextrema

import matplotlib.pyplot as plt


class FindDefect:
  """Tries to identify a defect
  """
  def __init__(self, poscar, verbose=False):
    # avoiding to modify the original poscar
    self.p = copy.deepcopy(poscar)
    self.verbose = verbose
    self.defects = {} # all the defects from the different methods
                      # should be here. It is a dictionary of lists
    self.all_defects = [] # a simple list with all the defects found
    self.neighbors = latticeUtils.Neighbors(self.p, verbose=False)
    self.find_forgein_atoms()
    self.nearest_neighbors_environment()
    return

  def _set_all_defects(self):
      """
      Updates the `self.all_defects` list from `self.defects`. It
      should be run after any update to `self.defects`
      """
      indexes = list(self.defects.values())
      indexes = [set(x) for x in indexes]
      indexes = list(set.union(*indexes))
      self.all_defects = indexes

  def find_forgein_atoms(self):
    numberSp = self.p.numberSp # number of atoms per element
    if len(set(numberSp)) > 1:
      if self.verbose:
        print("\nFindDefect.find_forgein_atoms()")
        print("Number of atoms per element", self.p.numberSp)
    else:
      self.defects['find_forgein_atoms'] = []
      return
    # reshaping the data for machine learning
    numberSp = numberSp.reshape(-1, 1)
    # print(numberSp)
    # 
    kde = KernelDensity(kernel='gaussian', bandwidth=3).fit(numberSp)
    # The samples are chosen to have a `max-min-max` pattern (maybe
    # with extra -min-max blocks)
    delta = max(int(self.p.Ntotal*0.1),10) # to have a local maximum at start/end
    samples = np.linspace(-delta, max(numberSp.flatten())+delta)
    scores = kde.score_samples(samples.reshape(-1,1))
    samples, scores = generalUtils.remove_flat_points(samples, scores)
    print(scores)
    #plt.plot(samples, scores)
    #plt.show()
    self.verbose = True
    #
    # The local minima of the scores denotes the groups. argrelextrema
    # returns a tuple, only first entry is useful
    minima = argrelextrema(scores, np.less)[0]
    print(argrelextrema(scores, np.less))
    maxima = argrelextrema(scores, np.greater)[0]
    if self.verbose:
      print('local max:',maxima,'  localmin:', minima)
    if len(maxima) <= len(minima):
      print('Maxima, ', maxima)
      print('Minima, ', minima)
      raise RuntimeError('FindDefect.find_forgein_atoms error: '
                         'the local min/max doesnt follows '
                         'the expected order')
    # The threshlod to determine if an atom is forgein.
    try: # perhaps there is no minumum
      lower_min = minima[0]
    except IndexError:
      print('\n\ndefects.FindDefect.find_forgein_atoms(): No defect found')
      self.defects['find_forgein_atoms'] = []
      self._set_all_defects()
      return
    # likely only the smallest cluster of atoms are defects, but if
    # there are three or more cluster, I am not so sure, and the user
    # should be warned
    if len(minima) > 1: # printing regardless verbosity
      print("\n\nWARNING: in FindDefect.find_forgein_atoms() more than "
            "two sets of atoms were found. Cluster delimited by "
            "`minima`= ", minima, ', `maxima=`', maxima)
      print('Only elements with less than ', lower_min, 'atoms are regarded as defects')
    
    defect_elements = []
    # detecting what elements are defects
    for (natoms, element) in zip(self.p.numberSp, self.p.typeSp):
      if natoms <= lower_min:
        defect_elements.append(element)
    defects = []
    for i in range(len(self.p.elm)):
      if self.p.elm[i] in defect_elements:
        defects.append(i)

    if self.verbose:
      print('list of defects: ')
      print([(i,self.p.elm[i]) for i in defects])
    self.defects['find_forgein_atoms'] = defects
    self._set_all_defects()
    return defects
    
  def nearest_neighbors_environment(self):
    """This method looks for atoms with an statistically different
    environment (nearest neighbors).

    The enviornment of each atom (i.e. the number and type of
    elements) are compared, and those statiscally different from the
    rest are dibbed as defects.

    A good nearest neighbors list is a must for this method.

    """
    # self.verbose = True
    nn_elem = self.neighbors.nn_elem
    # Building a single string with the environment, it needs to be
    # sorted, for taking statistics
    nn_elem = [''.join(sorted(x)) for x in nn_elem]
    
    # Assume in hBN a B->N defect, its environment is NNN, which seems
    # fine, but for a B atom, not when surrounding a N. This means
    # that the atom at which its environment is being proccesed also
    # matters. And it can be distinguihed from its environment (no
    # sorting)
    nn_elem = [x[0]+x[1] for x in zip(self.p.elm, nn_elem)]
    
    # counting the frequency of unique elements
    from collections import Counter
    uniques = Counter(nn_elem)
    if self.verbose:
      print('\nFindDefect.nearest_neighbors_environment()')
      print('Atomic environments and their frequency:')
      print(list(zip(uniques.keys(), uniques.values())))
    # now determining which of them are defects
    
    data = np.array(list(uniques.values())).reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=3).fit(data)
    # The samples are chosen to have a `max-min-max` pattern (maybe
    # with extra -min-max blocks)
    delta = max(int(self.p.Ntotal*0.1),10) # to have a local maximum at start/end
    samples = np.linspace(-delta, max(data.flatten())+delta)
    scores = kde.score_samples(samples.reshape(-1,1))
    # print(scores)
    #
    # The local minima of the scores denotes the groups. argrelextrema
    # returns a tuple, only first entry is useful
    minima = argrelextrema(scores, np.less)[0] 
    maxima = argrelextrema(scores, np.greater)[0]

    if self.verbose:
      print('local max:',maxima,'  localmin:', minima)
    if len(maxima) <= len(minima):
      print('Maxima, ', maxima)
      print('Minima, ', minima)
      raise RuntimeError('FindDefect.nearest_neighbors_environment error: '
                         'the local min/max doesnt follows '
                         'the expected order')
    # The threshlod to determine if an atom is forgein.
    try:
      lower_min = minima[0]
    except IndexError:
      print('\n\ndefects.FindDefect.nearest_neighbors_environment(): No defect found')
      self.defects['nearest_neighbors_environment'] = []
      self._set_all_defects()
      return

    # likely only the atoms with an environment less abundant than
    # `lower_min` are to be regarded as defects. But if there are
    # three or more statistically different types of environment, the
    # user should be warned 
    if len(minima) > 1: # printing regardless verbosity
      print("\n\nWARNING: in FindDefect.nearest_neighbors_environment() more than "
            "two sets of atoms were found. Cluster delimited by "
            "`minima`= ", minima, ', `maxima=`', maxima)
      print('Only elements with environments less abundant than ', lower_min,
            ' are regarded as defects')
    
    defects = []
    # detecting what atoms are defects
    # nn_elem is ['CCC', 'CC' CCH, 'CCH', ...]
    for i in range(len(nn_elem)):
      environment = nn_elem[i]
      if uniques[environment] < lower_min:
        defects.append(i)

    if self.verbose:
      print('list of defects: ')
      print([(i,self.p.elm[i]) for i in defects])
    self.defects['nearest_neighbors_environment'] = defects
    self._set_all_defects()
    return defects

  def write_defects(self, method='any', filename='defects.vasp'):
    """
    Writes a POSCAR file with the defects marked as dummy atoms
    
    `method` can be:
    'find_forgein_atoms' -> see self.find_forgein_atoms()
    'nearest_neighbors_environment' -> see self.nearest_neighbors_environment()
    'any', any method will do

    """
    if method == 'any':
      indexes = self.all_defects
    else:
      indexes = self.defects[method]

    N = len(indexes)
    newElements = ['D']*N
    
    newP = poscarUtils.poscar_modify(self.p, verbose=False)
    newP.change_elements(indexes=indexes, newElements=newElements)
    newP.write(filename=filename)
    # print(indexes)
    
