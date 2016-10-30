import pickle as p
from operator import itemgetter
from dicttoxml import dicttoxml
import csv
from csv import DictWriter

diagnoses = [ u'Red DCIS', u'Red ILC',  u'Red IDC', u'Red LCIS',  \
 u'Red ADH', u'LobularNeoplasia', u'Red ALH']

cancer = ['Red DCIS', u'Red ILC',  u'Red IDC', u'Red LCIS']
atypias = ['Red ADH', 'Red ALH' ]


"I need all atypias between 2010 and 2016 with no prior or concurrent LCIS or cancer.  Need all path reports for each."
 

"Later need all atypias including LCIS with no prior or concurrent cancer (Less urgent.  I want to find all atypias in males."
 

dataPath = "../reportDB+new.p"
exportPath = "kevinExport.csv"

db = p.load( open (dataPath, 'rb'))

print "len seed DB", len(db)

def getMRNDB(db):
    mrns = {}

    for report in db:
        mrn = report['MRNPlusX']
        if mrn in mrns:
            mrns[mrn].append(report)
        else:
            mrns[mrn] = [report]

    for mrn in mrns:
        reports = mrns[mrn]
        
        sortedReports = sorted( reports, key=itemgetter('Report_Date_TimePlusX') )

        mrns[mrn] = sortedReports

    return mrns    


def filt(report, validKeys, blackout):
       
    for diag in blackout:
        assert report[diag] in [1,0, 'Present','Absent']
        if report[diag] in [1, 'Present']:
            return False
    
    for diag in validKeys:
        assert report[diag] in [1,0, 'Present','Absent']
        if report[diag] in [1, 'Present']:
            return True
    
    return 'benign'

results = []
resultRecords = []
resultFirstRecs = []

mrns = getMRNDB(db)

for mrn in mrns:
    reports = mrns[mrn]
    
    sortedReports = sorted( reports, key=itemgetter('Report_Date_TimePlusX') )


    assert reports == sortedReports
    
    assert len(sortedReports) > 0
    indx = 0
    firstRep =  sortedReports[indx]
    while not 'breast' in firstRep['Report_Text'].lower() and indx < len(sortedReports) -1:
        indx +=1
        firstRep =  sortedReports[indx]

    
    inst = firstRep['Institution']
    time = firstRep['Report_Date_TimePlusX'].isoformat().split("T")[0]

    if firstRep['Report_Date_TimePlusX'].year < 2010:
        continue

    passes = filt(firstRep, atypias,cancer)
    queryIndx = indx
    while passes == 'benign' and queryIndx < len(sortedReports) -1:
        queryIndx +=1
        passes = filt(sortedReports[queryIndx], atypias,cancer)

    if passes == True:
        results.append( (mrn, inst, time) ) 
        resultRecords.extend([r for r in sortedReports if 'breast' in r['Report_Text'].lower()])
        resultFirstRecs.append(sortedReports[queryIndx])


    assert len(set([r[0] for r in results])) == len(results)

print "Number of Fitting query", len(results)
print "Number of Records", len(resultRecords)

p.dump(resultRecords, open('atypiaExport.p','wb'))

keys = resultRecords[0].keys()
with open(exportPath, "wb") as outCSV:
    writer = DictWriter(outCSV, keys)
    writer.writeheader()
    writer.writerows(resultRecords)
    

