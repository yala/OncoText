#!/bin/bash
pathTypes1=("Red_CancerSuspicious" "Red_TubularCancer" "Red_InvasiveSuspicious" "Red_SuspiciousForPhyllodes" "TumorGrade" "Oncotype_score" "Red_CancerInvInsituNOS" "Red_InsituNOS" )
pathTypes2=("Red_InvasiveSuspicious" "Red_CancerNOS" "Red_Phylodes" "Red_ADH_DCIS" "BiopsyType" "Red_DCIS" "Red_LCIS" "Red_IDC" "Red_ILC" "Red_ALH" "Red_ADH" "Red_LobularNeoplasia")
pathTypes3=("atypia" "Are_there_positive_LN?"  "ITC" "PR"  "Her2_(Fish)" "ER" "ECE" "LVI" "BVI" "Red_FlatEpithelial" "Red_BluntAdenosis" "Red_BreastSide" "cancer")
pathTypes4=("Red_DCIS" "Red_LCIS" "Red_IDC" "Red_Papill" 'Red_CancerInvasive'  'Red_CancerInvNOS'  'NodeTissue'  'CancerNotOfBreastOrigin' 'PathologyType')
stem="$1"
outStem="../../../classification_results/API/$1"

for name in "${pathTypes1[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p1"
for name in "${pathTypes2[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p2"
for name in "${pathTypes3[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p3"
    
for name in "${pathTypes4[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done p4"
    
