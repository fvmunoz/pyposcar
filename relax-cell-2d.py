#!/usr/bin/env python3

import poscarUtils
import poscar
import os
import argparse
import re
import numpy as np

def get_data():
  """Getting the information from two sources:
  1) The 'OPT_SUM' file, if it exists it has the energies and lattice
  data of previous iterations

  2) The 'OUTCAR' file, it is useful to guess a first step if there
  is no enough data to fit a parabola
  
  The OPT_SUM file will be updated (and created if needed).
  This file contains:

  lat_a lat_b angle_ab energy stress_a stress_b stress_theta
  
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
  stress_AB = (stress_A + stress_B)/2
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
  
  
  # updating and perhaps creating a file with energies
  line = ''
  line += str(length_a) + ' '
  line += str(length_b) + ' '
  line += str(angle_ab) + ' '
  line += str(energy) + ' '
  line += str(stress_A) + ' '
  line += str(stress_B) + ' '
  line += str(stress_theta) + '\n'
  
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
  return history

def make_prediction(opt_type, history, maxStep=0.01):
  """
  `opt_type`: a dict of the form
  {'a':Bool, 'b':Bool, 'ab':Bool, 'theta':Bool}
  where Bool={True, False}. It indicates what is going to be optimized

  `history` is an array with the form:
  [[lat_a lat_b angle_ab energy stress_a stress_b stress_theta],
   [...],
   [...]]
  
  maxStep: relative maximum change, 0.01 is 1%

  """
  print('\n\nStarting prediction:\n')
  # preparing a lookup table to iterate easily
  stress = {'a':history[:,4],
            'b':history[:,5],
            'theta':history[:,6]}
  stress['ab'] = (stress['a'] + stress['b'])/2
  # a dict with the factors to be changed
  factors = {'a':1, 'b':1, 'ab':1, 'theta':1}
  # with one or two data points, there is nothing to interpolate. Just
  # moving a little bit from the lowest energy point
  if len(history) < 3:
    for opt_t in ['a', 'b', 'ab', 'theta']:
      if opt_type[opt_t]:
        print('Dealing with the following type of stress:', opt_t)
        energies = history[:,3]
        i_min = np.argmin(energies)
        stress_i_min = stress[opt_t][i_min]
        print('minimum Energy iteration', i_min, ', stress', stress_i_min)
        if stress_i_min < 0:
          factors[opt_t] = 1 - maxStep
        else:
          factors[opt_t] = 1 + maxStep
  # if I have enough data, they will be fitted together
  else:
    if opt_type['ab'] == True and opt_type['theta'] == False:
      pass
    else:
      raise RuntimeError('Not implemented')
    
  if factors['ab'] != 1:
    factors['a'] = factors['ab']
    factors['b'] = factors['ab']
  factor = [factors['a'], factors['b'], 1.0]
  print('new factors', factors['a'], factors['b'])

  p = poscar.Poscar('POSCAR')
  p.parse()
  new_p = poscarUtils.poscar_modify(p)
  new_p.scale_lattice(factor, cartesian=False)
  new_p.write('POSCAR-NEW')
          
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
  
  history = get_data()
  make_prediction(opt_type=opt_type, history=history)
  
  
  # I will create a list with results
  

