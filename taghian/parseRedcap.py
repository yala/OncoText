import pickle as p
import openpyxl as xl
import sys
sys.path.append("..")
from constants import *
import datetime
from createEpisodes import validateRepsDB
from operator import itemgetter


dateFields = ['Date of 1st biopsy', 'Date of 2nd biopsy',  'Date of 3rd biopsy', 'Date of 1 st surgery','Date of 2nd surgery', 'Date of 3rd surgery' ]
dateFieldsToIndx = {'Date of 1st biopsy':0, 'Date of 2nd biopsy':1,  'Date of 3rd biopsy':2, 'Date of 1 st surgery':3,'Date of 2nd surgery':4, 'Date of 3rd surgery':5}

#Below is sequence of er/pr/her2 col names as they align to the order of biops as surgs above
erColSeq = ['Estrogen receptors - qualitative', 'Estrogen receptors ', '2 Estrogen receptors ', '2 Estrogen receptors - qualitative', '3 Estrogen receptors - qualitative', '4 Estrogen receptors - qualitative' ]
prColSeq = ['Progesterone receptors - qualitative', 'Progesterone receptors ', '2 Progesterone receptors ', '2 Progesterone receptors - qualitative', '3 Progesterone receptors - qualitative', '4 Progesterone receptors - qualitative']
her2ColSeq = ['Her2 (FISH)', '2 Her2 (FISH)', '3 Her2 (FISH)', '4 Her2 (FISH)', '5 Her2 (FISH)', '6 Her2 (FISH)']
gradeColSeq = ['Final Tumor Grade']



def parseXLS(inp, out):
    print "loading wb"
    wb = xl.load_workbook(inp)

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
                    newName = col.value
                    legend.append(newName)
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
    p.dump(data, open(out, 'wb'))
    return data

def parseRedCapXLS():
    return parseXLS('redcap.xlsx', 'redcap.p')
   
def parseGradesLS():
    grades1 =  parseXLS('../externalDataSources/Grades.xlsx', 'gradesXls.p')
    grades2 =  parseXLS('../externalDataSources/Grades_2.xlsx', 'gradesXls2.p')
    grades = grades1 + grades2
    print "preprocessing grades db"
    textToGrade = {}
    print len(grades)
    for row in grades:
        textToGrade[row['Report_Text'] ] = row['TumorGrade']

    print len(textToGrade)

    p.dump(textToGrade, open('grades.p','wb'))

    return textToGrade


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

            if newName == 'Oncotype score':
                assert rowDict['Mapped to '] == 'Oncotype'

            if not legend == ['Column name', 'Mapped to ', 'comments', 'type']:
                print legend
                raw_input()

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

def findMatchingReports(db, pathReps, save=False):
    print "Len redcap DB", len(db)

    lengthsDB = {}
    pathMrns = {}

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
                redCapDates = [r[d] for d in dateFields]
                sideDict = {'Left':0, "Right":1}
                redSide = redcapReps[rowIndx]['Side']
                if redSide in sideDict:
                    redSide = sideDict[redSide]
                else:
                    continue

                for pathRep in pathMrns[mrn]:
                    if pathRep['Report_Date'] in redCapDates and pathRep['BreastSide'] == redSide:
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


## Take dict of {extract} -> [ reports ]
## Print label dist with count of each label
def printLabelDist(db):
    for extraction in db:
        if 'date' in extraction.lower():
            continue
        print "--------------------------------------"
        print "Extraction", extraction
        reps = db[extraction]
        possLabels = set([r[extraction] for r in reps])
        labelCounts = {}
        for label in possLabels:
            labelCounts[label] = len([ r for r in reps if r[extraction] == label ])
        print labelCounts
    print "*******************************************"

