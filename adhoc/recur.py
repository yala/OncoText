import pickle as p
from operator import itemgetter
from csv import DictWriter
import sys
sys.path.append("..")
from constants import *

cancers = const_cancers




def hasCat(r, cat):
    for c in cat:
        if r[c] == 'Present':
            return True
    return False


print "load reps"
reps = p.load(open('../reportDB+new.p','rb'))


cancersMRns = set([])
recurrances = set([])
initToRep = {}
recurToRep = {}
noRecurs = set([])

mrnToReps = {} 
for r in reps:
    mrn = r['MRNPlusX']
    if not mrn in  mrnToReps:
        mrnToReps[mrn] = []
    mrnToReps[mrn].append(r)

for mrn in mrnToReps:
    rs = sorted( mrnToReps[mrn],key=itemgetter('Report_Date_TimePlusX') )

    for i,r in enumerate(rs):
        date = r['Report_Date_TimePlusX']
        if hasCat(r, cancers):
            if not r['MRNPlusX'] in cancersMRns:
                initToRep[r['MRNPlusX']] = r
            cancersMRns.add(r['MRNPlusX'])
            ## look for recurrance:
            for j in range(i, len(rs)):
                rj = rs[j]

                def dateDif():
                    return (rj['Report_Date_TimePlusX'] - date).days / 365
                if dateDif() >= 1  and hasCat(rj, cancers):
                    if not rj['MRNPlusX'] in recurrances:
                        recurToRep[r['MRNPlusX']] = rj
                    recurrances.add(mrn)

print "cancsrs", len(cancersMRns)
print "recurs", len(recurrances)

def query(cohort, keys=['ER','PR', 'Her2 (Fish)'], targets=['Negative']):#, 'Her2 (Fish)']):
    fs = cohort
    ms = set([r['MRNPlusX'] for r in fs])

    for k in keys:
        fs = [r for r in fs if r[k] in targets and r['MRNPlusX'] in ms]
        ms = set([r['MRNPlusX'] for r in fs])

    return ms

print "build cohorts"
## Get ER/PR thing Gen pipulation
queryNum = 0
cohortReps = []
noEpBool = False
for mrn in cancersMRns:
    
    epId = initToRep[mrn]['EpisodeID']
    rs = sorted( [r for r in mrnToReps[mrn] if r['EpisodeID']==epId or noEpBool],key=itemgetter('Report_Date_TimePlusX') )
    cohortReps.extend(rs)

cancCoh = cohortReps

print len(query(cohortReps))*1. / len(query(cohortReps,targets=['Positive','Negative'])), 'gen population er/pr neg'

## Get ER/PR thing recur pipulation
queryNum = 0
cohortReps = []
for mrn in recurrances:
    epId = initToRep[mrn]['EpisodeID']
    rs = sorted( [r for r in mrnToReps[mrn] if r['EpisodeID']==epId or noEpBool],key=itemgetter('Report_Date_TimePlusX') )
    cohortReps.extend(rs)


print len(query(cohortReps))*1. / len(query(cohortReps,targets=['Positive','Negative'])), 'recur population er/pr neg'

tN = query(cohortReps)
cohortTN = [r for r in cohortReps if r['MRNPlusX'] in tN]
lvis = query(cohortTN, keys=['LVI'], targets=['Yes'])
print "LVI rate", len(lvis), len(tN), 'in trip negative group'

lvis = query(cohortReps, keys=['LVI'], targets=['Yes'])
print "LVI rate", len(lvis)*1. / len(set([r['MRNPlusX'] for r in cohortReps])), 'in all recur group'


lvis = query(cancCoh, keys=['LVI'], targets=['Yes'])
print "LVI rate", len(lvis)*1. / len(set([r['MRNPlusX'] for r in cancCoh])), 'in all canc group'

# Get breastside switch
countSame = 0
for mrn in recurrances:
    if initToRep[mrn]['Red BreastSide'] == recurToRep[mrn]['Red BreastSide']:
        countSame +=1
print "num same side", countSame *1./ len(recurrances)


# Get ER/PR/Her2 Switch:
iCoh = []
rCoh = []
for mrn in recurrances:
    iepId = initToRep[mrn]['EpisodeID']
    repId = recurToRep[mrn]['EpisodeID']
    irs = sorted( [r for r in mrnToReps[mrn] if r['EpisodeID']==iepId or noEpBool],key=itemgetter('Report_Date_TimePlusX') )
    rrs = sorted( [r for r in mrnToReps[mrn] if r['EpisodeID']==repId or noEpBool],key=itemgetter('Report_Date_TimePlusX') )

    iCoh.extend(irs)
    rCoh.extend(rrs)

flipDict = {}
allFlips = set([])
for key in ['ER','PR','Her2 (Fish)']:
    posNeg = query(iCoh, keys=[key], targets=['Positive']).intersection(query(rCoh, keys=[key], targets=['Negative']))
    negPos = query(iCoh, keys=[key], targets=['Negative']).intersection(query(rCoh, keys=[key], targets=['Positive']))
    flips = posNeg.union(negPos)
    flipDict[key] = flips
    denom = query(iCoh, keys=[key],targets=['Positive','Negative']).intersection(query(rCoh, keys=[key],targets=['Positive','Negative']))
    allFlips = allFlips.union(flips)
    print "Flips for", key, len(flips)*1./len(denom)

print len(flipDict['ER'].union(flipDict['PR'])) * 1. / len(allFlips), 'protion of flips erpr'

denom = query(iCoh, keys=[key],targets=['Positive','Negative']).intersection(query(rCoh, keys=[key],targets=['Positive','Negative']))
sames = denom.difference(allFlips)

# sames = set([])
# keys = ['ER','PR','Her2 (Fish)']
# for key in keys:
#     for target in ['Positive', 'Negative']
#     posPos = query(iCoh, keys=keys, targets=['Positive']).intersection(query(rCoh, keys=keys, targets=['Positive']))
#     negNeg = query(iCoh, keys=keys, targets=['Negative']).intersection(query(rCoh, keys=keys, targets=['Negative']))
#     sames = posPos.union(negNeg)

print "Same for", len(sames)*1./len(denom)


outReps = [r for r in reps if r['MRNPlusX'] in recurrances]
print len(outReps)
p.dump(outReps, open('allRepsForPatientsWithRecurrance.p','wb'))