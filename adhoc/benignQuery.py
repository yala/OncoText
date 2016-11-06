import pickle as p
from operator import itemgetter
from csv import DictWriter
import sys
sys.path.append("..")
from constants import *
import matplotlib as plt

def getQuery(reps, targets, avoids):
    resultMRNs = set({})
    mrnToReps = {} 
    for r in reps:
        mrn = r['MRNPlusX']
        if not mrn in  mrnToReps:
            mrnToReps[mrn] = []
        mrnToReps[mrn].append(r)

    for mrn in mrnToReps:
        if len(mrnToReps[mrn]) < 0:
            continue
        reps = sorted( mrnToReps[mrn],key=itemgetter('Report_Date_TimePlusX') )


        def fitsCriteta(r):
            if hasCat(r, avoids):
                return False

            if hasCat(r, targets):
                for j in range(0,len(reps)):
                    rj = reps[j]
                    def dateDiff():
                        return (rj['Report_Date_TimePlusX']  - r['Report_Date_TimePlusX']).days < 93
                    if dateDiff() and hasCat(r, avoids):
                        return False
                return True
            else:
                return 'next'
        
        for i,r in enumerate(reps):
            decision = fitsCriteta(r)
            if decision == 'next':
                continue
            if decision == True:
                resultMRNs.add(mrn)
                break
            if decision == False:
                if mrn in resultMRNs:
                    resultMRNs.remove(mrn)
                break

    results = []
    for mrn in resultMRNs:
        results.extend(mrnToReps[mrn])
    return results

def hasNotCat(r, cat):
    for c in cat:
        if r[c] == 'Present':
            return False
    return True


def hasCat(r, cat):
    for c in cat:
        if r[c] == 'Present':
            return True
    return False

reps = p.load(open('../reportDB+new.p','rb'))
# targets = ['Red FlatEpithelial']
# noAllow = ['Red ALH','Red ADH','Red LobularNeoplasia','Red ADH_DCIS', 'Red LCIS', 'Red Phylodes',
# 'Red ILC','Red DCIS', 'Red IDC', 'cancer', 'Red CancerNOS', 'Red InsituNOS', 'Red CancerInvInsituNOS',
# 'Red TubularCancer']

targets = ['Red ALH','Red ADH', 'Red ADH_DCIS', 'Red LCIS']
noAllow = [ 'Red FlatEpithelial', 'Red Phylodes',
'Red ILC','Red DCIS', 'Red IDC', 'cancer', 'Red CancerNOS', 'Red InsituNOS', 'Red CancerInvInsituNOS',
'Red TubularCancer']

cohort = getQuery(reps, targets, noAllow)
print "len cohort", len(cohort)
print "num patients in cohort", len(set([r['MRNPlusX'] for r in cohort]))
# outPath = "kevinFEAs"
outPath = "kevinAtyps"
keys = cohort[0].keys()
with open(outPath+".csv", "wb") as outCSV:

    writer = DictWriter(outCSV, keys)#,  delimiter = "$")
    writer.writeheader()
    writer.writerows(cohort)
