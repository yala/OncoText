import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
from createEpisodes import preprocessReports
import datetime
from operator import itemgetter
random.seed(0)

def hasCancer(b):
    cancers = [u'cancer']#, u'Red DCIS', u'Red ILC', u'Red IDC', u'Red LCIS']
    vals = [b[c] for c in cancers]
    return 'Present' in vals

## Return structue of {mrn :{epID:[reps]}}
def getEps(data,mo=3):
    countIncis = 0
    countFilt = 0
    countExis = 0
    pairs = []
    mrns = {}
    for i in range(len(data)):

        if not data[i]['MRNPlusX'] in mrns:
            mrns[data[i]['MRNPlusX']] = {}

        if not data[i]['Red BreastSide'] in mrns[data[i]['MRNPlusX']]:
            mrns[data[i]['MRNPlusX']][data[i]['Red BreastSide']] = [data[i]]
        else:
            mrns[data[i]['MRNPlusX']][data[i]['Red BreastSide']].append(data[i])

    for mrn in mrns:
        patient = mrns[mrn]
        for side in patient:
            patient[side] = sorted( patient[side], key=itemgetter('Report_Date_TimePlusX') )
            breasts = patient[side]
            

            incis= [b for b in breasts if b['BiopsyType']=='Incision' and not (hasCancer(b)) ]

            if len([b for b in breasts if b['BiopsyType']=='Incision'])>0:
                countIncis +=1

            if len([b for b in breasts if b['BiopsyType']=='Excision'])>0:
                countExis +=1

            if len(incis)>0:
                countFilt +=1

            for inc in incis:
                incisDate = inc['Report_Date_TimePlusX']
                def delta(b):
                    return (b['Report_Date_TimePlusX'] - incisDate).days/30. <= mo and (b['Report_Date_TimePlusX'] - incisDate).days > 0

                exis = [b for b in breasts if b['BiopsyType']=='Excision' and delta(b)]
                for e in exis:
                    pairs.append((inc, e))

    print "count Incis", countIncis
    print "count Excis", countExis
    print "countFilt", countFilt
    return pairs


def getStats(pairs):
    print "len pairs", len(pairs)
    num = len(pairs)
    numMalig, numBenign = len([p for p in pairs if hasCancer(p[1])]),len([p for p in pairs if not hasCancer(p[1])])
    print "malig vs benign",numMalig ,"(",round(numMalig*1./num,2),")" , numBenign,"(",round(numBenign*1./num,2),")"


key = "BiopsyType"
reps = p.load(open('../reportDB+new.p','rb'))

## Build structure of "Episodes to reps" and constrai
pairs = getEps(reps, 3)

getStats(pairs)

p.dump(pairs, open('incisToExisDb.p','wb'))

## benign needle and subsequence exis in episode

stem = '../boostexer/breast/adhoc/incisToExcis'
labels = ['malig','benign']

dataset = [(p[0]['Report_Text_Segmented'],'malig' if hasCancer(p[1]) else 'benign') for p in pairs]

random.shuffle(dataset)

trainData = dataset[:-500]
trainReports = preprocessReports([t[0] for t in trainData])
trainLabels = [t[1] for t in trainData]

testData = dataset[-500:]
testReports = preprocessReports([t[0] for t in testData])
testLabels = [t[1] for t in testData]



with open(stem+".names", 'wb') as f:
    labels = ", ".join(labels) + ".\n"
    features = "pathReport: text.\n"
    f.write(labels)
    f.write(features)

print "Saved namefile for", stem

with open(stem+".data", 'wb') as trF:
    for rep, label in zip(trainReports, trainLabels):
        trF.write(rep +", "+ str(label) + ".\n")

print "Saved trainfile for", stem

with open(stem+".test", 'wb') as tsF:
    for rep, label in zip(testReports, testLabels):
        tsF.write(rep +", "+ str(label) + ".\n")

print "Saved testfile for", stem, 'at ', (stem)