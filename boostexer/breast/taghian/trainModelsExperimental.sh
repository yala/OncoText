#!/bin/bash
pathTypes=("Are_there_positive_LN?" "Type_of_sampled_LN_(choice=None)" "Pagets" "Lymphovascular_invasion Number_of_LN_with_0.02-_0.2_cm" "EIC" "ITC" "Focality" "Sentinel_LN_(#_Sampled)" "PR" "Comedonercrosis" "ECE" "Purpose_of_surgey" "SLN_staining_(if_positive)_(choice=Frozen_Section)" "Type_of_sampled_LN_(choice=SLNB_(Sentinel_LN_Biopsy))" "Micro_or_Gross Other_Cancr" "Radical_Mastectomy" "Type_of_Surgery" "Simple_Mastectomy" "Type_of_biopsy" "No_malignancy" "Solid_Cribiform" "Number_of_LN_with_<_=0.02_cm Method_size" "Her2_(Fish)" "SLN_staining_(if_positive)_(choice=Keratin)" "Mastectomy_incision" "LVI" "ER" "Micopapillary" "Skin_sparing_Mastectomy" "Invasive" "SLN_staining_(if_positive)_(choice=H_&_E)" "Type_of_sampled_LN_(choice=Non_SLN_(Non_Sentinel_LN))" "Sentinel_LN_(#_Malignant)" "Nipple_sparing_Mastectomy" "Type_of_sampled_LN_(choice=ALND_(Axillary_LN_Dissection))" "Skin" "ALND_(#malignant)" "BVI" "Modified_radical_Mastectomy" "Type_of_sampled_LN_(choice=Intraparynchemal)" "NOS")
stem="pathology_"
outStem="../../../classification_results/Breast/class_results_"
for name in "${pathTypes[@]}"; do
    echo $stem$name 
    touch $outStem$name.txt &&
    ./../../boostexter -n 1 -W 1 -N ngram -S $stem$name - V &&
    ./../../boostexter -C -S $stem$name < $stem$name.test  > $outStem$name.txt ;
    echo "-------------------------------------"
done
echo "Done"
    