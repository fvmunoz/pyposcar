#!/usr/bin/env python

import argparse
import numpy as np
from poscar import Poscar

class poscar_modify:
  """ class to change properties of a Poscar-object.
      It requires a poscar-object, not a filename.

  Methods:

  write(filename, cartesian, xyz)   # write the poscar with `filename`, in `cartesian`?
  pos_multiply(factor, cartesian)   # multiply the position of each atoms by `factor`
  pos_sum(factor, cartesian)        # sums `factor` to each position
  remove(self, atoms, human)        # removes a list of `atoms`
  add(element, position, cartesian) # add a single atom with  `element` at `position`
  shift(amount, cartesian)          # shift all the positions by `amount`
  scale_lattice(factor, cartesian)  # scale the lattice by `factor`. are `cartesian` fixed?

  """
  def __init__(self, poscar, verbose=False):
    self.p = poscar
    self.verbose = verbose

  def write(self, filename, cartesian=False, xyz=False):
    """It just invokes the write method from the poscar. Put here just
    for convenience

    filename: the name of the file to be written
    cartesian: write in cartesian or direct coordinates
    xyz: should a xyz be written too?

    """
    direct = True
    if cartesian:
      direct=False
    self.p.write(filename, direct=direct)
    if xyz:
      self.p.xyz(filename + '.xyz')

    if self.verbose:
      print("new POSCAR:")
      print(self.p.poscar)
      if xyz:
        print('XYZ file written')
    
  def pos_multiply(self, factor, cartesian=True):
    """ Multiplies each (x,y,z) position by the Factor (Fx,Fy,Fz)
    args:

    factor: a list or array with 3 numbers
    cartesian: should the operation be done in Cartesian or direct coordinates
    
    """
    factor = np.array(factor, dtype=float)
    if verbose:
      print("Multiply positions, factor = ", factor)
      print("old positions:")
      if cartesian:
        print(self.p.cpos)
      else:
        print(self.p.dpos)
        
    if cartesian is True:
      self.p.cpos = self.p.cpos*factor
      self.p._set_direct()
    else:
      self.p.dpos = self.p.dpos*factor
      self.p._set_cartesian()

    if verbose:
      print("\nnew positions:")
      if cartesian:
        print(self.p.cpos)
      else:
        print(self.p.dpos)      
    return

  def pos_sum(self, factor, cartesian=True):
    """ Add each (x,y,z) position by the Factor (Fx,Fy,Fz)
    args:

    factor: a list or array with 3 numbers
    cartesian: should the operation be done in Cartesian or direct coordinates
    
    """
    factor = np.array(factor, dtype=float)
    
    if verbose:
      print("summing to positions, factor = ", factor)
      print("old positions:")
      if cartesian:
        print(self.p.cpos)
      else:
        print(self.p.dpos)

    if cartesian is True:
      self.p.cpos = self.p.cpos + factor
      self.p._set_direct()
    else:
      self.p.dpos = self.p.dpos + factor
      self.p._set_cartesian()

    if verbose:
      print("\nnew positions:")
      if cartesian:
        print(self.p.cpos)
      else:
        print(self.p.dpos)      
    return
  
  
  def remove(self, atoms, human=False):
    """Removes a list of atoms from the Poscar object. The order of
    remotion is not trivial, but the method (at the Poscar-class
    level) sort it before removing the atoms.
    
    args:
    
    atoms: a list with the indexes of the atoms
    human: does `atoms` start from 1 (True) or 0 (False)?
    """
    atoms = np.array(atoms)
    # the atoms list could be disordered, Poscar.remove is safe
    if human:
      atoms = atoms - 1
    if self.verbose:
      print('removing the following atoms (0-based indexes):', atoms)
      self.p.remove(atoms)

  def add(self, element, position, cartesian=True):
    """Removes a list of atoms from the Poscar object. The order of
    remotion is not trivial, but the method (at the Poscar-class
    level) sort it before removing the atoms.
    
    args:
    
    element: a string with the atomic specie, e.g. 'Cu'
    position: [X, Y, Z]
    cartesian: Cartesian (True) or direct coordiantes (False)?
    """
    position = np.array(position, dtype=float)
    if self.verbose:
      print('New atom:', element, position)
    direct = True
    if cartesian is True:
      direct = False
    self.p.add(position=position, element=element, direct=direct)

  def shift(self, amount, cartesian):
    """Shift all the positions by `amount`, given in cartesian or direct
    coordinates. The PBCs are always enforced (i.e. [0,1] in direct
    coords)

    args:
    amount: [X,Y,Z] a list or array with the shift along each basios vector
    cartesian: is `amount` given in cartesian (True) or direct (False) coords?

    """
    amount = np.array(amount, dtype=float)
    if cartesian:
      if self.verbose:
        print('\nOriginal Cartesian coords:')
        print(p.cpos)
      self.p.cpos = self.p.cpos + amount
      self.p._set_direct()
      if self.verbose:
        print('\nShifted Cartesian coords:')
        print(p.cpos)        
    else:
      if self.verbose:
        print('\nOriginal Direct coords:')
        print(p.dpos)      
      self.p.dpos = self.p.dpos + amount
      self.p._set_cartesian()
      if self.verbose:
        print('\nShifted Cartesian coords:')
        print(p.cpos)        

    # enforcing the PBCs
    self.p.dpos = np.mod(self.p.dpos, 1.0)
    self.p._set_cartesian()
    return

  def scale_lattice(self, factor, cartesian):
    """ Scale the lattice vectors by factor [a,b,c] 

    args:

    factor: [A,B,C] the first lattice vector is multiplied by A, etc.
    cartesian: What cooddinates should remain constant? Cartesian or direct?
    """
    if self.verbose:
      print("Old lattice")
      print(self.p.lat)

    self.p.lat = (self.p.lat.T * factor).T
    if self.verbose:
      print("New lattice")
      print(self.p.lat)

    if cartesian:
      # if cartesian positions are to remain constant, the direct ones
      # needs to be updated
      self.p._set_direct()
    else:
      self.p._set_cartesian()
    return

  


  