def getColSeqs(redmap, outDB):
    ## Get list of extractions under my name. Similar to diagnoses pre-filtering
    types = set([redmap[m]['extraction feild'] for m in redmap 
        if (redmap[m]['event'] in lauraDictToIndx or redmap[m]['extraction feild'] in maxedOutDictToIndx)
        and not redmap[m]['extraction feild'] == None]) 

    assert 'Oncotype score' in types
    assert not None in types

    for extract in types:
        outDB[extract] = []
    print "Types are", types

    for extract in externalList:
        outDB[extract] = []

    ## Note Structure of redmap is as follows: "Col in Redcape " -> ['Event': which biop or surgery is this. is it maxed out?, 'ExtractionFeild': My name for this extraction. 
    ## Allows to collapse different names to a single type]

    colSeqs = {}
    for extract in types:
        if extract in maxedOutList:
            colSeqs[extract] = [ m for m in redmap if redmap[m]['extraction feild'] == extract ]
            assert len(colSeqs[extract]) == 1
        else:
            colSeqs[extract] = ['Placeholder'] * len(lauraDictToIndx)
            relevantCols = [ (m, redmap[m]['event']) for m in redmap if redmap[m]['extraction feild'] == extract]
            for col, target in relevantCols:
                indx = lauraDictToIndx[target]
                colSeqs[extract][indx] = col


    assert colSeqs['ER'] == erColSeq
    assert colSeqs['PR'] == prColSeq
    assert colSeqs['Her2 (Fish)'] == her2ColSeq
    return colSeqs, types

def processRedcapData(db, colSeqs, types, outDB, outDBRepIds, toSee, seen):
    for mrn in db:

        pathReps =  db[mrn]['hughes']
        redcap   =  db[mrn]['taghian']

        ## For normal extractions that line up to a specific report,
        ## we iterate through reps, find corresponding col for that extraction
        ## for that report and produce DB
        for rep in pathReps:
            for extraction in types:
                colSeq =  colSeqs[extraction]

                if 'taghainColIndx' in rep and 'taghainRowIndx' in rep:
                    redcapIndx = rep['taghainRowIndx']
                    colIndx = rep['taghainColIndx'] 
                    if extraction in maxedOutList:
                        continue
                    else:
                        colField = colSeq[colIndx ]
                        if not rep['Report_Date'] == redcap[redcapIndx][dateFields[colIndx]]:
                            print "ERROR"
                            print rep['Report_Date'] ,redcap[redcapIndx][dateFields[colIndx]]
                            print "colIndx, rowIndx:", colIndx , ",", redcapIndx
                            print "Redcap[redcapIndx] is", redcap[redcapIndx]
                            print "Redcap is", redcap
                            assert False

                        ## Not all fields apply to all path reps and all surg reps
                        ## If the field is a placeholder, it means that this colIndx (ie type of report the path report it)
                        ## doesn't hold the extraction
                        if colField == 'Placeholder':
                            continue
                        rep[extraction] = redcap[redcapIndx][colField]
                        if not rep[extraction] == None:
                            outDB[extraction].append(rep)
                            if not rep['ReportID'] in outDBRepIds:
                                outDBRepIds[rep['ReportID']] = {} 

                            assert not extraction  in outDBRepIds[rep['ReportID']]  
                            outDBRepIds[rep['ReportID']][extraction] = rep[extraction]

                            if extraction in toSee and seen[extraction] < 10:
                                 seen[extraction] += 1
                                 print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                                 print "Extraction type", extraction
                                 print rep[reportTextKey]
                                 print rep[extraction]
                                 raw_input()

                        else:
                            continue
    return False

def parseOncoScore(score):
    if score < 18:
        return 'Low risk'
    elif score <= 30:
        return 'High risk'
    else: 
        return 'High risk'
## Suport building dbs from path reps (aligned by taghian index in the path rep) for er/pr/her2
## This is because I have col to index dictionaries to figure out which date led to that result
## Input DB is joinedDB
## Key { MRN} -> {'taghian': [recap events], 'hughes':[pathReps], 'lengths':[ countRedCapEvents, count pathReps]}

def processGradeData(grades, allPathReps, outDB, outDBRepIds):
    for rep in allPathReps:
        ## Now we merge in external data, like grade
        if rep['Report_Text'] in grades:
            grade = grades[rep['Report_Text']].strip()[0].upper() + grades[rep['Report_Text']].strip()[1:]
            rep['TumorGrade'] = grade
            outDB['TumorGrade'].append(rep)
            if not rep['ReportID'] in outDBRepIds:
                outDBRepIds[rep['ReportID']] = {}
            outDBRepIds[rep['ReportID']]['TumorGrade'] = rep['TumorGrade']
    return False

