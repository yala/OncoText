import cPickle as p
import sys, os
sys.path.append("..")
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
            if str(r[c]) == '1':
                return True
        else:
            if c in r:
                return True
    return False


## Runs enforces global constraints like ER/PR NA given no cancer
def postProcessRules(db_train):

    for r in db_train:
        if hasCat(r, const_cancers):
            r['cancer'] = '1'
        else:
            r['cancer'] = '0'
            if hasCat(r, const_atypias):
                r['atypia'] = '1'
            else:
                r['atypia'] = '0'

        if r['cancer'] == '0':
            for k in ['ER','PR','Her2Fish', 'ECE', 'LVI','BVI', 'PositiveLN', 'ITC']:
                r[k] = '9'

        for k in r.keys():
            if type(r[k]) is unicode:
                r[k] = r[k].encode('ascii','replace')

    return db_train



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
        
        sortedReports = sorted( reports, key=lambda x: x.get('Report_Date_Time', "") )

        mrns[mrn] = sortedReports

    return mrns    


def filt(report, validKeys, blackout):
       
    for diag in blackout:
        assert str(report[diag]) in ['1','0']
        if str(report[diag]) in ['1']:
            return False
    
    for diag in validKeys:
        assert str(report[diag]) in ['1','0']
        if str(report[diag]) in ['1']:
            return True
    
    return 'benign'


def updateAccesDB(reportDB, tableName):
   
    reportDB = postProcessRules(reportDB)
    print "Exporting", len(reportDB), "breast records to name", tableName

    db = MySQLdb.connect(host="localhost",user="root",passwd="nlpdb",db="reports")
    cur = db.cursor()
    try: 
        cur.execute("DROP TABLE "+ tableName)
    except Exception, e:
        pass

    cur.execute("CREATE TABLE "+tableName +" LIKE "+ reportsTableName)
    db.commit()
    dbKeys, placeholders = [k for k in columnKeys if k in reportDB[0]], ["%s" for i in columnKeys if i in reportDB[0]]
    

    print "Exporting breast records... to", tableName
    sql = ("insert into "+tableName+" ("+", ".join(dbKeys)+") VALUES ("+", ".join(placeholders)+")")
    #print reportDB[0]
    for report in reportDB:
        try:
            values = [report[k] for k in dbKeys]
        except Exception , e:
            print e
            print report.keys(), "but looking for keys", [k for k in dbKeys]
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
    db = [d for d in db if ((d['Organ'] == '1') and (('filename' not in d) or (d['filename'] not in os.listdir(EVALDIR))))]
    print "len seed DB", len(db)

    exportPaths = ["allFEAsTable", "allADHsTable", "allAtypiaTable", 
    "allAtypia2010Table", "allCancersTable"]

    yearFilts = [ False, False, False, True, False]

    all_cancer = [const_cancers, const_cancers, const_cancers, const_cancers, []]

    fea = ["FlatEpithelial"]
    adh = ["ADH"]

    all_atypias = [fea, adh, const_atypias, const_atypias, const_cancers]

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
                if 'Report_Date_Time' in r:
                    r['date'] = utcToDate(r['Report_Date_Time'])
                else:
                    r['date'] = utcToDate(r['Report_Date_TimePlusX'])
            sortedReports = sorted( reports, key=itemgetter('date') )

            for r in sortedReports:
                if 'Report_Date_Time' in r:
                    if type(r['Report_Date_Time']) == datetime.datetime:
                        r['Report_Date_Time'] = r['Report_Date_Time'].isoformat()
                else:
                    if type(r['Report_Date_TimePlusX']) == datetime.datetime:
                        r['Report_Date_TimePlusX'] = r['Report_Date_TimePlusX'].isoformat()


            assert len(reports) == len(sortedReports)
            
            assert len(sortedReports) > 0
            indx = 0
            firstRep = sortedReports[indx]
            
            if 'Report_Date_Time' in firstRep:
                time = firstRep['Report_Date_Time'].split("T")[0]
            else:
                time = firstRep['Report_Date_TimePlusX'].split("T")[0]

            passes = filt(firstRep, atypias,cancer)
            queryIndx = indx


            def crit():
                repBool = passes == 'benign' #or passBool
                return repBool and queryIndx < len(sortedReports) -1

            while crit():
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
                    resultRecords.extend([r for r in sortedReports])
                    resultFirstRecs.append(sortedReports[queryIndx])


            assert len(set([r[0] for r in results])) == len(results)
        print "-------------"
        print "query", exportPath
        print "Number of Fitting query", len(results)
        print "Num MRNs", len( set([r['MRN'] for r in resultRecords] ))
        print "Number of Records", len(resultRecords)
                
        if len(resultRecords) > 0:
            for r in resultRecords:
                if "ruleBreastSide" in r:
                    del r["ruleBreastSide"]

            p.dump(resultRecords, open('atypiaExport.p','wb'))

            keys = [k for k in diagnoses if k in resultRecords[0].keys()]
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