def p_atoms_f(args):
  print('Operations related with atomic positions')
  if args.verbose:
    print('Input:     ', args.input)
    print('Output:    ', args.output)
    print('sum:       ', args.sum)
    print('multiply:  ', args.multiply)
    print('xyz:       ', args.xyz)
    print('cartesian: ', args.cart)
    print('save_cart: ', args.sc)
    print('remove:    ', args.remove)
    print('human:     ', args.human)
    print('add:       ', args.add)

  p = Poscar(args.input, verbose=False)
  p.parse()

  Modifier = poscar_modify_atoms(p, verbose=args.verbose)
  
  # first dealing with the maths
  if args.multiply:
    Modifier.pos_multiply(factor, cartesian=args.cart)
      
  if args.sum:
    Modifier.pos_sum(factor, cartesian=args.cart)


  if args.remove:
    Modifier.remove(args.remove, human=args.human)

  if args.add:
    # parsing the string: 'C 1.2 4 -5.0'
    # args.add = args.add.split()
    element = args.add[0]
    position = args.add[1:]
    if len(position) != 3:
      raise RuntimeError("the --add parameter has a wrong format, " +  args.add)
    position = np.array(position, dtype=float)
    Modifier.add(element=element, position=position, cartesian=args.cartesian)

  # Now we are done with all modifications  

  Modifier.write(args.output, cartesian=args.sc, xyz=args.xyz)
  return

def p_pbc_f(args):
  print('PBC-related utilities')
  if args.verbose:
    print('Input:     ', args.input)
    print('Output:    ', args.output)
    print('shift:     ', args.shift)
    print('xyz:       ', args.xyz)
    print('cartesian: ', args.cart)
    print('save_cart: ', args.sc)

  p = Poscar(args.input, verbose=False)
  p.parse()

  Modifier = poscar_modify(p, verbose=args.verbose)
    
  if args.shift:
    Modifier.shift(args.shift, args.cart)
  Modifier.write(args.output, cartesian=args.sc, xyz=args.xyz)

  return
    
def p_lattice_f(args):
  print('Lattice stuff')
  if args.verbose:
    print('Input:     ', args.input)
    print('Output:    ', args.output)
    print('scale:     ', args.scale)
    print('factor:    ', args.factor)
    print('xyz:       ', args.xyz)
    print('cartesian: ', args.cart)
    print('save_cart: ', args.sc)

  p = Poscar(args.input, verbose=False)
  p.parse()

  Modifier = poscar_modify_PBC(p, verbose=args.verbose)
  
  # first dealing with the factors, if any
  if args.factor == None:
    args.factor = 1.0
  if args.scale == None:
    scale = np.array([1.0, 1.0, 1.0])
  
  factor = factor*scale
  # Now changing the lattice vectors
  Modifier.scale_lattice(factor=factor, cartesian=args.cart)
  # and writing
  Modifier.write(args.output, cartesian=args.sc, xyz=args.xyz)      
  return

