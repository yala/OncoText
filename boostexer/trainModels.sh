#!/bin/bash
pathTypes=(DCIS ILC Phylodes CancerSuspicious CancerNOS TubularCancer IDC LCIS ADH CancerInvInsituNOS ClingingCarcinoma InvasiveSuspicious LobularNeoplasia FlatEpithelial BluntAdenosis Medullary ALH ADH_DCIS)
for name in "${pathTypes[@]}"; do
    echo $name;
    ./boostexter -n 300 -W 4 -N ngram -S pathology_$name - V &&
    ./boostexter -C -S pathology_$name < pathology_$name.test  > ../class_results_$name.txt &
done
echo "Done"