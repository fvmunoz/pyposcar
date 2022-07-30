echo "Testing the identification of defects"
for i in POSCAR   POSCAR-7-9-B.vasp   POSCAR-7-9.vasp   POSCAR-C3Si.vasp\
                  POSCAR-C4.vasp   POSCAR-C6H.vasp   POSCAR-C6.vasp   POSCAR-nv.vasp\
                  POSCAR-SiV.vasp   POSCAR-V2.vasp
do
    echo $i;
    ../analize.py $i >> temp
    mv ${i}_defect.vasp ${i}_cluster.vasp aux
    diff -q aux/${i}_defect.vasp results/${i}_defect.vasp
    diff -q aux/${i}_cluster.vasp results/${i}_cluster.vasp
done
mv temp aux/results
# diff aux/results results/results

echo "Testing the creation of clusters"
for i in POSCAR   POSCAR-7-9-B.vasp   POSCAR-7-9.vasp   POSCAR-C3Si.vasp\
                  POSCAR-C4.vasp   POSCAR-C6H.vasp   POSCAR-C6.vasp   POSCAR-nv.vasp\
                  POSCAR-SiV.vasp   POSCAR-V2.vasp
do    
    echo $i;
    ../analize.py $i -n 1 >> temp-n1
    mv ${i}_cluster.vasp aux/${i}_cluster-n1.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-n1.vasp results/${i}_cluster-n1.vasp

    # testing even larger clusters
    ../analize.py $i -n 2 >> temp-n2
    mv ${i}_cluster.vasp aux/${i}_cluster-n2.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-n2.vasp results/${i}_cluster-n2.vasp

done
mv temp-n1 aux/results-n1
mv temp-n2 aux/results-n2
# diff aux/results-n1 results/results-n1
# diff aux/results-n2 results/results-n2


echo "Testing the creation of clusters plus smoothing"
for i in POSCAR   POSCAR-7-9-B.vasp   POSCAR-7-9.vasp   POSCAR-C3Si.vasp\
                  POSCAR-C4.vasp   POSCAR-C6H.vasp   POSCAR-C6.vasp   POSCAR-nv.vasp\
                  POSCAR-SiV.vasp   POSCAR-V2.vasp
do
    echo $i
    ../analize.py $i -n 1 -s >> temp-s1
    mv ${i}_cluster.vasp aux/${i}_cluster-s1.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-s1.vasp results/${i}_cluster-s1.vasp

    ../analize.py $i -n 2 -s >> temp-s2
    mv ${i}_cluster.vasp aux/${i}_cluster-s2.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-s2.vasp results/${i}_cluster-s2.vasp

done
mv temp-s1 aux/results-s1
mv temp-s2 aux/results-s2
# diff aux/results-s1 results/results-s1
# diff aux/results-s2 results/results-s2


echo "Testing the creation of passivated clusters"
for i in POSCAR   POSCAR-7-9-B.vasp   POSCAR-7-9.vasp   POSCAR-C3Si.vasp\
                  POSCAR-C4.vasp   POSCAR-C6H.vasp   POSCAR-C6.vasp   POSCAR-nv.vasp\
                  POSCAR-SiV.vasp   POSCAR-V2.vasp
do
    echo $i
    ../analize.py $i -n 1 -s -y >> temp-h1 2>> error-h1
    mv ${i}_cluster.vasp aux/${i}_cluster-h1.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-h1.vasp results/${i}_cluster-h1.vasp 

    ../analize.py $i -n 2 -s -y >> temp-h2 2>> error-h2
    mv ${i}_cluster.vasp aux/${i}_cluster-h2.vasp
    rm ${i}_defect.vasp 
    diff  aux/${i}_cluster-h2.vasp results/${i}_cluster-h2.vasp  
done
mv temp-h1 aux/results-h1
mv temp-h2 aux/results-h2
mv error-h1 aux/
mv error-h2 aux/
# diff temp-h1 results/results-h1
# diff temp-h2 results/results-h2
