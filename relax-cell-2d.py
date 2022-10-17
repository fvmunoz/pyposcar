#!/usr/bin/env python3

import poscarUtils
import poscar
import os
import argparse
import re
import numpy as np

def get_data(opt_type={'a':False, 'b':False, 'ab':True, 'theta':False}):
  """Getting the information from two sources:
  1) The 'OPT_SUM' file, if it exists it has the energies and lattice
  data of previous iterations

  2) The 'OUTCAR' file, it is useful to guess a first step if there
  is no enough data to fit a parabola
  
  The OPT_SUM file will be updated (and created if needed).

  args:

  `opt_type` what is going to be optimized

  """

  if not os.path.isfile('OUTCAR'):
    raise RuntimeError('File OUTCAR does not exist')
  outcar = open('OUTCAR', 'r').read()
  energy = re.findall(r'energy without entropy =\s*([-.\d]+)', outcar)
  energy = float(energy[-1])
  print('energy, ', energy)

  stress = re.findall(r'Total[-.\s\d]+\s*in kB', outcar)
  stress = stress[-1].split()
  stress_A = float(stress[1])
  stress_B = float(stress[2])
  stress_theta = float(stress[4])
  print('stress A,', stress_A)
  print('stress B,', stress_B)
  print('stress theta,', stress_theta)

  # locating the parameters
  vectors = re.findall(r'reciprocal lattice vectors[-.\d\s]*', outcar)
  vectors = vectors[-1].split()
  vec_a = np.array(vectors[3:6], dtype=float)
  vec_b = np.array(vectors[9:12], dtype=float)
  print('2D lattice, ', vec_a, vec_b)
  length_a = np.linalg.norm(vec_a)
  length_b = np.linalg.norm(vec_b)
  print('length A, ', length_a)
  print('length B, ', length_b)
  angle_ab = np.arccos(np.dot(vec_a, vec_b)/length_a/length_b)
  print('angle AB', angle_ab*180/np.pi, '(deg)', ', ', angle_ab, ' (rad)')
  
  
  # updating and prehaps creating a file with energies
  line = ''
  if opt_type['a']:
    line += str(length_a) + ' '
  if opt_type['b']: 
    line += str(length_b) + ' '
  if opt_type['ab']:
    length_ab = (length_a + length_b)/2
    line += str(length_ab) + ' '
  if opt_type['theta']:
    line += str(angle_ab) + ' '
  line += str(energy) + '\n'
  print('New line to OPT_SUM\n',line)
  f_histo = open('OPT_SUM', 'a')
  f_histo.write(line)
  f_histo.close()

  # reading the full history
  history = open('OPT_SUM', 'r').readlines()
  history = list(set(history))
  history = [x.split() for x in history]
  history = np.array(history, dtype=float)
  print('Full history (excluding duplicate points)')
  print(history)

  # passing the relevant info:
  # (full) history
  # stress.
  data = {}
  data['history'] = history
  data['stress_A'] = stress_A
  data['stress_B'] = stress_B
  data['stress_theta'] = stress_theta

  return data

def make_prediction(opt_type, history, stress, maxStep=0.01):
  """
 `history` is ordered, but it only includes the data when they exist.
  The order is 'a', 'b', 'ab', 'theta' 
  These are the valid fileds for `stress` too.
  
  maxStep: relative maximum change, 0.01 is 1%

  """
  print('\n\nStarting prediction:\n')
  # index of current item (field)
  cur_index = 0
  # number of inequivalent data of each item (field)
  nvalues = []
  # I need at least three different values per parameter
  if opt_type['a']:
    values = set(history[:,cur_index])
    print('values of `a`', values)
    nvalues.append(len(values))
    cur_index += 1
  if opt_type['b']:
    values = set(history[:,cur_index])
    print('values of `b`', values)
    nvalues.append(len(values))
    cur_index += 1
  if opt_type['ab']:
    values = set(history[:,cur_index])
    print('values of `ab`', values)
    nvalues.append(len(values))
    cur_index += 1
  if opt_type['theta']:
    values = set(history[:,cur_index])
    print('values of `theta`', values)
    nvalues.append(len(values))
    cur_index += 1

  # if across the least represented paramenter I only have one value,
  # the only option is to do a initial guess, based on the stress.
  #
  # if there are two different data, I could take the value at the
  # middle point
  #
  # With three or more data, I could fit a curve, eventually excluding
  # far away (initial) points

  p = poscar.Poscar('POSCAR')
  p.parse()
  new_p = poscarUtils.poscar_modify(p)

  factor_a = factor_b = factor_theta = 1.0
  if min(nvalues) == 1:
    if opt_type['a']:
      if stress['a'] > 0:
        factor_a = 1 + maxStep/3
      else:
        factor_a = 1 - maxStep/3
    if opt_type['b']:
      if stress['b'] > 0:
        factor_b = 1 + maxStep/3
      else:
        factor_b = 1 - maxStep/3
    if opt_type['ab']:
      if stress['ab'] > 0:
        factor_a = factor_b = 1 + maxStep/3
      else:
        factor_a = factor_b = 1 - maxStep/3
    if opt_type['theta']:
      if stress['theta'] > 0:
        factor_theta = 1 + maxStep/3
      else:
        factor_theta = 1 - maxStep/3
  print('scaling in a, b, theta: ',factor_a, factor_b, factor_theta)
    



  

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='A lattice optimizer for a 2D'
                                    ' lattice. It will look to the old data and'
                                    ' try to fit a parabola (1D or 2D) on it')

  parser.add_argument('--a',  help='optimize the value of the lattice parameter'
                      ' a (length of first lattice vector)', action='store_true')
  parser.add_argument('--b',  help='optimize the value of the lattice parameter'
                      ' b (length of second lattice vector)', action='store_true')
  parser.add_argument('--theta',  help='optimize the value of the angle between '
                      ' both vectors', action='store_true')
  parser.add_argument('--equal', '-e', help='keep the ratio between both lattice'
                      ' parameters constant. By default if nothing given, a,b '
                      'will be optimized keeping the aspect ratio', action='store_true')
  args = parser.parse_args()

  opt_type = {}
  opt_type['a'] = False
  opt_type['b'] = False
  opt_type['ab'] = False
  opt_type['theta'] = False
  # if everything is False, going to scale the cell respecting the proportions
  if args.a==False and args.b==False and args.equal==False and args.theta==False:
    args.equal = True
  if args.a:
    opt_type['a'] = True
  if args.b:
    opt_type['b'] = True
  if args.equal:
    opt_type['a'] = opt_type['b'] = False
    opt_type['ab'] = True
  
  data = get_data(opt_type=opt_type)
  history = data['history']
  stress = {'a':data['stress_A'],
            'b':data['stress_B'],
            'ab':data['stress_theta'],
            'theta':data['stress_theta']}
  make_prediction(opt_type=opt_type, history=history, stress=stress)
  
  
  # I will create a list with results
  

