""" 
Defect-related utilities

class
FindDefect
- It tries to identify any defect by statistical means    


"""
import latticeUtils
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
  def __init__(self, poscar, verbose=True):
    self.p = poscar
    self.verbose = verbose
    self.defects = {} # all the defects from the different methods
                      # should be here
    self.neighbors = latticeUtils.Neighbors(self.p, verbose=False)
    self.find_forgein_atoms()
    self.nearest_neighbors_size()
    return

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
    # print(scores)
    #
    # The local minima of the scores denotes the groups. argrelextrema
    # returns a tuple, only first entry is useful
    minima = argrelextrema(scores, np.less)[0] 
    maxima = argrelextrema(scores, np.greater)[0]
    if self.verbose:
      print('local max:',maxima,'  localmin:', minima)
    if len(maxima) < len(minima):
      print('Maxima, ', maxima)
      print('Minima, ', minima)
      raise RuntimeError('FindDefect.find_forgein_atoms error: '
                         'the local min/max doesnt follows '
                         'the expected order')
    # The threshlod to determine if an atom is forgein. 
    lower_min = minima[0]
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
    return defects
    # plt.plot(samples, scores) # plt.show()
    
  def nearest_neighbors_size(self):
    # self.verbose = True
    nn_list = self.neighbors.nn_list
    coordination = [len(x) for x in nn_list]
    unique, counts = np.unique(coordination, return_counts=True)
    if self.verbose:
      print('\ndefetcs.FindDefect.nearest_neighbors_size()')
      print('neareast neighbors list')
      print(nn_list)
      print('coordination')
      print(coordination)
      print('Statistics of coordination: unique, counts')
      print(list(zip(unique, counts)))
