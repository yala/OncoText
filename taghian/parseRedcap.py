import pickle as p
import openpyxl as xl
import sys
sys.path.append("..")
from constants import *
import datetime

dateFields = ['Date of 1st biopsy', 'Date of 2nd biopsy',  'Date of 3rd biopsy', 'Date of 1 st surgery','Date of 2nd surgery', 'Date of 3rd surgery' ]
dateFieldsToIndx = {'Date of 1st biopsy':0, 'Date of 2nd biopsy':1,  'Date of 3rd biopsy':2, 'Date of 1 st surgery':3,'Date of 2nd surgery':4, 'Date of 3rd surgery':5 }

#Below is sequence of er/pr/her2 col names as they align to the order of biops as surgs above
erColSeq = ['Estrogen receptors - qualitative', 'Estrogen receptors ', '2 Estrogen receptors ', '2 Estrogen receptors - qualitative', '3 Estrogen receptors - qualitative', '4 Estrogen receptors - qualitative' ]
prColSeq = ['Progesterone receptors - qualitative', 'Progesterone receptors ', '2 Progesterone receptors ', '2 Progesterone receptors - qualitative', '3 Progesterone receptors - qualitative', '4 Progesterone receptors - qualitative']
her2ColSeq = ['Her2 (FISH)', '2 Her2 (FISH)', '3 Her2 (FISH)', '4 Her2 (FISH)', '5 Her2 (FISH)', '6 Her2 (FISH)']

def parseRedCapXLS():
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

def parseMapXLS():
    print "loading wb mp"
    wb = xl.load_workbook('redmap.xlsx')

    print "getting sheet"
    sheet = wb.get_active_sheet()

    data = {}

    legendRowBool = True
    print "Getting iterator"
    legend = []
    for row in sheet.iter_rows():
        rowDict = {}
        for indx, col in enumerate(row):
            if legendRowBool:
                legend.append(col.value)
            else:
                rowDict[legend[indx]] = col.value
        
        if not legendRowBool:
            newName = rowDict['Column name']

            if rowDict['Column name'] in data:
                counter = 2
                newName = str(counter) + " " + rowDict['Column name']
                while newName in data:
                    counter += 1
                    newName = str(counter) + " " + rowDict['Column name']

            
            data[newName] = { 'event':rowDict['Mapped to '], 'extraction feild': rowDict['type'] }

            assert legend == ['Column name', 'Mapped to ', 'comments', 'type']
        else:
            print 'processing legend row'

        legendRowBool = False
        
    print 'dumping redmap.p'
    print "legend", legend
    p.dump(data, open('redmap.p', 'wb'))
    return data


def normalizeMRN(mrn):
    res = str(mrn).strip()
    while len(res) < 8:
        res = '0' + res
    return res


def preprocessDB(data, save=False):
    mrnDB = {}
    for rep in data:

        mrn = normalizeMRN(rep['Registry ID'])
 
        rep['MRNPlusX'] = mrn
        if mrn in mrnDB:
            mrnDB[mrn].append(rep)
        else:
            mrnDB[mrn] = [rep]

    print "Number of unique MRNs in recap DB", len(mrnDB)

    if save:
        p.dump(mrnDB, open('redcapMRNDB.p', 'wb'))

    return mrnDB

def findMatchingReports(db, save=False):
    print "Len redcap DB", len(db)

    lengthsDB = {}
    pathMrns = {}
    pathReps = p.load(open('../'+outPath, 'rb'))

    for r in pathReps:
        pathMRN = normalizeMRN(r['MRNPlusX'])
        r['Report_Date'] = r['Report_Date_TimePlusX'] + datetime.timedelta(-13)


        if pathMRN in pathMrns:
            pathMrns[pathMRN].append( r )
        else:
            pathMrns[pathMRN] = [r]

    print "Updating lengthsDB with num Path reps per patient"
    for mrn in pathMrns:
        lengthsDB[mrn] = [ len(pathMrns[mrn]), 0]


    joinedDB = {}
    misAlignedDates = []
    countAligned = 0
    for mrn in db:
        redcapReps = db[mrn]
        if mrn in pathMrns:
            for rowIndx, r in enumerate(redcapReps):
                redCapDates = [r[d] for d in dateFields if not r[d] == None ]

                for pathRep in pathMrns[mrn]:
                    if pathRep['Report_Date'] in redCapDates:
                        pathRep['taghainColIndx'] = redCapDates.index(pathRep['Report_Date'])
                        pathRep['taghainRowIndx'] = rowIndx
                        countAligned += 1

                lengthsDB[mrn][1] += len(redCapDates)

            joinedDB[mrn] = {'hughes':pathMrns[mrn], 'taghian':db[mrn], 'lengths':lengthsDB[mrn]}

    
    if save:
        p.dump(joinedDB, open('redcapWithPathReps.p', 'wb'))

    print "Size of taghian hughes MRN overlap", len(joinedDB)
    print "Count Aligned ", countAligned
    return joinedDB


