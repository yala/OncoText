#!/bin/bash
pathTypes=( cancer atypia BreastSide DCIS ILC Phylodes TubularCancer IDC LCIS ADH LobularNeoplasia FlatEpithelial BluntAdenosis Medullary ALH )
stem="labeled/pathology_"
outStem="../../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../boostexter -n 200 -W 3 -N ngram -S $stem$name - V &&
    ./../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
