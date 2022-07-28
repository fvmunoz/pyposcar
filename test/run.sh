rm temp
for i in POSCAR   POSCAR-7-9-B.vasp   POSCAR-7-9.vasp   POSCAR-C3Si.vasp   POSCAR-C4.vasp   POSCAR-C6H.vasp   POSCAR-C6.vasp   POSCAR-nv.vasp   POSCAR-SiV.vasp   POSCAR-V2.vasp
do
    
    echo $i;
    ../analize.py $i > temp
    mv ${i}_defect.vasp ${i}_cluster.vasp aux
    diff -q aux/${i}_defect.vasp results/${i}_defect.vasp
    diff -q aux/${i}_cluster.vasp results/${i}_cluster.vasp
done
diff temp results/results
