#!/usr/bin/env python

import poscar
import latticeUtils
import defects
import argparse



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("inputfile", type=str, help="input file")
  parser.add_argument('-v', '--verbose', action='store_true')
  
  args = parser.parse_args()
  
  p = poscar.Poscar(args.inputfile, verbose=args.verbose)
  p.parse()

  Defects = defects.FindDefect(poscar=p, verbose=args.verbose)
  print(Defects.defects)
