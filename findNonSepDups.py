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
for i,report in enumerate(set(reports)):
    mrn = goldData[i]['MRNPlusX']
    count = 0
    dupLabels[report] = set([labels[i]])
    dupMRNs[report] = set([mrn])

    for j,r2 in enumerate(reports):
        if r2 == report and not "PATIENT: REMOVED_PATIENT_NAME" == report:
            count +=1
            mrn2 = goldData[j]['MRNPlusX']
            if not mrn == mrn2:
                # print "MRNS NOT MATCHIN"
                # print mrn, "," , mrn2
                # print "REPORT IS"
                # print report
                countNotSameMRNs += 1
                dupLabels[report].add( labels[j] )
                dupMRNs[report].add(mrn2)
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
