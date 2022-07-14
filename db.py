import db_covalentBond
import numpy as np

class DB:
  def __init__(self):
    cr = db_covalentBond.covalent_radii
    cr = cr.replace('-', 'nan')
    cr_names = [x.split()[1] for x in cr.split('\n')]
    cr_values = [x.split()[2:] for x in cr.split('\n')]
    # converting the values to an array, in Angstroms
    cr_values = [np.array(x, dtype=float)/100 for x in cr_values]
    self.covalentRadii = dict(zip(cr_names,cr_values))
    # print(self.covalentRadii)
    return
  def estimateBond(self, element1, element2):
    """Estimates the covalent bond by summing the larger covalent radius
    for each atoms
    """
    radii1 = np.nanmax(self.covalentRadii[element1])
    radii2 = np.nanmax(self.covalentRadii[element2])
    return radii1 + radii2
    
    

atomicDB = DB()
