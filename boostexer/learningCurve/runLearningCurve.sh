#!/bin/bash
pathTypes=(Borderline BreastSide DCIS ILC Phylodes CancerSuspicious CancerNOS TubularCancer IDC LCIS InsituNOS ADH CancerInvInsituNOS ClingingCarcinoma InvasiveSuspicious LobularNeoplasia FlatEpithelial BluntAdenosis Medullary ALH ADH_DCIS)
size=(100, 500, 1000, 2000, 4000, 5000, 5500)
stem="pathology_"
outStem="../../learningCurveResults/class_results_"
for name in "${pathTypes[@]}"; do
    for num in "${size[@]}"; do
        touch $outStem$num_$name.txt &&
        ./../boostexter -n 200 -W 3 -N ngram -S $stem$num_$name - V &&
        ./../boostexter -C -S $stem$num_$name < $stem$num_$name.test  > $outStem$num_$name.txt &
    done
done
echo "Done"
