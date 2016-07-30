import pickle as p
import sys
sys.path.append("..")
from constants import *
from helpers import *
from csv import DictWriter


diagnoses = [ u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', 
 u'Medullary', u'ALH', u'ADH_DCIS', 'Borderline', 'FlatEpithelial']


def filt(report):
    if report['DOBPlusX'] == 0:
        return False
    for diag in diagnoses:
            assert report[diag] == 1 or report[diag] == 0
            if report[diag] == 1:
                return False
    return True


feas = p.load(open('FirstRecordsForFEAs.p', 'rb'))
mrnDict = getMRNDB(p.load(open('../'+outPath, 'rb')))

print "Len FEAS", len(feas)
feaDOBs = [f for f in feas if not f['DOBPlusX'] == 0]
print "Len FEAS DOBs", len(feaDOBs)

possControls = []
for mrn in mrnDict:
    reports = mrnDict[mrn]
    epId = reports[0]['EpisodeID']
    if not False in [filt(r) for r in reports if r['EpisodeID'] == epId]:
        possControls.append(mrn)

print "Len Poss Controls", len(possControls)

ageTol = 2
maxControl = 4
monthTol = 3

numPosExamples = 0
i = 0

numNegExamples = 0
j= 0

visited = {}
countNoControl = 0
controlListMRNs = []
controlListRecords = []
for fea in feaDOBs:
    dob = fea['DOBPlusX']
    diagDate = fea['Report_Date_TimePlusX']
    feaMRN =  fea['MRNPlusX']
    controls = 0
    for mrn in possControls:
        if mrn in visited:
            continue
        possDob = mrnDict[mrn][0]['DOBPlusX']
        possDiagDate = mrnDict[mrn][0]['Report_Date_TimePlusX']

        ageDif = abs((possDob - dob).days)/365.
        diagDif = abs((possDiagDate - diagDate).days)/30.

        if ageDif <= ageTol and controls < maxControl and \
        diagDif <= monthTol:
            controlListMRNs.append( {'MRNPlusX': mrn , \
            'Institution': mrnDict[mrn][0]['Institution'],\
            'ControlForMRN': feaMRN, 'ControlForInst': fea['Institution']   })
            
            for rep in mrnDict[mrn]:
                rep['ControlForMRN'] = feaMRN
                rep['ControlForInst'] = fea['Institution']

            controlListRecords.extend(mrnDict[mrn])
            controls += 1
            visited[mrn] = True

            if i < numPosExamples:
                print "POS"
                print "DOBs", dob,  possDob, ageDif
                print "diag", diagDate, possDiagDate, diagDif
                i += 1
        else:
            if j < numNegExamples:
                print "NEG"
                print "DOBs", dob,  possDob, ageDif
                print "diag", diagDate, possDiagDate, diagDif
                j += 1
    print dob.year, "Controls: ", controls

    if controls < maxControl:
        countNoControl += 1


print "Len FEAS DOBs", len(feaDOBs)
print "Count FEA mrns with no control", countNoControl
print "Num mrns in control set", len(controlListMRNs)
print "Num elts in control set", len(controlListRecords)

mrnKeys = ['MRNPlusX', 'Institution', 'ControlForMRN', 'ControlForInst']
with open("controlGroupMRN_Inst_ControlFor.csv", "wb") as outCSVMrn:
    writer = DictWriter(outCSVMrn, mrnKeys)
    writer.writeheader()
    writer.writerows(controlListMRNs)

keys = controlListRecords[0].keys()
with open("controlGroupAllData.csv", "wb") as outCSVRecords:
    writer = DictWriter(outCSVRecords, keys)
    writer.writeheader()
    writer.writerows(controlListRecords)


            






