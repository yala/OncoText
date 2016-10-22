import pickle as p
import sys
sys.path.append("..")
from constants import *
import random
from csv import DictWriter

random.seed(1)

ruleBasedData = p.load(open('../'+dataPath, 'rb'))
mlData = p.load(open('../'+outPath, 'rb'))

targets = [
  'ADH_DCIS', 'Phylodes', 'CancerNOS', 'InvasiveSuspicious', 
  'InsituNOS', 'CancerInvInsituNOS',
  'CancerSuspicious', 'TubularCancer', 'ILC', 'IDC', 'FlatEpithelial', 'BluntAdenosis' ]


targets = [
   'CancerNOS', 
  'InsituNOS', 'CancerInvInsituNOS' ]


def buildDict(data, debug = False):
    resultDict = {}
    for rep in data:
        text = rep['Report_Text']
        if debug:
            print rep
            print 'DCIS' in rep and 'ILC' in rep
            raw_input()
        # This is done to filter out unlabled reports
        if ('DCIS' in rep and 'ILC' in rep )or ('Red DCIS' in rep and 'Red ILC' in rep):
            resultDict[text] = rep
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
for diag in targets:


    disagreement[diag] = []
    countsDetecs[diag] = 0

    numPrinted = 0

    for text in ruleBasedDict:

        if diag in ruleBasedDict[text]:
            ruleLabel = ruleBasedDict[text][diag]
            if ruleLabel == "RIGHT":
                ruleLabel = 1
            elif ruleLabel == "LEFT":
                ruleLabel = 0
        else:
            continue
        
        if diag in HueAnotationSource:
            mlLabel   = 1 if mlDict[text]['Red '+diag] == 'Present' else 0
        else:
            mlLabel   = mlDict[text][diag]

        if not str(ruleLabel) == str(mlLabel):
            disaArticles.add(text)
            if numPrinted < 0 and str(ruleLabel) == '0':
                print diag, ruleLabel, mlLabel
                print text
                raw_input()
                numPrinted +=1
            disagreement[diag].append({ 'ReportID':ruleBasedDict[text]['ReportID'], 'text':text, 'ruleLabel':ruleLabel,\
             'mlLable':mlLabel})
            if str(ruleLabel) == '1':
                countsDetecs[diag]+= 1
    print "----"
    print diag, len(disagreement[diag])
    print "Num rule peredict 1, ML predicts 0:", countsDetecs[diag]
    print "Num rule peredict 0, ML predicts 1:", len(disagreement[diag]) - countsDetecs[diag]
    print "Ratio disagree rule pos ", countsDetecs[diag]*1. / len(disagreement[diag])
    print '********************'
    numDisagreement += len(disagreement[diag])


print "Total num Disagreement", numDisagreement
print "% /disagree on a label Level", numDisagreement * 1. / (len(ruleBasedDict) * len(disagreement))
print "Total ratio rulePosAndML_Negative/All", sum([countsDetecs[diag] for diag in countsDetecs]) *1. / numDisagreement
print "Total num Articles", len(disaArticles)
print "% /diasgree on a report Level", len(disaArticles) *1. / len(ruleBasedDict)

p.dump(disagreement, open("DisagreementDict.p", 'wb'))

for diag in disagreement:
    if  diag == "BreastSide":
        continue
    exportAll = disagreement[diag]
    random.shuffle(exportAll)
    export = exportAll[:60]
    path = "disagreementsForMolly/disagreement_on_"+diag+".csv"
    keys = export[0].keys()
    with open(path, "wb") as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(export)
    


