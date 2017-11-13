#!/bin/bash
stem="$1"
outStem="../../../classification_results/API/$1"

boost1=(${2//./ })
boost2=(${3//./ })
boost3=(${4//./ })
boost4=(${5//./ })
boost5=(${6//./ })
boost6=(${7//./ })

for name in "${boost1[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done ${boost1[@]}"
for name in "${boost2[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done ${boost2[@]}"
for name in "${boost3[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done ${boost3[@]}" 
    
for name in "${boost4[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done ${boost4[@]}"

for name in "${boost5[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done ${boost5[@]}"

for name in "${boost6[@]}"; do
    ./../../boostexter -n 400 -W 4 -N ngram -S $stem$name - V &&
    touch $outStem$name.txt &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
wait
echo "Done ${boost6[@]}"

    
