#!/usr/bin/env python

import poscar
import latticeUtils
import defects
import argparse



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("inputfile", type=str, help="input file")
  parser.add_argument('--size', '-n', type=int, help="size in nearest neighbors"
                      " of the cluster to build", default=0)
  parser.add_argument('--smooth', '-s', action='store_true')
  parser.add_argument('-v', '--verbose', action='store_true')
  
  
  args = parser.parse_args()
  
  p = poscar.Poscar(args.inputfile, verbose=False)
  p.parse()

  Defects = defects.FindDefect(poscar=p, verbose=args.verbose)
  print(Defects.defects)

  # going to write a new file to mark the defects
  Defects.write_defects(method='any', filename=args.inputfile+'_defect.vasp')

  import clusters
  cluster = clusters.Clusters(p, verbose=args.verbose,
                              neighbors=Defects.neighbors,
                              marked=Defects.all_defects)

  cluster.extend_clusters(args.size)
  # cluster.smooth_edges()
  cluster.write(args.inputfile+'_cluster.vasp')
  # cluster.hydrogenate(args.inputfile+'_cluster.vasp')

