import pickle as p
import sys
sys.path.append("..")
from constants import *
from helpers import *
from csv import DictWriter
import xmltodict



diagnoses = [ u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', 
 u'Medullary', u'ALH', u'ADH_DCIS', 'Borderline', 'FlatEpithelial']


#Return true if the report is benign
def filt(report):
    if report['DOBPlusX'] == 0:
        return False
    for diag in diagnoses:
            assert report[diag] == 1 or report[diag] == 0
            if report[diag] == 1:
                return False
    return True

### Main Script
### This script opens up first records from the FEA patients, and 
### tries to find maxControl number patients to match each one
### Control patient has to have benign episode, be within an age Tol of 
### age, and within a monthTol months of report date

feas = p.load(open('FirstRecordsForFEAs.p', 'rb'))
mrnDict = getMRNDB(p.load(open('../'+outPath, 'rb')))
oldDobs1 = xmltodict.parse(open('DOBmrnplusx.xml', 'rb'))['dataroot']['DOBmrnplusx']
oldDobs2 = xmltodict.parse( open('DataForAdamOn2010_2016WithDOB.xml', 'rb') )['dataroot']['DataForAdamOn2010_2016']
newDobs = p.load(open('graceLatestDOBs.p', 'rb'))   

print "Len FEAS", len(feas)
feaDOBs = [f for f in feas if not f['DOBPlusX'] == 0]
feaNoDOBs = [f['MRNPlusX'] for f in feas if  f['DOBPlusX'] == 0]
print 'FEA NO DOBS', feaNoDOBs
print "Len FEAS DOBs", len(feaDOBs)

possControls = []
for mrn in mrnDict:
    reports = mrnDict[mrn]
    epId = reports[0]['EpisodeID']
    ## Comperehension asserts that all reports in episode of first report is benign
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
notEnoughMRNs = []
## For each fea, find certain number of controls
for fea in feaDOBs:
    dob = fea['DOBPlusX']
    diagDate = fea['Report_Date_TimePlusX']
    feaMRN =  fea['MRNPlusX']
    controls = 0
    #Find controls for each one
    for mrn in possControls:
        if mrn in visited:# or not 'breast' in mrnDict[mrn][0]['Report_Text'].lower(): #Make sure we haven't used this control before
            continue
        possDob = mrnDict[mrn][0]['DOBPlusX']
        possDiagDate = mrnDict[mrn][0]['Report_Date_TimePlusX']

        ageDif = abs((possDob - dob).days)/365.
        diagDif = abs((possDiagDate - diagDate).days)/30.

        #Control checks
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
        notEnoughMRNs.append(feaMRN)


newestControls = []
newestMRNs = [ (f['MRNPlusX'],f['MRN_Type']) for f in newDobs]
oldMRNs1 =   [ (f['MRN_x002B_x'], f['MRN_Type']) for f in oldDobs1 if 'MRN_x002B_x' in f and 'MRN_Type' in f ]
oldMRNs2 = [ (f['MRNPlusX'],f['MRN_Type']) for f in oldDobs2 if 'MRNPlusX' in f and 'MRN_Type' in f]
oldMRNs = oldMRNs1 + oldMRNs2

newestControls = [r for r in controlListRecords if (r['ControlForMRN'], r['ControlForInst']) in newestMRNs  and not (r['ControlForMRN'], r['ControlForInst']) in oldMRNs]
print 'len(newDobs)', len(newDobs)
print 'len(newestControls MRNS)', len(set([r['ControlForMRN'] for r in newestControls]))
print 'len(newestControls)', len(newestControls)

keys = newestControls[0].keys()
with open("controlGroupAllData_newestOnly.csv", "wb") as newestCSVRecords:
    writer = DictWriter(newestCSVRecords, keys)
    writer.writeheader()
    writer.writerows(newestControls)

print "Len FEAS DOBs", len(feaDOBs)
print "Count FEA mrns with not enough control", countNoControl
print "Those MRNs are", notEnoughMRNs
print "Num mrns in control set", len(controlListMRNs)
print "Num elts in control set", len(controlListRecords)

print "Controls cover", len(set([(r['ControlForMRN'], r['ControlForInst']) for r in controlListRecords]))


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

missingDOBFeas = [f['MRNPlusX'] for f in feas if f['DOBPlusX'] == 0]
print "Number of missing DOBs", len(missingDOBFeas)
with open('missingFEAMRNs.csv', 'wb') as outMissing:
    outMissing.write(','.join(missingDOBFeas))



            






