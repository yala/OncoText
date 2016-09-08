#!/bin/bash
pathTypes=(Oncotype_score)
size=(10 50 100 500 1000 2000 4000 5000 5500)
stem="pathology_"
delim="_"
outStem="../../learningCurveResults/class_results_"
for name in "${pathTypes[@]}"; do
    for num in `seq 0 165` ; do
        touch $outStem$name.txt &&
        ./../boostexter -n 200 -W 3 -N ngram -S $stem$name$delim$size - V &&
        ./../boostexter -C -S $stem$name$delim$size < $stem$name$delim$size.test  >> $outStem$name.txt &
    done
done
echo "Done"
