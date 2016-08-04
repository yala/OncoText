#!/bin/bash
pathTypes=(er pr BVI Comedonercrosis EIC Her2 LVI Max_Tumor_Size Micopapillary NOS Other_Cancr Pagets Solid Cribiform Type_of_biopsy)
stem="pathology_"
outStem="../../../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -n 500 -W 5 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
    