## Suport building dbs from path reps (aligned by taghian index in the path rep) for er/pr/her2
## This is because I have col to index dictionaries to figure out which date led to that result
## Input DB is joinedDB
## Key { MRN} -> {'taghian': [recap events], 'hughes':[pathReps], 'lengths':[ countRedCapEvents, count pathReps]}
def buildDB(db, redmap):
    outDB = {}
    types = set([redmap[m]['extraction feild'] for m in redmap if redmap[m]['event'] in lauraDictToIndx and not redmap[m]['extraction feild'] == None])

    assert not None in types
    for extract in types:
        outDB[extract] = []
    print "Types are", types

    colSeqs = {}
    for extract in types:
        colSeqs[extract] = ['Placeholder'] * len(lauraDictToIndx)
        relevantCols = [ (m, redmap[m]['event']) for m in redmap if redmap[m]['extraction feild'] == extract]
        for col, target in relevantCols:
            indx = lauraDictToIndx[target]
            colSeqs[extract][indx] = col


    assert colSeqs['ER'] == erColSeq
    assert colSeqs['PR'] == prColSeq
    assert colSeqs['Her2 (Fish)'] == her2ColSeq

    #Investigative Counts
    yetToPrintBool = True

    for mrn in db:

        pathReps =  db[mrn]['hughes']
        redcap   =  db[mrn]['taghian']
        for extraction in types:
            colSeq =  colSeqs[extraction]

            for rep in pathReps:
                if 'taghainColIndx' in rep and 'taghainRowIndx' in rep:
                    redcapIndx = rep['taghainRowIndx']
                    colField = colSeq[ rep['taghainColIndx'] ]
                    ## Not all fields apply to all path reps and all surg reps
                    ## If the field is a placeholder, it means that this colIndx (ie type of report the path report it)
                    ## doesn't hold the extraction
                    if colField == 'Placeholder':
                        continue
                    rep[extraction] = redcap[redcapIndx][colField]
                    if not rep[extraction] == None:
                        outDB[extraction].append(rep)
                else:
                    continue

    p.dump(outDB, open('allExtractionDBs.p', 'wb'))
    for extraction in types:
        print "Number of ",extraction," reps and path reps equiv", len(outDB[extraction])
    print "Num extractions", len(outDB)
    print "num extractions over 500 reps", len([ extraction for extraction in types if len(outDB[extraction]) > 500 and extraction not in filtOutList])
    print [ (extraction, len(outDB[extraction])) for extraction in types if len(outDB[extraction]) > 500 and extraction not in filtOutList]

    print [ extraction for extraction in types if len(outDB[extraction]) > 500 and extraction not in filtOutList]

    return outDB

parseXLSBool = False
preprocessDBBool = False
findMatchingReportsBool = False
buildDBsBool = True

if __name__ == "__main__":
   
    if parseXLSBool:
        redmap = parseMapXLS()
        redcap = parseRedCapXLS()

    if preprocessDBBool:
        print 'Running preprocessDB'
        if not parseXLSBool:
            print "Loading redcap file and map"
            redcap = p.load(open('redcap.p', 'rb'))
            redmap = p.load(open('redmap.p', 'rb'))
        mrnDB = preprocessDB(redcap, True)

    if findMatchingReportsBool:
        print "Running findMatchingReports"
        if not preprocessDBBool:
            print "Loading redcapMRNDB.p"
            mrnDB = p.load(open('redcapMRNDB.p','rb'))
        joinedDB = findMatchingReports(mrnDB, True)
    
    if buildDBsBool:
        if not findMatchingReportsBool:
            joinedDB =  p.load(open('redcapWithPathReps.p', 'rb'))        
            redmap = p.load(open('redmap.p', 'rb'))
        dBs = buildDB(joinedDB, redmap)



