#!/usr/bin/env python3
import re 
import poscar
import argparse
import defects
import os

ORB_Dict  = {"s" :  [0], "p":[1,2,3], "d":[4,5,6,7,8], "f":[9,10,11,12,13,14,15]}
#Need default value for elimit
elimit = [-2,2]
mode_ = "parametric"

###CLASSIFY
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
    #If no defects were found, default to use all atoms instead
    if(atoms == []):
        print("No defects were found on ", POSCAR)
        atoms = range(POSCAR_.Ntotal)
    line = "#The defects found on "+POSCAR+" were \n"
    file.write(line)
    file.write("atoms = [".rstrip("\n"))
    file.write(str(atoms[0]).rstrip("\n"))
    for i in atoms[1:]:
        file.write(",".rstrip("\n"))
        file.write(str(i).rstrip("\n"))
    file.write("] \n")


    asked_orb = []
    #Picking and writing Orbitals
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

    #Checking OUTCAR for SPIN and Kpoint information
    out = open(OUTCAR ,"r")
    out = out.readlines()
    if(out):
        match_KPOINTS = [re.findall(r'NKPTS\s*=\s*(\d*)', line) for line in out]
        match_SPIN = [re.findall(r'ISPIN\s*=\s*(\d*)', line) for line in out]
        KPOINTS = int([x for x in match_KPOINTS if(x)][0][0])
        ISPIN = int([x for x in match_SPIN if(x)][0][0])
        if(ISPIN == 2):
            file.write("cmap = 'seismic'\n")
            file.write("vmax = 1.0\n")
            file.write("vmin = -1.0\n")
        else:
            file.write("cmap = 'jet'\n")
            file.write("vmax = None\n")
            file.write("vmin = None\n")            
        if(KPOINTS != 1):
            file.write("mode = 'parametric'\n")
        else:
            file.write("mode = 'atomic'\n")
    else:
        print("Couldn't find OUTCAR file, assuming default mode and cmap")
        file.write("cmap = 'jet'\n")
        file.write("mode = 'parametric'\n")

    file.write("#We then plot the bands specified \n")
    file.write("pyprocar.bandsplot(PROCAR,outcar = OUTCAR,elimit = elimit,mode = mode,savefig = savefigure,atoms = atoms,orbitals = orbitals, cmap = cmap, vmax = vmax, vmin = vmin)")
    file.close()
    os.system("chmod +rwx plot_file.py") 
    #pyprocar.bandsplot(PROCAR,outcar = outcar, elimit = elimit, mode = mode_,savefig = savefigure ,atoms = atoms, orbitals = asked_orb)

if __name__ == '__main__':
    #plot(orbitals='s', POSCAR='POSCAR')
    parser = argparse.ArgumentParser()
    parser.add_argument("--orbitals","-o", type=str,default = "spd", help = "Orbitals asked for ploting Ex = spd")
    parser.add_argument("--poscar","-g", type=str,default = "POSCAR", help = "POSCAR file name")
    parser.add_argument("--procar","-p", type=str,default = "PROCAR", help = "PROCAR file name")
    parser.add_argument("--outcar","-t", type=str,default = "OUTCAR", help = "OUTCAR file name")
    parser.add_argument("--bandplot","-b", type=str,default = "Band_Plot", help = "Plot file name")
    parser.add_argument("--run", action='store_true')
    args = parser.parse_args()
    if args.orbitals:
        orbitals = [*args.orbitals]
    if args.POSCAR:
        POSCAR = args.POSCAR
    if args.PROCAR:
        PROCAR = args.PROCAR
    if args.OUTCAR:
        OUTCAR = args.OUTCAR
    if args.Band_Plot:
        savefigure = args.Band_Plot
    plot(orbitals = orbitals, POSCAR = POSCAR, PROCAR = PROCAR, OUTCAR = OUTCAR, savefigure = savefigure)
    if args.run:
        os.system("./plot_file.py")
    


    