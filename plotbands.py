#!/usr/bin/env python3

import poscar
#import latticeUtils
import defects
#import pyprocar
import os
ORB_Dict  = {"s" :  [0], "p":[1,2,3], "d":[4,5,6,7,8], "f":[9,10,11,12,13,14,15]}
#Need default value for elimit
elimit = [-2,2]
mode_ = "parametric"


def plot(orbitals, POSCAR = "POSCAR", PROCAR = "PROCAR",OUTCAR = "OUTCAR", savefigure = "Band_plot"):
    """ Writes a script that uses pyprocar.bansplot() to plot the bands from a PROCAR and OUTCAR file
        for defect atoms from a given POSCAR file

        -Can select orbitals to plot
        -Can select a file to save the figure plotted
    """
    #Get list of defects for atoms
    file = open("plot_file.py", "w")
    file.write("#!/usr/bin/env python3 \n")
    file.write("import pyprocar \n")
    file.write("##Asumed default values are \n")
    file.write("#Energy limit values \n")
    file.write("elimit = [-2,2] \n")
    file.write("#Mode of ploting for bands, if the orbitals are not degenerate might want to change to 'plain' \n")
    file.write("mode = 'parametric' \n")
    file.write("#Orbital dictionary used \n")
    file.write("ORB_Dict  = {'s' :  [0], 'p':[1,2,3], 'd':[4,5,6,7,8], 'f':[9,10,11,12,13,14,15]}\n")
    file.write("#POSCAR,PROCAR, OUTCAR, and Ploted figure files \n")
    file.write("POSCAR = '"+POSCAR+"'\n")
    file.write("PROCAR = '"+PROCAR+"'\n")
    file.write("OUTCAR = '"+OUTCAR+"'\n")
    file.write("savefigure = '"+savefigure+"'\n")



    
    POSCAR_ = poscar.Poscar(POSCAR)
    POSCAR_.parse()
    Defects = defects.FindDefect(POSCAR_)
    atoms  = Defects.all_defects
    line = "#The defects found on "+POSCAR+" were \n"
    file.write(line)
    file.write("atoms = [".rstrip("\n"))
    file.write(str(atoms[0]).rstrip("\n"))
    for i in atoms[1:]:
        file.write(",".rstrip("\n"))
        file.write(str(i).rstrip("\n"))
    file.write("] \n")


    asked_orb = []
    #Dictionary of orbitals
    for i in orbitals:
        asked_orb += ORB_Dict[i]
    file.write("#Orbitals used for this plot\n")
    file.write("orbitals = [".rstrip("\n"))
    file.write(str(asked_orb[0]).rstrip("\n"))
    if(asked_orb[1:]):
        for i in asked_orb[1:]:
            file.write(",".rstrip("\n"))
            file.write(str(i).rstrip("\n"))
    file.write("] \n")
    file.write("#We then plot the bands specified \n")
    file.write("pyprocar.bandsplot(PROCAR,outcar = OUTCAR,elimit = elimit,mode = mode,savefig = savefigure,atoms = atoms,orbitals = orbitals)")
    file.close()
    os.system("chmod +rwx plot_file.py")
    
    #pyprocar.bandsplot(PROCAR,outcar = outcar, elimit = elimit, mode = mode_,savefig = savefigure ,atoms = atoms, orbitals = asked_orb)

if __name__ == '__main__':
    plot(orbitals='s', POSCAR='POSCAR')
