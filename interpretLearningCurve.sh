#!/bin/bash
size=(100 500 1000 2000 4000 5000 5500)
stem="learningCurveResults/class_results_"
delim="_"
for num in "${size[@]}"; do
    python interpretResults.py $stem$num$delim
done
echo "Done"
