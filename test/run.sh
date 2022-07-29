rm temp
for i in POSCAR   POSCAR-7-9-B.vasp   POSCAR-7-9.vasp   POSCAR-C3Si.vasp   POSCAR-C4.vasp   POSCAR-C6H.vasp   POSCAR-C6.vasp   POSCAR-nv.vasp   POSCAR-SiV.vasp   POSCAR-V2.vasp
do
    
    echo $i;
    ../analize.py $i > temp
    mv ${i}_defect.vasp ${i}_cluster.vasp aux
    diff -q aux/${i}_defect.vasp results/${i}_defect.vasp
    diff -q aux/${i}_cluster.vasp results/${i}_cluster.vasp

    # testing the larger clusters
    ../analize.py $i -n 1 > temp-n1
    mv ${i}_cluster.vasp aux/${i}_cluster-n1.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-n1.vasp results/${i}_cluster-n1.vasp

    # testing even larger clusters
    ../analize.py $i -n 2 > temp-n2
    mv ${i}_cluster.vasp aux/${i}_cluster-n2.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-n2.vasp results/${i}_cluster-n2.vasp

    # testing smoothing
    
    ../analize.py $i -n 1 -s > temp-s1
    mv ${i}_cluster.vasp aux/${i}_cluster-s1.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-s1.vasp results/${i}_cluster-s1.vasp

    ../analize.py $i -n 2 -s > temp-s2
    mv ${i}_cluster.vasp aux/${i}_cluster-s2.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-s2.vasp results/${i}_cluster-s2.vasp

    # testing hydrogenation

    ../analize.py $i -n 1 -s -y > temp-h1
    mv ${i}_cluster.vasp aux/${i}_cluster-h1.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-h1.vasp results/${i}_cluster-h1.vasp

    ../analize.py $i -n 2 -s -y > temp-h2
    mv ${i}_cluster.vasp aux/${i}_cluster-h2.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-h2.vasp results/${i}_cluster-h2.vasp

    
done
diff temp results/results
diff temp-n1 results/results-n1
diff temp-n2 results/results-n2
