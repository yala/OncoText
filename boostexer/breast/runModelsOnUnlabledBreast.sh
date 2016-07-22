#!/bin/bash
pathTypes=(Borderline BreastSide DCIS ILC Phylodes CancerSuspicious CancerNOS TubularCancer IDC LCIS InsituNOS ADH CancerInvInsituNOS ClingingCarcinoma InvasiveSuspicious LobularNeoplasia FlatEpithelial BluntAdenosis Medullary ALH ADH_DCIS)
stem="unlabeled/pathology_all_"
outStem="../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../boostexter -n 200 -W 3 -N ngram -S $stem$name - V &&
    ./../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
