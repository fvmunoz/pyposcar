#!/usr/bin/env python3
import poscarUtils
import poscar
import os

print("Testing the identification of defects")
POSCAR = ["POSCAR-7-9-B.vasp","POSCAR-7-9.vasp" , "POSCAR-C3Si.vasp",  "POSCAR-C4.vasp" ,  "POSCAR-C6H.vasp",   "POSCAR-C6.vasp",   "POSCAR-nv.vasp" ,"POSCAR-SiV.vasp",   "POSCAR-V2.vasp"]
for i in POSCAR:
    #Runing analize.py
    print(i)
    cmd_1  = "./analize.py "+" ./test/"+i+" >> ./test/temp"
    os.system(cmd_1)
    defect_string = "test/"+i+"_defect.vasp"
    cluster_string = "test/"+i+"_cluster.vasp"
    cmd_2 = "mv "+ "./"+defect_string +" "+ "./"+ cluster_string + " ./test/aux"
    os.system(cmd_2)
    path_defect_aux = "./test/aux/"+i+"_defect.vasp"
    path_defect_results = "./test/results/"+i+"_defect.vasp"
    path_cluster_aux = "./test/aux/"+i+"_cluster.vasp"
    path_cluster_results = "./test/results/"+i+"_cluster.vasp"
    poscar_defect_1 = poscar.Poscar(path_defect_aux)
    poscar_defect_1.parse()
    poscar_defect_2 = poscar.Poscar(path_defect_results)
    poscar_defect_2.parse()
    poscar_cluster_1 = poscar.Poscar(path_cluster_aux)
    poscar_cluster_1.parse()
    poscar_cluster_2 = poscar.Poscar(path_cluster_results)
    poscar_cluster_2.parse()
    if(poscarUtils.poscarDiff(poscar_defect_1,poscar_defect_2)):
        print(poscarUtils.poscarDiff(poscar_defect_1,poscar_defect_2))
    else:
        continue
    if(poscarUtils.poscarDiff(poscar_cluster_1,poscar_cluster_2)):
        print(poscarUtils.poscarDiff(poscar_cluster_1,poscar_cluster_2))
    else:
        continue 
    





