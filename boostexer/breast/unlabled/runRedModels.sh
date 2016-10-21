#!/bin/bash
pathTypes=( "Red_SuspiciousForPhyllodes" "TumorGrade" "Oncotype_score") # "Red_CancerInvInsituNOS" "Red_InsituNOS" "Red_InvasiveSuspicious" "Red_CancerNOS" "Red_Phylodes" "Red_ADH_DCIS" "BiopsyType" "Red_DCIS" "Red_LCIS" "Red_IDC" "Red_ILC" "Red_ALH" "Red_ADH" "Red_LobularNeoplasia" "Red_FlatEpithelial" "Red_BluntAdenosis" "Red_BreastSide" "cancer" "atypia" "Are_there_positive_LN?"  "ITC" "PR"  "Her2_(Fish)" "ER" "ECE" "LVI" "BVI")
stem="red_all_"
outStem="../../../classification_results/Breast/red_class_results_all_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -n 200 -W 5 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
    
