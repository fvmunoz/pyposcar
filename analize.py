#!/usr/bin/env python

import poscar
import latticeUtils
import defects
import argparse
import clusters


def create_cluster(filename, smooth=True, extend=0, hydrogenate=True):
  p = poscar.Poscar(args.inputfile, verbose=False)
  p.parse()

  Defects = defects.FindDefect(poscar=p, verbose=args.verbose)
  # going to write a new file to mark the defects
  Defects.write_defects(method='any', filename=args.inputfile+'_defect.vasp')

  cluster = clusters.Clusters(p, verbose=args.verbose,
                              neighbors=Defects.neighbors,
                              marked=Defects.all_defects)

  cluster.extend_clusters(args.size)
  if args.smooth:
    cluster.smooth_edges()

  if args.hydrogenate:
    cluster.hydrogenate(args.inputfile+'_cluster.vasp')
  else:
    cluster.write(args.inputfile+'_cluster.vasp')


def pyprocarLine(filename, smooth=False, extend=args.extend, ignoreH=False):
  
  
  pass    

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("inputfile", type=str, help="input file")
  parser.add_argument('--size', '-n', type=int, help="size in nearest neighbors"
                      " of the cluster to build", default=0)
  parser.add_argument('--smooth', '-s', action='store_true', help='remove dangling bonds')
  parser.add_argument('--hydrogenate', '-y', action='store_true', help='hydrogenate unsaturated bonds')
  parser.add_argument('--ignore_hydrogen', '-i', action='store_true', help='Ignores H atoms. Not used'
                      ' for create a cluster, but sometimes useful for `pyprocar`')
  parser.add_argument('-v', '--verbose', action='store_true')

  parser.add_argument('--pyprocar', '-p', action='store_true', help='just prints a line for pyprocar')
  
  args = parser.parse_args()


  if args.pyprocar:
    pyprocarLine(filename=args.inputfile, smooth=args.smooth,
                 extend=args.size, ignoreH=args.ignore_hydrogen)
  else:
    create_cluster(filename=args.inputfile, smooth=args.smooth,
                   extend=args.size, hydrogenate=args.hydrogenate)
  
  
