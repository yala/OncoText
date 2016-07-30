import pickle as p
import openpyxl as xl
import sys
sys.path.append("..")
from constants import *

dateFields = ['Date of Surgery', 'Date of 2nd surgery', 'Date of 3rd surgery', 'Date of 1 st surgery',\
'Date of 2nd biopsy', 'Date of 1st biopsy', 'Date of 3rd biopsy' ]

def parseXLS():
    print "loading wb"
    wb = xl.load_workbook('redcap.xlsx')

    print "getting sheet"
    sheet = wb.get_active_sheet()

    data = []

    legendRowBool = True
    print "Getting iterator"
    legend = []
    for row in sheet.iter_rows():
        rowDict = {}
        for indx, col in enumerate(row):
            if legendRowBool:
                if not col.value in legend:
                    legend.append(col.value)
                else:
                    counter = 2
                    newName = str(counter) + " " + col.value
                    while newName in legend:
                        counter += 1
                        newName = str(counter) + " " + col.value
                    legend.append(newName)
            else:
                rowDict[legend[indx]] = col.value

        if not legendRowBool:
            data.append(rowDict)
        else:
            print 'processing legend row'

        legendRowBool = False
        
    print 'dumping'
    print "legend", legend
    p.dump(data, open('redcap.p', 'wb'))
    return data


def normalizeMRN(mrn):
    res = str(mrn).strip()
    while len(res) < 8:
        res = '0' + res
    return res


def preprocessDB(data):
    mrnDB = {}
    for rep in data:
        try:
            mrn = normalizeMRN(rep['Registry ID'])
        except Exception, e:
            print rep['Registry ID']
            continue

        rep['MRNPlusX'] = mrn

        if mrn in mrnDB:
            mrnDB[mrn].append(rep)
        else:
            mrnDB[mrn] = [rep]

    print "Number of unique MRNs in recap DB", len(mrnDB)
    p.dump(mrnDB, open('redcapMRNDB.p', 'wb'))

    return mrnDB

def findMatchingReports(db):
    pathMrns = {}
    pathReps = p.load(open('../'+outPath, 'rb'))
    for r in pathReps:
        pathMRN = normalizeMRN(r['MRNPlusX'])

        if pathMRN in pathMrns:
            pathMrns[pathMRN].append( r )
        else:
            pathMrns[pathMRN] = [r]

    joinedDB = {}
    misAlignedDates = []
    for mrn in db:
        if not mrn in pathMrns:
            year = db[mrn]['Diagnosis date'].year
            misAlignedDates.append(year)
            continue

        joinedDB[mrn] = {'hughes':pathMrns[mrn], 'taghian':db[mrn]}

    p.dump(joinedDB, open('redcapWithPathReps.p', 'wb'))

    print "Size of taghian hughes MRN overlap", len(joinedDB)
    print "Avg year of misaligned ", sum(misAlignedDates)/len(mis)
    return joinedDB


def buildDB(db, baseName, path):
    erDB = []
    relevantEvents = ['b.Primary Tumor', 'c.Event 1', 'd.Event 2', 'e.Event 3']

    #Investigative Counts
    countEasy = 0 
    countERs  = 0
    countPathReps = 0
    countRedCapEvents = 0
    countAtLeast1 = 0
    yetToPrintBool = True

    for mrn in db:
        pathReps =  db[mrn]['hughes']
        redcap   =  [d for d in db[mrn]['taghian'] if d['Event Name'] in relevantEvents]

        numERs = 0
        erIndx = 1
        newName = baseName
        for red in redcap:
            while newName in red and not red[newName] == None:
                numERs += 1
                erIndx += 1
                newName = str(erIndx)  + " " + baseName
        
        
        countPathReps += len(pathReps)
        countRedCapEvents += len(redcap)
        countERs += numERs
        if numERs >0:
            countAtLeast1 += 1
            if yetToPrintBool:
                print "Example"
                print pathReps[0]
                print redcap[0][baseName]
                yetToPrintBool = False
            pathReps[0][baseName] = redcap[0][baseName]
            erDB.append(pathReps[0])

        if len(pathReps) == numERs:
            countEasy += 1

    p.dump(erDB, open(path, 'wb'))
    print "Number of ER reps and path reps equiv", countEasy
    print "countPathReps", countPathReps
    print "countRedCapEvents", countRedCapEvents
    print "countERs", countERs
    print 'countAtLeast1', countAtLeast1

    print "Length of ER DB", len(erDB)
    return erDB

parseXLSBool = False
preprocessDBBool = True
findMatchingReportsBool = True
buildERDBBool = False
buildPRDBBool = False
buildHer2Bool = False

if __name__ == "__main__":
   
    if parseXLSBool:
        redcap = parseXLS()

    if preprocessDBBool:
        if not parseXLSBool:
            redcap = p.load(open('redcap.p', 'rb'))
        mrnDB = preprocessDB(redcap)

    if findMatchingReportsBool:
        if not preprocessDBBool:
            mrnDB = p.load(open('redcapMRNDB.p','rb'))
        joinedDB = findMatchingReports(mrnDB)
    
    if buildERDBBool:
        if not findMatchingReportsBool:
            joinedDB =  p.load(open('redcapWithPathReps.p', 'rb'))        
        erDB = buildDB(joinedDB, 'Estrogen Receptor - qualitative', 'erDB.p')

    if buildPRDBBool:
        if not findMatchingReportsBool and not buildERDBBool:
            joinedDB =  p.load(open('redcapWithPathReps.p', 'rb'))        
        prDB = buildDB(joinedDB, 'Progesterone receptor - qualitative', 'prDB.p')

    if buildHer2Bool:
        if not findMatchingReportsBool and not buildERDBBool and not buildPRDBBool:
            joinedDB =  p.load(open('redcapWithPathReps.p', 'rb'))
            her2DB = buildDB(joinedDB, 'Her2 (FISH)', 'her2DB.p')





