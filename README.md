# MGH Breast Cancer Pathology Report Project

## clean.py
We read in an XML file, where raw path reports are under the key 'Report_Text', and remove all dates, 
patient names, and report ids.

We ouput a pickle file with all fields. and deidentified path reports.

## genBoostexaFiles.py
Finds the gold data in the deidentified path reports, preprocesses, splits and train and dev, and passes on relevant files to boostexer for classification

## interpretResults.py
Reads boostexa output files and gives detailed prec,recall,f1 scores per category and overall
Note, by I noticed some mistakes in human annotation, and so i fixed some of the gold labels here.

## createEpisodes.py
Link boostexa classifications to label all non-gold data, link together to form episodes, and dump into a pickle file

