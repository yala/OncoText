#!/bin/bash
pathTypes1=("Red_CancerSuspicious" "Red_TubularCancer" "Red_InvasiveSuspicious" "Red_SuspiciousForPhyllodes"   "Red_CancerInvInsituNOS" "Red_InsituNOS" )
pathTypes2=("Red_InvasiveSuspicious" "Red_CancerNOS"  "BiopsyType" "Her2" "Her2_IHC" "ER_Intensity" "PR_Intensity")
pathTypes3=( "ITC" "PR"  "Her2_(Fish)" "ER" "ECE" "LVI" "BVI" 'PathologyType' 'Organ')
pathTypes4=( "Red_Papill" 'Red_CancerInvasive'  'Red_CancerInvNOS'  'NodeTissue'  'CancerNotOfBreastOrigin' )
stem="$1"
outStem="../../../classification_results/API/$1"

for name in "${pathTypes1[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p1"
for name in "${pathTypes2[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p2"
for name in "${pathTypes3[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p3"
    
for name in "${pathTypes4[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p4"
    
