import pickle as p
import sys
sys.path.append("..")
from constants import *
import random
from csv import DictWriter

random.seed(1)

ruleBasedData = p.load(open('../'+dataPath, 'rb'))
mlData = p.load(open('../reportDB+new.p', 'rb'))

targets = [
  'ADH_DCIS', 'Phylodes', 'CancerNOS', 'InvasiveSuspicious', 
  'InsituNOS', 'CancerInvInsituNOS',
  'CancerSuspicious', 'TubularCancer', 'ILC', 'IDC', 'FlatEpithelial', 'BluntAdenosis'
]

targets = [
    'ALH','ADH','ADH_DCIS', 'LCIS', 'ILC', 'DCIS', 'IDC', 'InsituNOS', 'CancerNOS', 'CancerInvInsituNOS',
    'InvasiveSuspicious', 'CancerSuspicious'
 ]

targets = [
     'LCIS',  'IDC'
 ]


def buildDict(data, debug = False):
    resultDict = {}
    for rep in data:
        repid = rep['ReportID']
        if debug:
            print rep
            print 'DCIS' in rep and 'ILC' in rep
            raw_input()
        # This is done to filter out unlabled reports
        if ('DCIS' in rep and 'ILC' in rep )or ('Red DCIS' in rep and 'Red ILC' in rep):
            if 'ruleBreastSide' in rep:
                if not (rep['ruleBreastSide'] == rep['BreastSide']):
                    continue
            resultDict[repid] = rep
    return resultDict

print "len rule data", len(ruleBasedData)
print "len ml data", len(mlData)

ruleBasedDict = buildDict(ruleBasedData)
print "Num labled rule samples",len(ruleBasedDict)
mlDict = buildDict(mlData)
print "Num labled ML samples",len(mlDict)

## Task is as follows: Find disagreemnet per diag with rule based system

disagreement = {}
disaArticles = set([])


numDisagreement = 0
countsDetecs = {}
visitedReps = set([])
for diag in targets:


    disagreement[diag] = []
    countsDetecs[diag] = 0

    numPrinted = 0

    for repID in ruleBasedDict:
        text = ruleBasedDict[repID]['Report_Text_Segmented']

        if not ('ruleBreastSide' in ruleBasedData[repID] and ruleBasedDict[repID]['ruleBreastSide'] == mlDict[repID]['Red BreastSide']):
            continue



        if diag in ruleBasedDict[repID]:
            ruleLabel = ruleBasedDict[repID][diag]
            if ruleLabel in ['1', "RIGHT"]:
                ruleLabel = 1
            elif ruleLabel in ['0', "LEFT"]:
                ruleLabel = 0
        else:
            continue
        
        visitedReps.add(repID)

        if diag in HueAnotationSource:
            assert mlDict[repID]['Red '+diag] in ['Present','Absent']
            mlLabel   = 1 if mlDict[repID]['Red '+diag] == 'Present' else 0
        else:
            mlLabel   = mlDict[repID][diag]

        if not str(ruleLabel) == str(mlLabel):
            disaArticles.add(text)
            if numPrinted < 0 and str(ruleLabel) == '0':
                print diag, ruleLabel, mlLabel
                print text
                raw_input()
                numPrinted +=1
            disagreement[diag].append({ 'ReportID':ruleBasedDict[repID]['ReportID'], 'text':text, 'ruleLabel':ruleLabel,\
             'mlLable':mlLabel})
            if str(ruleLabel) == '1':
                countsDetecs[diag]+= 1
    print "----"
    print diag, len(disagreement[diag]), round(len(disagreement[diag])*1./len(ruleBasedDict),3)
    print "Num rule peredict 1, ML predicts 0:", countsDetecs[diag]
    print "Num rule peredict 0, ML predicts 1:", len(disagreement[diag]) - countsDetecs[diag]
    print "Ratio disagree rule pos ", countsDetecs[diag]*1. / len(disagreement[diag])
    print '********************'
    numDisagreement += len(disagreement[diag])

print "num articles visited", len(visitedReps)
print "Total num Disagreement", numDisagreement
print "% /disagree on a label Level", numDisagreement * 1. / (len(ruleBasedDict) * len(disagreement))
print "Total ratio rulePosAndML_Negative/All", sum([countsDetecs[diag] for diag in countsDetecs]) *1. / numDisagreement
print "Total num Articles", len(disaArticles)
print "% /diasgree on a report Level", len(disaArticles) *1. / len(ruleBasedDict)

p.dump(disagreement, open("DisagreementDict.p", 'wb'))

allDisagreements = []
for diag in disagreement:
    if  diag == "BreastSide":
        continue
    exportAll = disagreement[diag]
    random.shuffle(exportAll)
    export = exportAll[:60]

    allDisagreements.extend( [r['ReportID'] for r in exportAll[120:]])


disagreementReps = [r for r in mlData if r['ReportID'] in allDisagreements]
random.shuffle(disagreementReps)

path = "disagreementsForMolly/disagreement_on_all.csv"

for diag in diagnoses:
    annotationName = "MG "+diag
    for r in disagreementReps:
        r[annotationName] = ''
keys = disagreementReps[0].keys()
print len(disagreementReps)
print keys
with open(path, "wb") as outCSV:
    writer = DictWriter(outCSV, keys)
    writer.writeheader()
    writer.writerows(disagreementReps)



