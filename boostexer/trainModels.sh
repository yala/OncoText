#!/bin/bash
pathTypes=(DCIS ILC Phylodes CancerSuspicious CancerNOS TubularCancer IDC LCIS InsituNOS ADH CancerInvInsituNOS ClingingCarcinoma InvasiveSuspicious LobularNeoplasia FlatEpithelial BluntAdenosis Medullary ALH ADH_DCIS)
stem="pathology_all_"
outStem="../class_results_all_"
for name in "${pathTypes[@]}"; do
    ./boostexter -n 200 -W 3 -N ngram -S $stem$name - V &&
    ./boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"