#!/bin/bash
stem="adhoc_benignStart"
outStem="../class_results_Adhoc"
echo Running $stem
    touch $outStem.txt &&
    ./boostexter -n 500 -S $stem - V &&
    ./boostexter -C -S $stem < $stem.test  > $outStem.txt &
echo "Done"