def p_scell_f(args):
  print('Supercell creation')
  if args.verbose:
    print('Input:     ', args.input)
    print('Output:    ', args.output)
    print('b1:        ', args.b1)
    print('b2:        ', args.b2)
    print('b3:        ', args.b3)
    print('xyz:       ', args.xyz)
    print('save_cart: ', args.sc)

  p = Poscar(args.input)
  p.parse()
  lat = p.lat
  pos = p.dpos
  elem = p.elm
  scell = np.array([args.b1, args.b2, args.b3])
  if args.verbose:
    print("original lattice:\n", lat, "\n")
    print("New lattice (in terms of the original vectors)\n", scell, "\n")
    print("Cartesian coordinates new lattice:\n", np.dot(scell, lat))

  # inverse: a=ocell*b
  ocell = np.linalg.inv(scell)
  if args.verbose:
    print( "inverse transformation:\n", ocell)
    print( "atoms, direct\n", pos)
    print( "atoms in cart\n")
    print(  np.einsum('ij,jk', pos, lat))

    print( "in terms of new lattice\n")
  spos = np.einsum('ij,jk', pos, ocell)

  # I need to find the values of n_i, a_i *inside* the supercell.
  # n_i*a_i = n_i*ocell_ij*b_j
  # then, the condition is : 0 < n_i*ocell_ij < 1
  b = np.ones(3)
  n = np.einsum('j,ji', b, scell )
  n = int(np.max(np.abs(n)))
  if args.verbose:
    print( "maximum value of n to search for repetitions : ", n)

  n = np.arange(-n,n)

  n = np.array([(x,y,z) for z in n for y in n for x in n])
  nuseful = []
  #checking which of the previous repetitions works
  for trial in n:
    value = np.einsum('i,ij', trial, ocell)
    if value.min() >= 0 and value.max() < 1:
      nuseful.append(trial)
  if args.verbose:
    print( "set of new coords\n", nuseful)
  npos = []
  for nn in nuseful:
    npos.append(spos + np.einsum('i,ij', nn, ocell))
  if args.verbose:
    print( "positions:")
  npos = np.concatenate(npos)
  npos = np.mod(npos, 1)
  if args.verbose:
    print( npos, npos.shape)

  # I can have repeated elements, such as '0 0 1', and '0 0 0'
  # (the 1 can be 0.9999999 and fail the previous filter)
  tol = 0.001
  temp = []
  for i in range(len(npos)):
    repeated = False
    for j in range(i):
      d = np.abs(npos[i] - npos[j])
      for k in range(len(d)):
        if abs(d[k]-1) < d[k]:
          d[k]=d[k]-1
      #print d
      if np.linalg.norm(d) < tol and i != j:
        repeated = True
        if args.verbose:
          print( i, j, npos[i], npos[j])
    if not repeated:
      temp.append(npos[i])
  temp = np.concatenate(temp)
  temp.shape = (-1,3)
  if args.verbose:
    print( temp.shape)
  npos = temp[:]
  
  elem = elem*len(nuseful)
  #print elem
  p.elm = elem
  p.lat = np.dot(scell, lat)
  p.dpos = npos
  p._set_cartesian()

  p.sort()

  # Finally, writing the files
  if args.sc:
    p.write(args.output, direct=False)
  else:
    p.write(args.output, direct=True)
  if args.verbose:
    print("new POSCAR:")
    print(p.poscar)
  if args.xyz:
    p.xyz(args.output + '.xyz')
    if args.verbose:
      print('XYZ file written: ', args.output + '.xyz')
        
  return

