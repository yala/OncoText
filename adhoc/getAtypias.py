import cPickle as p
import sys
sys.path.append("..")
from operator import itemgetter
from dicttoxml import dicttoxml
import csv
from csv import DictWriter
from constants import *


dataPath = "../labeledReps_Convention.p"

db = p.load( open (dataPath, 'rb'))

print "len seed DB", len(db)


def getMRNDB(db):
    mrns = {}

    for report in db:
        mrn = report['FakeMRN'] if 'FakeMRN' in report else report['MRNPlusX']
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


exportPaths = ["allFEAsFeb6.csv", "allADHsFeb6.csv", "allAtypiaFeb6.csv", 
"allAtypia2010Feb6.csv", "allCancersFeb6.csv"]


yearFilts = [False, False, False, True, False]
instFilts = [False,False,False,False, False]


cancerT = [
   'ILC','DCIS', 'IDC', 
   'CancerNOS', 'InsituNOS', 'CancerInvInsituNOS', 'TubularCancer', 'CancerInvNOS', 'CancerInvasive',
   #'CancerNotOfBreastOrigin'#, 'cancer'
   ]

all_cancer = [cancerT, cancerT, cancerT, cancerT, [] ]

atypiasT = [
   'ALH','ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia'
   ]

fea = ["FlatEpithelial"]
adh = ["ADH"]

all_atypias = [fea, adh,atypiasT, atypiasT, cancerT ]

for i in range(len(exportPaths)):

    exportPath = exportPaths[i]
    cancer = all_cancer[i]
    atypias = all_atypias[i]
    yearFilt = yearFilts[i]
    instFilt = instFilts[i]

    results = []
    resultRecords = []
    resultFirstRecs = []

    mrns = getMRNDB(db)

    for mrn in mrns:
        reports = mrns[mrn]
        
        sortedReports = sorted( reports, key=itemgetter('Report_Date_TimePlusX') )

        for r in sortedReports:
            if type(r['Report_Date_TimePlusX']) == datetime.datetime:
                r['Report_Date_TimePlusX'] = r['Report_Date_TimePlusX'].isoformat()

        assert reports == sortedReports
        
        assert len(sortedReports) > 0
        indx = 0
        firstRep =  sortedReports[indx]
        while not 'breast' in firstRep['Report_Text'].lower() and indx < len(sortedReports) -1:
            indx +=1
            firstRep =  sortedReports[indx]
        
        inst = firstRep['Institution']
        time = firstRep['Report_Date_TimePlusX'].split("T")[0]

        passes = filt(firstRep, atypias,cancer)
        queryIndx = indx

        def crit():
            passBool = passes == True and int(sortedReports[queryIndx]['Report_Date_TimePlusX'].split('-')[0]) < 2010 and yearFilt
            repBool = passes == 'benign' or passBool
            return repBool and queryIndx < len(sortedReports) -1

        while  crit():
            queryIndx +=1
            passes = filt(sortedReports[queryIndx], atypias,cancer)


        if passes == True :
            if int(sortedReports[queryIndx]['Report_Date_TimePlusX'].split('-')[0]) < 2010 and yearFilt:
                continue
            epId = sortedReports[queryIndx]["EpisodeID"]
            concurrentCancr = False
            concReps = [r for r in sortedReports if r["EpisodeID"] == epId]
            for r in concReps:
                conc =filt(r, atypias, cancer)
                if conc == False:
                    concurrentCancr = True

            if not concurrentCancr:
                results.append( (mrn, inst, time) ) 
                resultRecords.extend([r for r in sortedReports if 'breast' in r['Report_Text'].lower()])
                resultFirstRecs.append(sortedReports[queryIndx])


        assert len(set([r[0] for r in results])) == len(results)

    print "Number of Fitting query", len(results)
    print "Number of Records", len(resultRecords)

    for r in resultRecords:
        if "ruleBreastSide" in r:
            del r["ruleBreastSide"]

    p.dump(resultRecords, open('atypiaExport.p','wb'))

    keys = [k for k in key_order_convention if k in resultRecords[0].keys()] + [k for k in resultRecords[0].keys() if not k in key_order_convention]
    with open(exportPath, "wb") as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(resultRecords)
        

