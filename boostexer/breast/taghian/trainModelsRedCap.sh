#!/bin/bash
pathTypes=("Red_DCIS" "Red_LCIS" "Red_IDC" "Red_ILC" "Red_ALH" "Red_ADH" "Red_LobularNeoplasia" "Red_FlatEpithelial" "Red_BluntAdenosis" "Red_BreastSide" "cancer" "atypia" "Are_there_positive_LN?"  "ITC" "PR"  "Her2_(Fish)" "ER" "ECE" "LVI" "BVI")
stem="pathology_"
outStem="../../../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -n 200 -W 4 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
    
