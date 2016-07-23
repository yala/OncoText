import pickle as p
import sys
sys.path.append("..")
from constants import *


ruleBasedData = p.load(open('../'+dataPath, 'rb'))
mlData = p.load(open('../'+outPath, 'rb'))


def buildDict(data, debug = False):
    resultDict = {}
    for rep in data:
        text = rep['Report_Text']
        if debug:
            print rep
            print 'DCIS' in rep and 'ILC' in rep
            raw_input()
        # This is done to filter out unlabled reports
        if 'DCIS' in rep and 'ILC' in rep:
            resultDict[text] = rep
    return resultDict


ruleBasedDict = buildDict(ruleBasedData)
print "Num labled rule samples",len(ruleBasedDict)
mlDict = buildDict(mlData)
print "Num labled ML samples",len(mlDict)

## Task is as follows: Find disagreemnet per diag with rule based system

disagreement = {}
counts = {}
numDisagreement = 0
for diag in diagnoses:
    disagreement[diag] = []
    counts[diag] = 0
    for text in ruleBasedDict:

        if diag in ruleBasedDict[text]:
            ruleLabel = ruleBasedDict[text][diag]
            if ruleLabel == "RIGHT":
                ruleLabel = 1
            elif ruleLabel == "LEFT":
                ruleLabel = 0
                
            counts[diag] += 1
        else:
            continue
            
        mlLabel   = mlDict[text][diag]
     
        if not str(ruleLabel) == str(mlLabel):
            if counts[diag] < 10:
                print diag, ruleLabel, mlLabel
            disagreement[diag].append({'text':text, 'ruleLabel':ruleLabel,\
             'mlLable':mlLabel})

    print diag, len(disagreement[diag])
    numDisagreement += len(disagreement[diag])


print "Total num Disagreement", numDisagreement
print counts


p.dump(disagreement, open("DisagreementDict.p", 'wb'))