def processOncoScores(db, colSeqs, allPathReps, outDB, outDBRepIds, toSee, seen ):
    allPathReps = p.load(open('../reportDB.p','rb'))
    ## Process external oncoscores
    loadBool = True
    extKey = 'Dx Score'
    if loadBool:
        externalPath =  '../externalDataSources/oncoscore.xlsx'
        extOncos =  parseXLS(externalPath, "oncoscoreList.p")   
        mrnToOnc = {}
        for row in extOncos:
            mrn = normalizeMRN(row['MRNPlusX'])
            if not mrn in mrnToOnc:
                mrnToOnc[mrn] = []    
            mrnToOnc[mrn].append(row)
        p.dump(mrnToOnc, open('oncoscoreDb.p','wb'))
    else:
        mrnToOnc = p.load(open('oncoscoreDb.p','rb'))
    print "len mrnToOnc", len(mrnToOnc), type(mrnToOnc.keys()[0])

    #process redcap
    for mrn in db:

        pathReps =  db[mrn]['hughes']
        redcap   =  db[mrn]['taghian']

        ## For normal extractions that line up to a specific report,
        ## we iterate through reps, find corresponding col for that extraction
        ## for that report and produce DB
        for rep in reversed(pathReps):
            for extraction in maxedOutList:
                if not extraction == 'Oncotype score':
                    continue

                colSeq =  colSeqs[extraction]

                if not ('taghainColIndx' in rep and 'taghainRowIndx' in rep):
                    continue

                redcapIndx = rep['taghainRowIndx']
                    
                colField = colSeq[0] ## maxed out reps have length one lists

                if redcap[redcapIndx][colField] == None:
                    continue

                if redcap[redcapIndx]['Oncotype date'] == None or rep['Report_Date_TimePlusX'] > redcap[redcapIndx]['Oncotype date']:
                    continue

                rep[extraction] = parseOncoScore(redcap[redcapIndx][colField])


                ##For oncoscore, assert that report is a lumpectomy
                
                outDB[extraction].append(rep)
                if not rep['ReportID'] in outDBRepIds:
                    outDBRepIds[rep['ReportID']] = {} 

                assert not extraction  in outDBRepIds[rep['ReportID']]  
                outDBRepIds[rep['ReportID']][extraction] = rep[extraction]

                if extraction in toSee and seen[extraction] < 0:
                     seen[extraction] += 1
                     print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                     print "Extraction type", extraction
                     print rep[reportTextKey]
                     print rep[extraction]
                     raw_input()

    #process ext
    extraction = 'Oncotype score'
    for mrnOnc in mrnToOnc:
        oncs = mrnToOnc[mrnOnc]

        relevantReps = [r for r in allPathReps if normalizeMRN(r['MRNPlusX']) == normalizeMRN(mrnOnc)]
        if not len(relevantReps)>0:
            continue

        relevantReps = sorted(relevantReps, key=itemgetter('Report_Date_TimePlusX') )

        for onc in oncs:
            oncDate = onc['SpecimenReceivedPlusX']
            onc = onc[extKey]

            for rep in reversed(relevantReps):
                if oncDate == None or rep['Report_Date_TimePlusX'] > oncDate:# or not rep['BiopsyType']=='Excision':
                    continue

                #Skip if annotated by taghain
                if rep['ReportID'] in outDBRepIds and extraction in [rep['ReportID']]:
                    continue

                ## Now at most recent excision that has no taghian annotation
                if 'Oncotype score' in rep:
                    continue

                rep[extraction] = parseOncoScore(onc)
                
                outDB[extraction].append(rep)
                if not rep['ReportID'] in outDBRepIds:
                    outDBRepIds[rep['ReportID']] = {} 

                if extraction  in outDBRepIds[rep['ReportID']]:
                    continue
                outDBRepIds[rep['ReportID']][extraction] = rep[extraction]

                if extraction in toSee and seen[extraction] < 10:
                     seen[extraction] += 1
                     print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
                     print "Extraction type", extraction
                     print rep[reportTextKey]
                     print rep[extraction]
                     raw_input()
                break
    print "num oncoscores", len(outDB[extraction])
    raw_input()
    return False

