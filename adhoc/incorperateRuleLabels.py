import pickle as p
import sys



rulePath = "../rawBreastPathReport.p"
modelPath = "../reportDB+new.p"
exportPath = "../reportDB+new+rule.p"


rules = p.load(open(rulePath, 'rb'))


transferDiags = ['CancerNOS', 'InvasiveSuspicious', 'InsituNOS', 'CancerInvInsituNOS', 
  'CancerSuspicious', 'TubularCancer']


transferAtyps = ['ADH', 'ALH', 'LCIS', 'ADH_DICS']

ruleDict = {}
for r in rules:
    ruleDict[r['ReportID']] = r

model = p.load(open(modelPath, 'rb'))

for m in model:
    repID = m['ReportID']
    rule = ruleDict[repID]
    for diag in transferDiags:
        if diag in rule:
            m['Red '+diag] = 'Present' if str(rule[diag]) == '1' else 'Absent'

    for diag in transferAtyps:
        if diag in rule:
            m[diag] = 'Present' if str(rule[diag]) == '1' else 'Absent'

p.dump(model, open(exportPath,'wb'))