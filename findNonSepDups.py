import pickle as p
from genBoostexaFiles import goldDataPath
import re
import pprint

goldData = p.load(open(goldDataPath, 'rb'))

labels = ['DCIS' if d['DCIS'] == '1' else "no_DCIS" for d in goldData]
reports = [d['Report_Text'] for d in goldData]

dupLabels = {}
dupMRNs = {}
countNotSameMRNs = 0
dups = {}
printed = True
for i in range(len(goldData)):
    report = goldData[i]['Report_Text'] 
    if report in dups: #Meaning we have already marked this
        continue
    mrn = goldData[i]['MRNPlusX']
    count = 0
    dupLabels[report] = set([labels[i]])
    dupMRNs[report] = set([(mrn,goldData[i]['Report_Date_TimePlusX'])])

    for j in range(i, len(goldData)):
        r2 = goldData[j]['Report_Text']
        if r2 == report and not "PATIENT: REMOVED_PATIENT_NAME" == report:
            count +=1
            mrn2 = goldData[j]['MRNPlusX']
            if not mrn == mrn2:
                countNotSameMRNs += 1
                dupLabels[report].add( labels[j] )
                dupMRNs[report].add((mrn2, goldData[j]['Report_Date_TimePlusX']))

                if printed:
                    print goldData[i]
                    print '****************************'
                    print goldData[j]
                    print "-------------------"
                    inp = raw_input()
                    if inp.lower() == "stop":
                        printed = False
        if count > 1:
            dups[report] = count

nonSepDups = []
nonSepMRNs = []
for rep in dupLabels:
    dup, mrn = rep,  dupMRNs[rep]
    if len(dupLabels[dup]) >1:
        nonSepDups.append(dup)
        nonSepMRNs.append(mrn)

print len(nonSepMRNs)

print "Number of identical reports matched with diff MRN"
pprint.pprint(nonSepMRNs)