def p_cat_f(args):
  print('Concatenation')
  if args.verbose:
    print('Input(s):  ', args.input)
    print('Output:    ', args.output)
    print('xyz:       ', args.xyz)
    print('save_cart: ', args.sc)

  # I will apend the other POSCAR to the first one
  first = args.input.pop(0)
  p1 = Poscar(first)
  p1.parse()
  if args.verbose:
    print('file', first, 'loaded.', p1.Ntotal, 'atoms')
  for filename in args.input:
    p = Poscar(filename)
    p.parse()
    if args.verbose:
      print('file', filename, 'loaded.', p.Ntotal, 'atoms')
    # adding the new atoms one by one
    for i in range(p.Ntotal):
      pos = p.dpos[i]
      elem = p.elm[i]
      direct = True
      selectiveFlags = None
      if p.selective:
        selectiveFlags = p.selectFlags[i]
      p1.add(position=pos, element=elem, direct=direct, selectiveFlags=selectiveFlags)
      print(p1.Ntotal)
  # Once all atoms have been added, I need to sort them
  p1.sort()

  # Finally, writing the file(s)
  if args.sc:
    p1.write(args.output, direct=False)
  else:
    p1.write(args.output, direct=True)
  if args.verbose:
    print("new POSCAR:")
    print(p1.poscar)
  if args.xyz:
    p1.xyz(args.output + '.xyz')
    if args.verbose:
      print('XYZ file written: ', args.output + '.xyz')
        
  return

  



  

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Utilities related to poscar.')
  subparsers = parser.add_subparsers(help='sub-command')
  
    
  # defining subparsers
  p_atoms = subparsers.add_parser('atoms', help='operations related with '
                                  'atomic positions, leaving the lattice unchanged')
  p_atoms.set_defaults(func=p_atoms_f)
  
  p_pbc = subparsers.add_parser('pbc', help='boundaries-related operations. It always'
                                ' applies PCBs at the atomic positions. ')
  p_pbc.set_defaults(func=p_pbc_f)
  
  p_lattice = subparsers.add_parser('lattice', help='lattice-related operations. '
                                    'The positions may/may not be modified with the '
                                    'lattice')
  p_lattice.set_defaults(func=p_lattice_f)
  
  p_scell = subparsers.add_parser('supercell', help='Creates a supercell')
  p_scell.set_defaults(func=p_scell_f)

  p_cat = subparsers.add_parser('cat', help='concatenates two or more POSCAR files.'
                                ' This must make sense (user!!!), for instance joining'
                                ' two layer of graphene to create BLG. You might need '
                                'to translate the positions of one layer beforehand')
  p_cat.set_defaults(func=p_cat_f)
  
  
  # filing the subparser options
  p_atoms.add_argument('input', type=str, help='Input POSCAR file ')
  p_atoms.add_argument('output', type=str, help='Output POSCAR file')
  p_atoms.add_argument('-s', '--sum', type=float, nargs=3, help='Sum (adds) [X Y Z] to each '
                       'position. This is in Direct coordinates by default, see `--cart`.' 
                       ' The PBC are NOT taken in to account, i.e. [0.5 0.5 0.5] + '
                       '[0.0 0.0 0.7] = [0.5 0.5 1.2]. Multiplication precedes addition.'
                       ' Nevertheless it is recommended to separate the operation in '
                       'different calls')

  p_atoms.add_argument('-m', '--multiply', type=float, nargs=3, help='Multiplies [X Y Z]'
                       ' element-wise each postion. This is in Direct coords by default,'
                       ' see `--cart`. PBC are not taken into account, i.e. [0.1 0.2 0.7]'
                       ' * [0.5 1.0 2.0] = [0.05 0.2 1.4]. Multiplication precedes addition.'
                       ' Nevertheless it is recommended to separate the operation in '
                       'different calls')
  
  p_atoms.add_argument('--xyz', action='store_true', help='writes an xyz file')
  
  p_atoms.add_argument('-c', '--cart', action='store_true', help='set to perform the '
                       'operations in the cartesian positions. By default Direct coords'
                       ' are used' )
  p_atoms.add_argument('--sc', action='store_true', help='set to save the file in '
                          'Cartesian. By default Direct coords are used, even if the '
                       'operations are  done in cartesians')
  p_atoms.add_argument('-v', '--verbose', action='store_true')
  p_atoms.add_argument('--remove', '-r', nargs='+', type=int, help='removes the atoms'
                       ' with the given indexes. They indexes start from 0, unless you'
                       ' set `--human`')
  p_atoms.add_argument('--human', '-u', action='store_true', help='All the indexes '
                       'from the input are put in `human` format, starting from 1 (i.e'
                       '.: the first atom is 1, and so on)')
  p_atoms.add_argument('--add', '-a', nargs=4, type=str, help='`--add C 0.5 0.3 0.1`,'
                       ' adds an C atom at the given direct coordinate. The coordinates'
                       ' can be direct (default) or Cartesian, see `--cart`')
  # p_atoms.add_argument('--duplicates', action='store_true', help="removes the duplicate "
  #                      "atoms, i.e. Those that are almost in the same position. Mind the"
  #                      "program will keep only the first occurrence. See `duplicate_tol`")
  # p_atoms.add_argument('--duplicate_tol', type=float, default=0.1, help='Tolerance '
  #                      'critetion for setting an atom as `duplicate`')
  
  #########
  
  p_pbc.add_argument('input', type=str, help='input file')
  p_pbc.add_argument('output', type=str, help='output file')
  # p_pbc.add_argument('-p', '--pbc', action='store_true', help='it actually imposes'
  #                    ' PBCs, by moving all the atoms into the [0, 1) interval. ')
  p_pbc.add_argument('-s', '--shift', type=float, nargs=3, help='it adds [X, Y ,Z] '
                     'to each coordinate, and then applies PBCs. see `--cart`, `--sc`')
  p_pbc.add_argument('--cart', action='store_true', help='The shift is given and made'
                     ' in Cartesian coords. ')
  p_pbc.add_argument('--sc', action='store_true', help='sets the output POSCAR file in'
                     ' cartesian coords. The default is direct')
  p_pbc.add_argument('--xyz', action='store_true', help='also saves a XYZ file')
  p_pbc.add_argument('-v', '--verbose', action='store_true')
    
  #########
  
  p_lattice.add_argument('input', type=str, help='Input POSCAR file ')
  p_lattice.add_argument('output', type=str, help='Output POSCAR file')
  p_lattice.add_argument('-s', '--scale', type=float, nargs=3, help='multiplies each '
                         'lattice vector by the [X Y Z] factor. The positions may/may '
                         'not be affeted. See `cart`')
  p_lattice.add_argument('-f', '--factor', type=float, default=1.0,
                         help='multiplies all the lattice'
                         ' by the given factor. The position may/may not be affected, '
                         'see `--cart`')
  p_lattice.add_argument('-c', '--cart', action='store_true', help='The positions are'
                           ' keep fixed in cartesian coordinates, their value in direct'
                         ' coords change with the lattice. The default is to keep the'
                         ' positions unaltered in direct coords.')
  p_lattice.add_argument('--sc', action='store_true', help='set it to write the output'
                         ' file in cartesian coords. Te default is in direct coords.')
  p_lattice.add_argument('-v', '--verbose', action='store_true')
  p_lattice.add_argument('--xyz', action='store_true', help='also a XYZ file is writtem')
  # p.lattice.add_argument('-r', '--rotate')
  
  ##########
  
  p_scell.add_argument('input', type=str, help='input file')
  p_scell.add_argument('output', type=str, help='output file')
  
  p_scell.add_argument("--b1", nargs=3, type=int, default=[1,0,0],
                       help="first supercell vector, eg '1 2 -1'" )
  p_scell.add_argument("--b2", nargs=3, type=int, default=[0,1,0],
                       help="first supercell vector, eg '1 1 1'" )
  p_scell.add_argument("--b3", nargs=3, type=int, default=[0,0,1],
                       help="first supercell vector, eg '0 0 10'" )
  p_scell.add_argument("--xyz", action="store_true")
  p_scell.add_argument('--sc', action='store_true', help='set it to write the output'
                       ' file in cartesian coords. The default is in direct coords.')
  p_scell.add_argument('-v', '--verbose', action='store_true')

  #########################################

  p_cat.add_argument('input', type=str, nargs='+', help='POSCAR files to concatenate. '
                     'The user must control the physics')
  p_cat.add_argument('output', type=str, help='Output file')
  p_cat.add_argument('-v', '--verbose', action='store_true')
  p_cat.add_argument('--xyz', action='store_true')
  p_cat.add_argument('--sc', action='store_true')

  
  

  args = parser.parse_args()

  # there is a python 3 bug. If no argument provided an exception is raised
  #try:
  args.func(args)
  #except AttributeError:
  #  parser.error("too few arguments")
