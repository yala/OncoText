import cPickle as p
import sys
sys.path.append("..")
sys.path.append("../preprocessDataset")
from preprocessRawDb import *
from operator import itemgetter
from dicttoxml import dicttoxml
import csv
from csv import DictWriter
from constants import *
import pdb
import MySQLdb

def hasCat(r, cat, loose=False):
    for c in cat:
        if not loose:
            if r[c] == 'Present' or str(r[c]) == '1':
                return True
        else:
            if c in r:
                return True
    return False


## Runs enforces global constraints like ER/PR NA given no cancer
def postProcessRules(db_train):
    print(db_train[0].keys())

    for r in db_train:
        if hasCat(r, const_cancers_mod):
            r['cancer'] = 'Present'
        else:
            r['cancer'] = "Absent"
            if hasCat(r, const_atypias_mod):
                r['atypia'] = 'Present'
            else:
                r['atypia'] = "Absent"

        if r['cancer'] == 'Absent':
            for k in ['ER','PR','Her2 (Fish)', 'ECE', 'LVI','BVI', 'Are there positive LN?', 'ITC ']:
                r[k] = 'NA'

        for k in r.keys():
            if type(r[k]) is unicode:
                r[k] = str(r[k])
            if r[k] in ["Present", "Yes", "Positive", "Anatomic", "breast"]:
                r[k] = "1"
            if r[k] in ["Absent", "No", "Negative", "Cytology", "non-breast"]:
                r[k] = "0"
            if r[k] == "NA":
                r[k] = "9"
            if r[k] == "RIGHT":
                r[k] = 'r'
            if r[k] == "LEFT":
                r[k] = "l"
            #TODO change these to ints and reconfigure the db

    return db_train#[d for d in db_train if d['Organ'] == 'breast']



def getMRNDB(db):
    mrns = {}

    for report in db:
        mrn = report['MRN'] if 'MRN' in report else report['MRNPlusX']
        if mrn in mrns:
            mrns[mrn].append(report)
        else:
            mrns[mrn] = [report]

    for mrn in mrns:
        reports = mrns[mrn]
        
        sortedReports = sorted( reports, key=itemgetter('Report_Date_Time') )

        mrns[mrn] = sortedReports

    return mrns    


def filt(report, validKeys, blackout):
       
    for diag in blackout:
        assert str(report[diag]) in ['1','0', 'Present','Absent']
        if report[diag] in [1, 'Present']:
            return False
    
    for diag in validKeys:
        assert str(report[diag]) in ['1','0', 'Present','Absent']
        if str(report[diag]) in ['1', 'Present']:
            return True
    
    return 'benign'


