#!/bin/bash
# Mode = "TAGHIAN" required
stem="../classification_results/Breast/class_results_"
python interpretResults.py $stem 
echo "Done"
