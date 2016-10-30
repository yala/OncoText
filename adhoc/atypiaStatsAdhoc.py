import pickle as p
from operator import itemgetter
from dicttoxml import dicttoxml
import csv
from csv import DictWriter
import sys
sys.path.append("..")
from constants import *


cancer =  const_cancers
atypias =   [
  'Red ALH','Red ADH', 'Red LCIS','Red ADH_DCIS'
  ]

cohort_atypias =   [
  'ADH_DCIS', 'LCIS','ALH','ADH',
  ]



"Later need all atypias including LCIS with no prior or concurrent cancer (Less urgent.  I want to find all atypias in males."
 
" 184/1,658 (11.1 %) developed breast cancer at a mean follow-up of 68 months. Estimated \
10-year cancer risks were 17.3 % with ADH, 20.7 % with ALH, 23.7 % with LCIS, and 26.0 % with severe ADH"

dataPath = "../reportDB+new+rule.p"
exportPath = "atypiaSet10-22.csv"
dateFilterFlag = True

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

def hasCancer(report):
    for diag in cancer:
        assert report[diag] in [1,0, 'Present','Absent']
        if report[diag] in [1, 'Present']:
            return True
    
    return False

def hasSomeAtyp(report):
    for diag in atypias:
        assert report[diag] in [1,0, 'Present','Absent']
        if report[diag] in [1, 'Present']:
            return True
    
    return False


def hasCancerThresh(rep, startYear, thresh):
    if ((rep['Report_Date_TimePlusX'] - startYear).days / 365.) >= thresh:
        return False
    return hasCancer(rep)

def filt(report):
       
    if hasCancer(report):
        return False
    
    for diag in cohort_atypias:
        if diag in report:
            assert report[diag] in [1,0, 'Present','Absent']
            if report[diag] in [1, 'Present']:
                return True
    
    return 'benign'

def getCohort(mrns):
    results = []
    resultRecords = []
    resultFirstRecs = []
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

        firstYear = firstRep['Report_Date_TimePlusX'].year
        if dateFilterFlag and (firstYear > 2010 or firstYear < 1987 )  :
            continue

        passes = filt(firstRep)

        ## implies prior or concurrent cancer:
        if passes == False:
            continue

        queryIndx = indx
        while passes == 'benign' and queryIndx < len(sortedReports) -1:
            queryIndx +=1
            passes = filt(sortedReports[queryIndx])

        if passes == True:

            concurrent = False
            ## Check cancer does not occur in 6months
            startYear = sortedReports[queryIndx]['Report_Date_TimePlusX']

            for rep in sortedReports[queryIndx:]:
                if hasCancerThresh(rep, startYear, .5):
                    concurrent = True
                    break
            if concurrent:
                continue

            resReps = sortedReports[queryIndx:]
            results.append( resReps ) 
            resultRecords.extend(resReps)
            resultFirstRecs.append(sortedReports[queryIndx])


    assert len(set([r[0]['Report_Text'] for r in results])) == len(results)

    return results, resultRecords, resultFirstRecs

def hasAtyp(rep, atyp):
    trumpOrder = ['Red ADH_DCIS', 'Red LCIS', 'Red ALH', 'Red ADH']
    trumpOrder = ['ADH_DCIS', 'LCIS', 'ALH', 'ADH']

    for a in trumpOrder:
        if a == atyp:
            return atyp in rep and rep[atyp] == 'Present'

        if a in rep and rep[a] == "Present":
            return False


def countCancers(cohort, years):

    for atyp in cohort_atypias:#atypias:    
        print "atyp:", atyp

        seed = [patient for patient in cohort if hasAtyp(patient[0], atyp)]

        if len(seed) == 0:
            continue

        print "count seed", len(seed)
        print "percent seed over cohort", round(1.*len(seed) / len(cohort),2)
        cancerCount = 0
        for patient in seed:
            startYear = patient[0]['Report_Date_TimePlusX']
            for rep in patient[1:]:
                if hasCancerThresh(rep, startYear, years):
                    cancerCount += 1
                    break
        print "cancer count", cancerCount
        print "cancer rate at ", years,"years:",  round(cancerCount*1./len(seed),2)

        print "--------"


db = p.load( open (dataPath, 'rb'))

print "len seed DB", len(db)

allAtyps = [r for r in db if hasSomeAtyp(r)]
print "atyp rate", round(len(allAtyps)*1. / len(db),1)


mrns = getMRNDB(db)

results, resultRecords, resultFirstRecs = getCohort(mrns)
print len(results)

countCancers(results, 10)


print "Number of Fitting query", len(results)
print "Number of Records", len(resultRecords)

p.dump(resultRecords, open('atypiaExport.p','wb'))

keys = resultRecords[0].keys()
with open(exportPath, "wb") as outCSV:
    writer = DictWriter(outCSV, keys)
    writer.writeheader()
    writer.writerows(resultRecords)
    

