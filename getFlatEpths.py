import pickle as p
from operator import itemgetter
import csv

diagnoses = [ u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', 
 u'Medullary', u'ALH', u'ADH_DCIS', 'Borderline']

dataPath = "mrnDB.p"
exportPath = "flatAtypExports.csv"

db = p.load( open (dataPath, 'rb'))

def filt(report):
    validKeys = ['FlatEpithelial', 'Phylodes']
    for diag in diagnoses:
        if not diag in validKeys:
            if str(report[diag]) == '1' or (diag in str(report[diag]) and not 'no_' in str(report[diag])) :
                return False

    return str(report['FlatEpithelial']) == '1' or ('FlatEpithelial' in str(report['FlatEpithelial']) and not 'no_' in str(report['FlatEpithelial']))

results = []

for mrn in db:
    sides = db[mrn]
    reports = []
    for key in sides:
        reports.extend(sides[key])
    sortedReports = sorted( reports, key=itemgetter('Report_Date_TimePlusX') )
    
    assert(len(sortedReports) > 0)
    firstRep =  sortedReports[0]
    passes = filt(firstRep)

    # print "firstRep", firstRep
    # print "Flat epts", firstRep['FlatEpithelial']
    # print "passes", passes

    # raw_input()

    if filt(firstRep):
        results.append(mrn)

print "Number of records", len(results)


with open(exportPath, 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(results)
