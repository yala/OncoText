#!/bin/bash
pathTypes=("Are_there_positive_LN?" "Type_of_sampled_LN_(choice=None)" "ITC" "PR"  "Type_of_sampled_LN_(choice=SLNB_(Sentinel_LN_Biopsy))"  "Type_of_Surgery" "Simple_Mastectomy" "Type_of_biopsy" "Her2_(Fish)" "ER" "Nipple_sparing_Mastectomy" "Type_of_sampled_LN_(choice=ALND_(Axillary_LN_Dissection))")
stem="red_all_"
outStem="../../../classification_results/Breast/red_class_results_all_"
for name in "${pathTypes[@]}"; do
    touch $outStem$name.txt &&
    ./../../boostexter -n 200 -W 5 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt &
done
echo "Done"
    