#!/bin/bash
pathTypes=("Red_ADH_DCIS" "Red_Phylodes" "Red_CancerNOS" "Red_InvasiveSuspicious" "Red_InsituNOS" "Red_CancerInvInsituNOS" "Red_CancerSuspicious" "Red_TubularCancer" "Red_ILC" "Red_IDC" "Red_FlatEpithelial" "Red_BluntAdenosis") #"Red_SuspiciousForPhyllodes" "TumorGrade" "Oncotype_score" "Red_CancerInvInsituNOS" "Red_InsituNOS" "Red_InvasiveSuspicious" "Red_CancerNOS" "Red_Phylodes" "Red_ADH_DCIS" "BiopsyType" "Red_DCIS" "Red_LCIS" "Red_IDC" "Red_ILC" "Red_ALH" "Red_ADH" "Red_LobularNeoplasia" "Red_FlatEpithelial" "Red_BluntAdenosis" "Red_BreastSide" "cancer" "atypia" "Are_there_positive_LN?"  "ITC" "PR"  "Her2_(Fish)" "ER" "ECE" "LVI" "BVI")
stem="pathology_"
outStem="../../../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    ./../../boostexter -n 300 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
        ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
    