def updateAccesDB(reportDB, tableName):

    print "Exporting", len(reportDB), "breast records to name", tableName

    db = MySQLdb.connect(host="localhost",user="root",passwd="nlpdb",db="reports")
    cur = db.cursor()
    dbKeys, placeholders = [k for k in accessDbKeys if k in reportDB[0]], ["%s" for i in accessDbKeys if i in reportDB[0] ]
    

    print "Exporting breast records... to", tableName
    sql = ("insert into "+tableName+" ("+", ".join(dbKeys)+") VALUES ("+", ".join(placeholders)+")")
    #print reportDB[0]
    for report in reportDB:
        try:
            values = [report[AccessDbToGregDict[k]] for k in dbKeys]
        except Exception , e:
            print e
            print report.keys(), "but looking for keys", [AccessDbToGregDict[k] for k in dbKeys]
            continue

        try:
            cur.execute(sql,tuple(values))
        except MySQLdb.Error, e:
             try:
                 print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                 print report
                 return None
             except IndexError:
                 print "MySQL Error: %s" % str(e)
                 print report
                 return None
        except TypeError, e:
            print("MySQL TypeError",e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError",e)
            print report
            return None
    db.commit()
    print "done."

    cur.close()
    db.close()

    return "Success"



def main():
    dataPath = "/home/nlp/pathology/returnedDB_mghMar.p"

    db = p.load( open (dataPath, 'rb'))
    db = [d for d in db if d['Organ'] == 'breast']
    print "len seed DB", len(db)

    exportPaths = ["allFEAsTable", "allADHsTable", "allAtypiaTable", 
    "allAtypia2010Table", "allCancersTable"]


    yearFilts = [ False, False, False, True, False]


    cancerT = [
       'ILC','DCIS', 'IDC', 
        'TubularCancer', 'CancerInvNOS', 'CancerInvasive',
        'CancerNotOfBreastOrigin'
       ]

    all_cancer = [cancerT, cancerT, cancerT, cancerT, [] ]

    atypiasT = [
       'ALH','ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia'
       ]

    fea = ["FlatEpithelial"]
    adh = ["ADH"]

    all_atypias = [fea, adh,atypiasT, atypiasT, cancerT ]

    for i in range(0,4):#len(exportPaths)):

        exportPath = exportPaths[i]
        cancer = all_cancer[i]
        atypias = all_atypias[i]
        yearFilt = yearFilts[i]

        results = []
        resultRecords = []
        resultFirstRecs = []

        mrns = getMRNDB(db)

        for mrn in mrns:
            reports = mrns[mrn]
            for r in reports:
                r['date'] = utcToDate(r['Report_Date_Time']) 

            sortedReports = sorted( reports, key=itemgetter('date') )

            for r in sortedReports:
                if type(r['Report_Date_Time']) == datetime.datetime:
                    r['Report_Date_Time'] = r['Report_Date_Time'].isoformat()

            assert len(reports) == len(sortedReports)
            
            assert len(sortedReports) > 0
            indx = 0
            firstRep =  sortedReports[indx]
            while not 'breast' in firstRep['Report_Text'].lower() and indx < len(sortedReports) -1:
                indx +=1
                firstRep =  sortedReports[indx]
            
            time = firstRep['Report_Date_Time'].split("T")[0]

            passes = filt(firstRep, atypias,cancer)
            queryIndx = indx

            def crit():
                passBool = passes == True and sortedReports[queryIndx]['date'].year < 2010 and yearFilt
                repBool = passes == 'benign' #or passBool
                return repBool and queryIndx < len(sortedReports) -1

            while  crit():
                queryIndx +=1
                passes = filt(sortedReports[queryIndx], atypias,cancer)

            if passes == True :

                #pdb.set_trace()
                if sortedReports[queryIndx]['date'].year >= 2010 and yearFilt:
                    continue
                epId = sortedReports[queryIndx]["EpisodeID"]
                concurrentCancr = False
                def inRange(r):
                    return abs((r['date'] - sortedReports[queryIndx]['date']).days) < 183
                concReps = [r for r in sortedReports if inRange(r)]
                for r in concReps:
                    conc =filt(r, atypias, cancer)
                    if conc == False:
                        concurrentCancr = True

                if not concurrentCancr:
                    results.append( (mrn, time) ) 
                    resultRecords.extend([r for r in sortedReports if 'breast' in r['Report_Text'].lower()])
                    resultFirstRecs.append(sortedReports[queryIndx])


            assert len(set([r[0] for r in results])) == len(results)
        print "-------------"
        print "query", exportPath
        print "Number of Fitting query", len(results)
        print "Num MRNs", len( set([r['MRN'] for r in resultRecords] ))
        print "Number of Records", len(resultRecords)

        for r in resultRecords:
            if "ruleBreastSide" in r:
                del r["ruleBreastSide"]

        p.dump(resultRecords, open('atypiaExport.p','wb'))
        resultRecords = postProcessRules(resultRecords)

        keys = [k for k in key_order_convention if k in resultRecords[0].keys()] + ['Report_Date_Time', 'MRN', 'EMPI']
        filtRecs = []
        for r in resultRecords:
            filtR = {}
            for k in r:
                if k in keys:
                    filtR[k] = r[k]
            filtRecs.append(filtR)
        resultRecords = filtRecs

        updateAccesDB(resultRecords, exportPath)

if __name__ == "__main__":
    main()


