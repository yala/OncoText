#!/bin/bash
pathTypes=("Are_there_positive_LN?"  "ITC" "PR"  "Her2_(Fish)" "ER" "ECE" "LVI" "BVI" "TumorGrade")
stem="red_all_"
outStem="../../../classification_results/Breast/red_class_results_all_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -n 200 -W 5 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
    