def buildDB(db, grades, redmap, allPathReps, debug = False):
    outDBReps = []
    outDBRepIds = {}
    outDB = {}
    labelDist = {}
    ## Use this for debugging
    seen = {}
    toSee = ['Oncotype score']
    for s in toSee:
        seen[s] = 0

    colSeqs, types = getColSeqs(redmap, outDB)

    #Investigative Counts
    yetToPrintBool = True


    processRedcapData(db, colSeqs, types, outDB, outDBRepIds, toSee, seen)
    processGradeData(grades, allPathReps, outDB, outDBRepIds)
    processOncoScores(db, colSeqs, allPathReps, outDB, outDBRepIds, toSee, seen )

    ## Now we print label distrubtions for generating maps and in constants
    printLabelDist(outDB)
    assert len(outDBReps) == 0
                
    for report in allPathReps:
        if report['ReportID'] in outDBRepIds:
            validateRepsDB( [report], True )
            if report['DCIS'] == 'Checked':
                assert False

            report['TaghianGold'] = 1
            for extraction in outDBRepIds[report['ReportID']]:
                assert MODE == "TAGHIAN" and (extraction in types or extraction in externalList)
                if extraction in report: ## This is to catch things like DCIS which are both in Taghian and Hughes dB
                    continue
                else:
                    report[extraction] = outDBRepIds[report['ReportID']][extraction]



                # assert report['Report_Text'] in [r['Report_Text'] for r in  outDB[extraction]]


            assert 'TaghianGold' in report and report['TaghianGold'] == 1
            assert len( [t for t in list(types)+externalList if t in report ] ) > 0
            validateRepsDB( [report], True, True )
            outDBReps.append( report )
                

    p.dump(outDBReps, open('allExtractionReps.p', 'wb'))
    p.dump(outDB, open('allExtractionDBs.p', 'wb'))
    for extraction in outDB:
        print "Number of ",extraction," reps and path reps equiv", len(outDB[extraction])
    print "Num extractions", len(outDB)
    print "num extractions over 500 reps", len([ extraction for extraction in types if len(outDB[extraction]) > 500 and extraction not in filtOutList])
    print "Num path reps", len(outDBReps)
    print "Num path rep IDs", len(outDBRepIds)
    assert len(outDBReps) > 5000
    assert len(outDBRepIds) > 5000

    return outDB, outDBReps


## redReps: Paths aligned with redcap. All pathreps should have tahianGold = 1
## pathReps: all 100k pathreps
## Objective redump (ReportsDB) and essentially merge redReps with pathReps
def exportRepDB(redReps, pathReps):
    ## First build Dict of redReps counting on aligning MRN, Inst, Report_Text, Date, Breaside
    ## Enforce no dups
    ## go thoguh path reps, if find something in dict, replace and edump

    #Build Dict
    redDict = {}
    for red in redReps:
        repId = red['ReportID']
        redDict[repId] = red

    for indx, path in enumerate(pathReps):
        pathId = path['ReportID']
        if pathId in redDict:
            pathReps[indx] = redDict[pathId]

    if not len(redReps)  == len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1]):
        print 'len(redReps)', len(redReps)
        print "len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1])", len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1])
    assert len(redReps) == len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1])

    p.dump(pathReps, open('../reportDB+red.p','wb'))    
    


parseXLSBool = False
parseMapBool = False
parseExternal = False
preprocessDBBool = False
findMatchingReportsBool = False
buildDBsBool = True
exportToRepsDBBool= True

if __name__ == "__main__":
    allPathReps = p.load(open('../reportDB.p', 'rb'))
    # print "Validate all path", '../reportDB.p'
    # validateRepsDB(allPathReps, True)


    if parseXLSBool:
        redcap = parseRedCapXLS()

    if parseMapBool:
        redmap = parseMapXLS()


    if parseExternal:
        grades = parseGradesLS()

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
        joinedDB = findMatchingReports(mrnDB, allPathReps, True)
    
    if buildDBsBool:
        if findMatchingReportsBool:
            allPathReps = p.load(open('../reportDB.p', 'rb'))

        if not findMatchingReportsBool:
            joinedDB =  p.load(open('redcapWithPathReps.p', 'rb'))
        if not parseXLSBool:
            redmap = p.load(open('redmap.p', 'rb'))
        if not parseExternal:
            grades = p.load(open('grades.p','rb'))
        dBs, redReps = buildDB(joinedDB, grades, redmap, allPathReps,  True)

    if exportToRepsDBBool:
        if not buildDBsBool:
            redReps =     p.load(open('allExtractionReps.p', 'rb'))
        print "Validate red path reps", 'allExtractionReps.p'
        validateRepsDB(redReps, True, True)
        exportRepDB(redReps, allPathReps)



