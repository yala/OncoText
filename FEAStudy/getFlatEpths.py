import pickle as p
from operator import itemgetter
from dicttoxml import dicttoxml
import csv
from csv import DictWriter
from helpers import *

diagnoses = [ u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', 
 u'Medullary', u'ALH', u'ADH_DCIS', 'Borderline']

dataPath = "../reportDB.p"
exportPath = "flatAtypExports.csv"

db = p.load( open (dataPath, 'rb'))

print "len seed DB", len(db)

def filt(report):
    validKeys = ['FlatEpithelial', 'Phylodes']
    for diag in diagnoses:
        if not diag in validKeys:
            assert report[diag] == 1 or report[diag] == 0
            if report[diag] == 1:
                return False

    return report['FlatEpithelial'] == 1 

results = []
resultRecords = []
resultFirstRecs = []

mrns = getMRNDB(db)

for mrn in mrns:
    reports = mrns[mrn]
    
    sortedReports = sorted( reports, key=itemgetter('Report_Date_TimePlusX') )

    assert reports == sortedReports
    
    assert(len(sortedReports) > 0)
    firstRep =  sortedReports[0]
    inst = firstRep['Institution']
    time = firstRep['Report_Date_TimePlusX'].isoformat().split("T")[0]


    passes = filt(firstRep)

    # print "firstRep", firstRep
    # print "Flat epts", firstRep['FlatEpithelial']
    # print "passes", passes

    # raw_input()

    if filt(firstRep):
        results.append( (mrn, inst, time) ) 
        resultRecords.extend(reports)
        resultFirstRecs.append(firstRep)

    assert len(set([r[0] for r in results])) == len(results)

print "Number of FEAs", len(results)
print "Number of Records", len(resultRecords)

p.dump(resultRecords, open("AllRecordsForFEAs.p", "wb"))
p.dump(resultFirstRecs, open("FirstRecordsForFEAs.p", "wb"))



keys = resultRecords[0].keys()
with open("AllRecordsForFEAs.csv", "wb") as outCSV:
    writer = DictWriter(outCSV, keys)
    writer.writeheader()
    writer.writerows(resultRecords)
    

