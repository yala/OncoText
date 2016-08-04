#!/bin/bash
pathTypes=("ER" "PR" "BVI" "Comedonercrosis" "EIC" "Her2_(Fish)" "LVI" "Micopapillary" "NOS" "Other_Cancr" "Pagets" "Solid_Cribiform" "Type_of_biopsy")
stem="pathology_"
outStem="../../../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -n 1 -W 1 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt ;
done
echo "Done"
    