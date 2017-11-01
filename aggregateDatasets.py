import openpyxl as xl
import sys
sys.path.append("..")
sys.path.append("../buildNewDataset")
from constants import *
import datetime
from createEpisodes import validateRepsDB
from operator import itemgetter
from anonymize import deIdenText
# from docx import Document
import cPickle as p
import xmltodict


# dateFields = ['Date of 1st biopsy', 'Date of 2nd biopsy',  'Date of 3rd biopsy', 'Date of 1 st surgery','Date of 2nd surgery', 'Date of 3rd surgery' ]
# dateFieldsToIndx = {'Date of 1st biopsy':0, 'Date of 2nd biopsy':1,  'Date of 3rd biopsy':2, 'Date of 1 st surgery':3,'Date of 2nd surgery':4, 'Date of 3rd surgery':5}

# #Below is sequence of er/pr/her2 col names as they align to the order of biops as surgs above
# erColSeq = ['Estrogen receptors - qualitative', 'Estrogen receptors ', '2 Estrogen receptors ', '2 Estrogen receptors - qualitative', '3 Estrogen receptors - qualitative', '4 Estrogen receptors - qualitative' ]
# prColSeq = ['Progesterone receptors - qualitative', 'Progesterone receptors ', '2 Progesterone receptors ', '2 Progesterone receptors - qualitative', '3 Progesterone receptors - qualitative', '4 Progesterone receptors - qualitative']
# her2ColSeq = ['Her2 (FISH)', '2 Her2 (FISH)', '3 Her2 (FISH)', '4 Her2 (FISH)', '5 Her2 (FISH)', '6 Her2 (FISH)']
# gradeColSeq = ['Final Tumor Grade']



def parseXLS(inp, out, legend=None):
    wb = xl.load_workbook(inp)

    sheet = wb.get_active_sheet()

    data = []

    legendRowBool = legend == None
    legend = [] if legend == None else legend
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
    

        legendRowBool = False
        
    p.dump(data, open(out, 'wb'))
    return data

# def parseDoc(inp, out, legend=None):
#     print "loading wb"
#     doc = Document(inp)

#     table = doc.tables[0]
#     data = []

#     legendRowBool = legend == None
#     print "Getting iterator"
#     legend = [] if legend == None else legend
#     for row in table.rows:
#         rowDict = {}
#         for indx, cell in enumerate(row.cells):
#             if legendRowBool:
#                 if not cell.text in legend:
#                     newName = cell.text
#                     legend.append(newName)
#                 else:
#                     counter = 2
#                     newName = str(counter) + " " + cell.text
#                     while newName in legend:
#                         counter += 1
#                         newName = str(counter) + " " + cell.text
#                     legend.append(newName)
#             else:
#                 rowDict[legend[indx]] = cell.text

#         if not legendRowBool:
#             data.append(rowDict)
#         else:
#             print 'processing legend row'
#         legendRowBool = False
        
#     print 'dumping'
#     print "legend", legend
#     p.dump(data, open(out, 'wb'))
#     print "num rows in ",inp, "is",len(data)
#     return data

# def parseRedCapXLS():
#     return parseXLS('data/redcap.xlsx', 'data/redcap.p')
   
# def parseGradesLS():
#     grades1 =  parseXLS('../externalDataSources/Grades.xlsx', 'data/gradesXls.p')
#     grades2 =  parseXLS('../externalDataSources/Grades_2.xlsx', 'data/gradesXls2.p')
#     grades = grades1 + grades2
#     print "preprocessing grades db"
#     textToGrade = {}
#     print len(grades)
#     for row in grades:
#         textToGrade[row['Report_Text'] ] = row['TumorGrade']

#     print len(textToGrade)

#     p.dump(textToGrade, open('data/grades.p','wb'))

#     return textToGrade


# def parseMapXLS():
#     print "loading wb mp"
#     wb = xl.load_workbook('data/redmap.xlsx')

#     print "getting sheet"
#     sheet = wb.get_active_sheet()

#     data = {}

#     legendRowBool = True
#     print "Getting iterator"
#     legend = []
#     for row in sheet.iter_rows():
#         rowDict = {}
#         for indx, col in enumerate(row):
#             if legendRowBool:
#                 legend.append(col.value)
#             else:
#                 rowDict[legend[indx]] = col.value
        
#         if not legendRowBool:
#             newName = rowDict['Column name']
#             if rowDict['Column name'] in data:
#                 counter = 2
#                 newName = str(counter) + " " + rowDict['Column name']
#                 while newName in data:
#                     counter += 1
#                     newName = str(counter) + " " + rowDict['Column name']

            
#             data[newName] = { 'event':rowDict['Mapped to '], 'extraction feild': rowDict['type'] }

#             if newName == 'Oncotype score':
#                 assert rowDict['Mapped to '] == 'Oncotype'

#             if not legend == ['Column name', 'Mapped to ', 'comments', 'type']:
#                 print legend

#         else:
#             print 'processing legend row'

#         legendRowBool = False
        
#     print 'dumping redmap.p'
#     print "legend", legend
#     p.dump(data, open('data/redmap.p', 'wb'))
#     return data


# def normalizeMRN(mrn):
#     res = str(mrn).strip()
#     while len(res) < 8:
#         res = '0' + res
#     return res


# def preprocessDB(data, save=False):
#     mrnDB = {}
#     for rep in data:

#         mrn = normalizeMRN(rep['Registry ID'])
 
#         rep['MRNPlusX'] = mrn
#         if mrn in mrnDB:
#             mrnDB[mrn].append(rep)
#         else:
#             mrnDB[mrn] = [rep]

#     print "Number of unique MRNs in recap DB", len(mrnDB)

#     if save:
#         p.dump(mrnDB, open('data/redcapMRNDB.p', 'wb'))

#     return mrnDB

# def findMatchingReports(db, pathReps, save=False):
#     print "Len redcap DB", len(db)

#     lengthsDB = {}
#     pathMrns = {}

#     for r in pathReps:
#         pathMRN = normalizeMRN(r['MRNPlusX'])
#         try:
#             r['Report_Date'] = r['Report_Date_TimePlusX'] + datetime.timedelta(-13)
#         except Exception, e:
#             print e
#             print r['Report_Date_TimePlusX']
#             raw_input()

#         if pathMRN in pathMrns:
#             pathMrns[pathMRN].append( r )
#         else:
#             pathMrns[pathMRN] = [r]

#     print "Updating lengthsDB with num Path reps per patient"
#     for mrn in pathMrns:
#         lengthsDB[mrn] = [ len(pathMrns[mrn]), 0]

#     joinedDB = {}
#     misAlignedDates = []
#     countAligned = 0
#     for mrn in db:
#         redcapReps = db[mrn]
#         if mrn in pathMrns:
#             for rowIndx, r in enumerate(redcapReps):
#                 redCapDates = [r[d] for d in dateFields]
#                 sideDict = {'Left':'LEFT', "Right":'RIGHT'}
#                 redSide = redcapReps[rowIndx]['Side']
#                 if redSide in sideDict:
#                     redSide = sideDict[redSide]
#                 else:
#                     continue

#                 for pathRep in pathMrns[mrn]:
#                     if pathRep['Report_Date'] in redCapDates and pathRep['BreastSide'] == redSide:
#                         pathRep['taghainColIndx'] = redCapDates.index(pathRep['Report_Date'])
#                         pathRep['taghainRowIndx'] = rowIndx
#                         countAligned += 1

#                 lengthsDB[mrn][1] += len(redCapDates)

#             joinedDB[mrn] = {'hughes':pathMrns[mrn], 'taghian':db[mrn], 'lengths':lengthsDB[mrn]}

    
#     if save:
#         p.dump(joinedDB, open('data/redcapWithPathReps.p', 'wb'))

#     print "Size of taghian hughes MRN overlap", len(joinedDB)
#     print "Count Aligned ", countAligned
#     return joinedDB


# ## Take dict of {extract} -> [ reports ]
# ## Print label dist with count of each label
# def printLabelDist(db):
#     for extraction in db:
#         if 'date' in extraction.lower():
#             continue
#         print "--------------------------------------"
#         print "Extraction", extraction
#         reps = db[extraction]
#         possLabels = set([r[extraction] for r in reps])
#         labelCounts = {}
#         for label in possLabels:
#             labelCounts[label] = len([ r for r in reps if r[extraction] == label ])
#         print labelCounts
#     print "*******************************************"

# def getColSeqs(redmap, outDB):
#     ## Get list of extractions under my name. Similar to diagnoses pre-filtering
#     types = set([redmap[m]['extraction feild'] for m in redmap 
#         if (redmap[m]['event'] in lauraDictToIndx or redmap[m]['extraction feild'] in maxedOutDictToIndx)
#         and not redmap[m]['extraction feild'] == None]) 

#     assert 'Oncotype score' in types
#     assert not None in types

#     for extract in types:
#         outDB[extract] = []
#     print "Types are", types

#     for extract in externalList:
#         outDB[extract] = []

#     ## Note Structure of redmap is as follows: "Col in Redcape " -> ['Event': which biop or surgery is this. is it maxed out?, 'ExtractionFeild': My name for this extraction. 
#     ## Allows to collapse different names to a single type]

#     colSeqs = {}
#     for extract in types:
#         if extract in maxedOutList:
#             colSeqs[extract] = [ m for m in redmap if redmap[m]['extraction feild'] == extract ]
#             assert len(colSeqs[extract]) == 1
#         else:
#             colSeqs[extract] = ['Placeholder'] * len(lauraDictToIndx)
#             relevantCols = [ (m, redmap[m]['event']) for m in redmap if redmap[m]['extraction feild'] == extract]
#             for col, target in relevantCols:
#                 indx = lauraDictToIndx[target]
#                 colSeqs[extract][indx] = col


#     assert colSeqs['ER'] == erColSeq
#     assert colSeqs['PR'] == prColSeq
#     assert colSeqs['Her2Fish'] == her2ColSeq
#     return colSeqs, types

# def processRedcapData(db, colSeqs, types, outDB, outDBRepIds, toSee, seen):
#     for mrn in db:

#         pathReps =  db[mrn]['hughes']
#         redcap   =  db[mrn]['taghian']

#         ## For normal extractions that line up to a specific report,
#         ## we iterate through reps, find corresponding col for that extraction
#         ## for that report and produce DB
#         for rep in pathReps:
#             for extraction in types:
#                 colSeq =  colSeqs[extraction]

#                 if 'taghainColIndx' in rep and 'taghainRowIndx' in rep:
#                     redcapIndx = rep['taghainRowIndx']
#                     colIndx = rep['taghainColIndx'] 
#                     if extraction in maxedOutList:
#                         continue
#                     else:
#                         colField = colSeq[colIndx ]
#                         if not rep['Report_Date'] == redcap[redcapIndx][dateFields[colIndx]]:
#                             print "ERROR"
#                             print rep['Report_Date'] ,redcap[redcapIndx][dateFields[colIndx]]
#                             print "colIndx, rowIndx:", colIndx , ",", redcapIndx
#                             print "Redcap[redcapIndx] is", redcap[redcapIndx]
#                             print "Redcap is", redcap
#                             assert False

#                         ## Not all fields apply to all path reps and all surg reps
#                         ## If the field is a placeholder, it means that this colIndx (ie type of report the path report it)
#                         ## doesn't hold the extraction
#                         if colField == 'Placeholder':
#                             continue
#                         rep[extraction] = redcap[redcapIndx][colField]
#                         if not rep[extraction] == None:
#                             outDB[extraction].append(rep)
#                             if not rep['ReportID'] in outDBRepIds:
#                                 outDBRepIds[rep['ReportID']] = {} 

#                             assert not extraction  in outDBRepIds[rep['ReportID']]  
#                             outDBRepIds[rep['ReportID']][extraction] = rep[extraction]

#                             if extraction in toSee and seen[extraction] < 10:
#                                  seen[extraction] += 1
#                                  print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
#                                  print "Extraction type", extraction
#                                  print rep[reportTextKey]
#                                  print rep[extraction]
#                                  raw_input()

#                         else:
#                             continue
#     return False

# def parseOncoScore(score):
#     if score < 18:
#         return 'Low risk'
#     elif score <= 30:
#         return 'Mid risk'
#     elif score > 30: 
#         return 'High risk'
#     else:
#         return 'None'
# ## Suport building dbs from path reps (aligned by taghian index in the path rep) for er/pr/her2
# ## This is because I have col to index dictionaries to figure out which date led to that result
# ## Input DB is joinedDB
# ## Key { MRN} -> {'taghian': [recap events], 'hughes':[pathReps], 'lengths':[ countRedCapEvents, count pathReps]}

# def processGradeData(grades, allPathReps, outDB, outDBRepIds):
#     for rep in allPathReps:
#         ## Now we merge in external data, like grade
#         if rep['Report_Text'] in grades:
#             grade = grades[rep['Report_Text']].strip()[0].upper() + grades[rep['Report_Text']].strip()[1:]
#             rep['TumorGrade'] = grade
#             outDB['TumorGrade'].append(rep)
#             if not rep['ReportID'] in outDBRepIds:
#                 outDBRepIds[rep['ReportID']] = {}
#             outDBRepIds[rep['ReportID']]['TumorGrade'] = rep['TumorGrade']
#     return False

# def processSusPhyllodes(allPathReps, outDB, outDBRepIds):
#     scrape = False
#     if scrape:
#         phylodesDb = parseXLS('../externalDataSources/susPhyllodes.xlsx', 'data/susPhyllodes.p')
#     else: 
#         phylodesDb = p.load(open('data/susPhyllodes.p','rb'))
#     ## build Mrn -> sus for phyllodes 
#     mrnSus = {}
#     mrnKey = 'MRNPlusX'
#     susKey = 'HxOfOrSuspiciousForPhyllodes'
#     phyKey = "Phylodes"
#     for row in phylodesDb:
#         mrn = str(row[mrnKey])
#         if not susKey in row or row[susKey] == None:
#             continue
#         sus = row[susKey]
#         phy = row[phyKey]
#         if mrn in mrnSus:
#             mrnSus[mrn] = 'SKIP'
#         else:
#             mrnSus[mrn] = (sus,phy)

#     print "num mrnSus", len([m for m in mrnSus if not mrnSus[m] == "SKIP"])

#     ## build mrn: to num articles, if 1 then sus phyllodes
#     repCounts = {}
#     for rep in allPathReps:
#         mrn = rep['MRNPlusX']
#         if not mrn in repCounts:
#             repCounts[mrn] = 0
#         repCounts[mrn] += 1

#     print "num eligble reps", (len([k for k in repCounts if repCounts[k]== 1 and k in mrnSus]))

#     susKey = 'Red SuspiciousForPhyllodes'
#     if not susKey in outDB:
#         outDB[susKey] = [] 
#     phyKey =  'Red Phylodes'  
#     if not susKey in outDB:
#         outDB[phyKey] = []    
#     ## do allignmnet on the ones
#     for rep in allPathReps:
#         mrn = rep['MRNPlusX']
#         criteria = (mrn in mrnSus and repCounts[mrn] == 1 and not mrnSus[mrn]=='SKIP')
#         if not criteria:
#             continue

#         sus = 'Present' if str(mrnSus[mrn][0]) == '1' else 'Absent'
#         phy = 'Present' if str(mrnSus[mrn][1]) == '1' else 'Absent'
#         rep[phyKey] = phy

#         outDB[phyKey].append(rep)
#         if not rep['ReportID'] in outDBRepIds:
#             outDBRepIds[rep['ReportID']] = {}

#         outDBRepIds[rep['ReportID']][phyKey] = phy


#     ## print stats
#     vals = [r['Red Phylodes'] for r in outDB['Red Phylodes'] ]
#     print "Phylodes",len([v for v in vals if v == 'Present']), "present, ", len([v for v in vals if v == 'Absent']), "absent"
#     return False

# def anon(db, textKey='text', keys=None):
#     print "calling anonAndAlign"
#     print "len db to allign", len(db)

#     #anon
#     for r in db:
#         cleanText =  deIdenText(r[textKey])
#         r['Report_Text'] = cleanText
#         r['Report_Text_Segmented'] = cleanText
#         del r[textKey] 

#     return db


# def processSusPhyllodesOct(allPathReps, outDB, outDBRepIds):
#     scrape = False
#     legend = ['text', 'Red Phylodes', 'Red SuspiciousForPhyllodes', 'Explanation', 'explanation2']
#     if scrape:
#         phyllodesDb = parseDoc('../externalDataSources/Phyllodes_Annotations_All_Oct30.docx', 'data/susPhyllodesOctRaw.p', 
#             legend=legend)
#     else: 
#         phyllodesDb = p.load(open('data/susPhyllodesOctRaw.p','rb'))

#     annonKeys = legend[1:-1]
#     phyllodesDb = anon(phyllodesDb,keys=annonKeys)
#     p.dump(phyllodesDb, open('data/susPhyllodesOct.p','wb'))

#     print "Done anone"
#     ## asign them new rep ids, dont split em
#     for r in phyllodesDb:
#         r['ReportID'] = len(allPathReps)+1
#         allPathReps.append(r)
    

#     susKey = 'Red SuspiciousForPhyllodes'
#     if not susKey in outDB:
#         outDB[susKey] = [] 
#     phyKey =  'Red Phylodes'  
#     if not phyKey in outDB:
#         outDB[phyKey] = []    
#     ## do allignmnet on the ones
#     for rep in phyllodesDb:
        
#         if susKey in rep:
#             rep[susKey] = 'Present' if str(rep[susKey]) == '1' else 'Absent'
#             outDB[susKey].append(rep)

#         if phyKey in rep:
#             rep[phyKey] = 'Present' if str(rep[phyKey]) == '1' else 'Absent'
#             outDB[phyKey].append(rep)

#         if phyKey in rep or susKey in rep:
#             if not rep['ReportID'] in outDBRepIds:
#                 outDBRepIds[rep['ReportID']] = {}

#             outDBRepIds[rep['ReportID']][phyKey] = rep[phyKey]
#             outDBRepIds[rep['ReportID']][susKey] = rep[susKey]


#     ## print stats
#     vals = [r['Red Phylodes'] for r in outDB[phyKey] ]
#     print "Phylodes",len([v for v in vals if v == 'Present']), "present, ", len([v for v in vals if v == 'Absent']), "absent"
#     vals = [r[susKey] for r in outDB[susKey] ]
#     print "Phylodes Sus",len([v for v in vals if v == 'Present']), "present, ", len([v for v in vals if v == 'Absent']), "absent"
#     return False

# def processOncoScores(db, colSeqs, allPathReps, outDB, outDBRepIds, toSee, seen ):
#     allPathReps = p.load(open(rawDBPath,'rb'))
#     ## Process external oncoscores
#     loadBool = True
#     extKey = 'Dx Score'
#     if loadBool:
#         externalPath =  '../externalDataSources/oncoscore.xlsx'
#         extOncos =  parseXLS(externalPath, "data/oncoscoreList.p")   
#         mrnToOnc = {}
#         for row in extOncos:
#             mrn = normalizeMRN(row['MRNPlusX'])
#             if not mrn in mrnToOnc:
#                 mrnToOnc[mrn] = []    
#             mrnToOnc[mrn].append(row)
#         p.dump(mrnToOnc, open('data/oncoscoreDb.p','wb'))
#     else:
#         mrnToOnc = p.load(open('data/oncoscoreDb.p','rb'))
#     print "len mrnToOnc", len(mrnToOnc), type(mrnToOnc.keys()[0])

#     #process redcap
#     for mrn in db:

#         pathReps =  db[mrn]['hughes']
#         redcap   =  db[mrn]['taghian']

#         ## For normal extractions that line up to a specific report,
#         ## we iterate through reps, find corresponding col for that extraction
#         ## for that report and produce DB
#         for rep in reversed(pathReps):
#             for extraction in maxedOutList:
#                 if not extraction == 'Oncotype score':
#                     continue

#                 colSeq =  colSeqs[extraction]

#                 if not ('taghainColIndx' in rep and 'taghainRowIndx' in rep):
#                     continue

#                 redcapIndx = rep['taghainRowIndx']
                    
#                 colField = colSeq[0] ## maxed out reps have length one lists

#                 if redcap[redcapIndx][colField] == None:
#                     continue

#                 if redcap[redcapIndx]['Oncotype date'] == None or rep['Report_Date_TimePlusX'] > redcap[redcapIndx]['Oncotype date']:
#                     continue
                
#                 score = parseOncoScore(redcap[redcapIndx][colField])
#                 if score == "None":
#                     continue
#                 rep[extraction] = score


#                 ##For oncoscore, assert that report is a lumpectomy
                
#                 outDB[extraction].append(rep)
#                 if not rep['ReportID'] in outDBRepIds:
#                     outDBRepIds[rep['ReportID']] = {} 

#                 assert not extraction  in outDBRepIds[rep['ReportID']]  
#                 outDBRepIds[rep['ReportID']][extraction] = rep[extraction]

#                 if extraction in toSee and seen[extraction] < 0:
#                      seen[extraction] += 1
#                      print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
#                      print "Extraction type", extraction
#                      print rep[reportTextKey]
#                      print rep[extraction]
#                      raw_input()

#     #process ext
#     extraction = 'Oncotype score'
#     for mrnOnc in mrnToOnc:
#         oncs = mrnToOnc[mrnOnc]

#         relevantReps = [r for r in allPathReps if normalizeMRN(r['MRNPlusX']) == normalizeMRN(mrnOnc)]
#         if not len(relevantReps)>0:
#             continue

#         relevantReps = sorted(relevantReps, key=itemgetter('Report_Date_TimePlusX') )

#         for onc in oncs:
#             oncDate = onc['SpecimenReceivedPlusX']
#             onc = onc[extKey]

#             for rep in reversed(relevantReps):
#                 try:
#                     if oncDate == None or rep['Report_Date_TimePlusX'] > oncDate \
#                     or (oncDate - rep['Report_Date_TimePlusX']).days > 35\
#                     or ("right" in rep['Report_Text'].lower() and "left" in rep['Report_Text'].lower() ):
#                         continue
#                 except Exception, e:
#                     print oncDate
#                     print e
#                     raw_input()

#                 #Skip if annotated by taghain
#                 if rep['ReportID'] in outDBRepIds and extraction in [rep['ReportID']]:
#                     continue

#                 ## Now at most recent excision that has no taghian annotation
#                 if 'Oncotype score' in rep:
#                     continue

#                 rep[extraction] = parseOncoScore(onc)
                
#                 outDB[extraction].append(rep)
#                 if not rep['ReportID'] in outDBRepIds:
#                     outDBRepIds[rep['ReportID']] = {} 

#                 if extraction  in outDBRepIds[rep['ReportID']]:
#                     continue
#                 outDBRepIds[rep['ReportID']][extraction] = rep[extraction]

#                 if extraction in toSee and seen[extraction] < 0:
#                      seen[extraction] += 1
#                      print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
#                      print "Extraction type", extraction
#                      print rep[reportTextKey]
#                      print rep[extraction], rep['MRNPlusX'], oncDate
#                      print rep['Report_Date_TimePlusX']
#                      print [r['Report_Date_TimePlusX'] for r in relevantReps]
#                 if normalizeMRN(mrnOnc) == "05413985":
#                     print "rep chosen", rep['Report_Text']
#                     print onc
#                 break
#     print "num oncoscores", len(outDB[extraction])
#     return False

# def processTabbedExcel(path, out):
#     print "loading wb"
#     wb = xl.load_workbook(path)
#     output = {}
#     sheetNames = wb.sheetnames
#     for name in sheetNames:
#         sheet = wb.get_sheet_by_name(name)

#         data = []

#         legendRowBool = True
#         print "Getting iterator"
#         legend = []
#         targets = ['Correct','ReportID']
#         for row in sheet.iter_rows():
#             rowDict = {}
#             for indx, col in enumerate(row):
#                 if legendRowBool:
#                     if not col.value in legend:
#                         newName = col.value
#                         legend.append(newName)
#                     else:
#                         counter = 2
#                         newName = str(counter) + " " + col.value
#                         while newName in legend:
#                             counter += 1
#                             newName = str(counter) + " " + col.value
#                         legend.append(newName)
#                 else:
#                     if legend[indx] in targets:
#                         rowDict[legend[indx]] = col.value



#             if not legendRowBool:
#                 if reduce( (lambda x, y:  x and y) , [t in rowDict and not rowDict[t] == None for t in targets]):
#                     data.append(rowDict)
#             else:
#                 print 'processing legend row'

#             legendRowBool = False
                
#         print 'dumping'
#         print "legend", legend

#         output[name] = data

#     p.dump(output, open(out, 'wb'))
#     return output


# def  processDisagreements(allPathReps, outDB, outDBRepIds):
#     print "called process disagrements"
#     disagreementsPaths = '../externalDataSources/disagreements_MG.xlsx'
#     disaDbPath = "data/disagreement_MG_Oct.p"
#     scrape = False
#     if scrape:
#         disgreements = processTabbedExcel(disagreementsPaths, disaDbPath)
#     else:
#         disgreements = p.load(open(disaDbPath,'rb'))

#     keyToDiag = {
#         u'disagreement_on_TubularCancer.c':'Red TubularCancer',
#         u'ILC': 'Red ILC',
#         u'FlatEpithelial':'Red FlatEpithelial',
#         u'INSITUNOS': 'Red InsituNOS',
#         u'tubular cancer':'Red TubularCancer',
#         u'blunt adenosis':'Red BluntAdenosis',
#         u'CancerSuspicious':'Red CancerSuspicious',
#         u'CancerNOS': 'Red CancerNOS',
#         u'CancerInvInsituNOS':'Red CancerInvInsituNOS',
#         u'Invasive Suspicious':'Red InvasiveSuspicious',
#         u'IDC':'Red IDC',
#         u'phyllodes': 'Red Phylodes'}

#     for key  in keyToDiag:
#         updates = disgreements[key]
#         if len(updates) == 0:
#             continue
#         targetDiag = keyToDiag[key]
#         for annotation in updates:
#             repId = annotation['ReportID']
#             label = "Present" if annotation['Correct'] == 1 else 'Absent'

#             rep = [jr for jr in allPathReps if jr['ReportID']==repId][0]

#             rep[targetDiag] = label

#             if not targetDiag in outDB:
#                 outDB[targetDiag] = []
#             if not repId in outDBRepIds:
#                 outDBRepIds[repId] = {}

#             outDB[targetDiag].append(rep)
#             outDBRepIds[repId][targetDiag] = label
        
#         print "Num of ", targetDiag, "annotations", len(outDB[targetDiag])

#     return False

# def processPapil(allPathReps, outDB, outDBRepIds):
#     print "called process papil"
#     disagreementsPaths = '../externalDataSources/papilAnnotations.xlsx'
#     disaDbPath = "data/papil_MG_Nov.p"
#     scrape = True
#     if scrape:
#         papils = parseXLS(disagreementsPaths, disaDbPath)
#     else:
#         papils = p.load(open(disaDbPath,'rb'))

#     print "num papil Annotations", len(papils)

#     textToVal = {}
#     for row in papils:
#         textToVal[row['text']] = row['Papill']

#     for r in allPathReps:
#         if r['Report_Text_Segmented'] in textToVal:
#             repId = r['ReportID']

#             label = textToVal[r['Report_Text_Segmented']]
#             r['Red Papill'] = label

#             targetDiag = 'Red Papill'

#             if not targetDiag in outDB:
#                 outDB[targetDiag] = []
#             if not repId in outDBRepIds:
#                 outDBRepIds[repId] = {}

#             outDB[targetDiag].append(r)
#             outDBRepIds[repId][targetDiag] = label

# def processCorrections(allPathReps, outDB, outDBRepIds):
#     print "called process corrections"
#     disagreementsPaths = '../externalDataSources/noFollowupForAtypias_11_21_all_rknys.xlsx'
#     disaDbPath = "data/mg_rknys_corrections.p"
#     scrape = True
#     if scrape:
#         corrections = parseXLS(disagreementsPaths, disaDbPath)
#     else:
#         corrections = p.load(open(disaDbPath,'rb'))

#     print "num papil Annotations", len(corrections)

#     textToVal = {}
#     for row in corrections:
#         textToVal[row['Report_Text_Segmented']] = row

#     rowMap = {
#         'BreastSide': 'Red BreastSide',
#         'BiopsyType': 'BiopsyType',
#         'cancer': 'cancer',
#         'IDC': 'Red IDC',
#         'ILC': 'Red ILC',
#         'TubularCancer': 'Red TubularCancer',
#         'CancerNOS': 'DCIS', 
#         'InsituNOS':'Red InsituNOS',
#         'ER': 'ER',
#         'PR':'PR',
#         'Her2Fish': 'Her2Fish',
#         'CancerSuspicious':'Red CancerSuspicious',
#         'InvasiveSuspicious': 'Red InvasiveSuspicious',
#         'AretherepositiveLN?': 'Are there positive LN?',
#         'ECE(extracapsularextension)':'ECE',
#         'LVI':'LVI',
#         'BVI':'BVI',
#         'LobularNeoplasia': 'Red Lobular Neoplasia',
#         'ALH':'Red ALH',
#         'ADH':'Red ADH',
#         'ADH_DCIS':'Red ADH_DCIS',
#         'FlatEpithelial': 'Red FlatEpithelial',
#         'LCIS':'Red LCIS',
#         'DCIS':'Red DCIS',
#         'Phylodes': 'Red Phyllodes'
#     }

#     labelMap = {
#         'Present':'Present',
#         'Absent':'Absent',
#         'NO':'NA',
#         'NO':'No',
#         'No':'No',
#         'Yes':'Yes',
#         'na':'NA',
#         'NA':'NA',
#         'Right':'RIGHT',
#         'RIGHT':'RIGHT',
#         'LEFT':'LEFT',
#         'Excision':'Excision',
#         'Core':'Core',
#         'Excision LYMP NODE':'Excision',
#         'FNA':'Other',
#         'Incision':'Other',
#         'Exsicion':'Excision',
#         'unknown':'Other',
#         'TRUM REDUCTION':'Other',
#         'No_breast_biopsy':'Other',
#         'axillary disection':'Other',
#         'excision':'Excision',
#         'Mastectomy':'Excision',
#         'Lymph node':'Other'

#     }

#     for r in allPathReps:
#         if r['Report_Text_Segmented'] in textToVal:
#             repId = r['ReportID']

#             for k in rowMap:
#                 rawLabel = textToVal[ r['Report_Text_Segmented']][k] 
#                 label = labelMap[ rawLabel ] if rawLabel in labelMap else defaultLabelDict[rowMap[k]]
#                 r[ rowMap[k] ]= label

#                 targetDiag = rowMap[k]

#                 if not targetDiag in outDB:
#                     outDB[targetDiag] = []
#                 if not repId in outDBRepIds:
#                     outDBRepIds[repId] = {}

#                 outDB[targetDiag].append(r)
#                 outDBRepIds[repId][targetDiag] = label

# def processExtraXMLs(allPathReps, outDB, outDBRepIds):
#     files= ['TraingSetLymphoma_NonBreastCancerInBreast.xml'
#         ,'TraingSetSarcoma_NonBreastCancerInBreast.xml'
#         ,'TrainingForMetaplasticMedullaryMucinous_NonBreastCancerInBreast.xml'
#         ,'TrainingForMicropapillary_NonBreastCancerInBreast.xml'
#         ,'TrainingSetNonBreast.xml']

#     paths = ["../externalDataSources/"+ f for f in files]
#     rs = [ xmltodict.parse( open(path,'rb'))['dataroot'] for path in paths ]
#     keys = [ [k for k in r.keys() if not "@" in k][0] for r in rs]
#     trs = [rs[i][keys[i]] for i in range(len(rs))]

#     allAnn = []
#     for t in trs:
#         allAnn.extend([r for r in t if not r == None])

#     labelDict = {'absent':'Absent'}
#     keyDict = {
#             'Node_x0020_tissue':'NodeTissue',
#             'CancerNotOfBreastOrigin':'CancerNotOfBreastOrigin',
#             'Report_Text':'Report_Text_Segmented',
#             'CancerInvNOS':'Red CancerInvNOS',
#             'Cancer_x0020_Invasive': 'Red CancerInvasive',
#             'Pathology_x0020_type': 'PathologyType'
#             }
#     for r in allAnn:
#         for k in keyDict:
#             if k in r:
#                 r[ keyDict[k] ] = r[k]

#     allAnn = anon(allAnn, textKey = 'Report_Text_Segmented')

#     p.dump(allAnn,open('../xmlTrainingData.p','wb'))
#     return 0




# def buildDB(db, grades, redmap, allPathReps, debug = False):
#     outDBReps = []
#     outDBRepIds = {}
#     outDB = {}
#     labelDist = {}
#     ## Use this for debugging
#     seen = {}
#     toSee = ['Oncotype score']
#     for s in toSee:
#         seen[s] = 0

#     colSeqs, types = getColSeqs(redmap, outDB)

#     #Investigative Counts
#     yetToPrintBool = True
#     processExtraXMLs(allPathReps, outDB, outDBRepIds)

#     processRedcapData(db, colSeqs, types, outDB, outDBRepIds, toSee, seen)
#     processGradeData(grades, allPathReps, outDB, outDBRepIds)
#     processOncoScores(db, colSeqs, allPathReps, outDB, outDBRepIds, toSee, seen )
#     processSusPhyllodes(allPathReps, outDB, outDBRepIds)
#     processSusPhyllodesOct(allPathReps, outDB, outDBRepIds)
#     processDisagreements(allPathReps, outDB, outDBRepIds)
#     processPapil(allPathReps, outDB, outDBRepIds)
#     processCorrections(allPathReps, outDB, outDBRepIds)

#     ## Now we print label distrubtions for generating maps and in constants
#     printLabelDist(outDB)
#     assert len(outDBReps) == 0
                
#     for report in allPathReps:
#         if report['ReportID'] in outDBRepIds:
#             report['TaghianGold'] = 1
#             for extraction in outDBRepIds[report['ReportID']]:
#                 if extraction in report: ## This is to catch things like DCIS which are both in Taghian and Hughes dB
#                     continue
#                 else:
#                     report[extraction] = outDBRepIds[report['ReportID']][extraction]


#             assert 'TaghianGold' in report and report['TaghianGold'] == 1
#             outDBReps.append( report )
                

#     p.dump(outDBReps, open('data/allExtractionReps.p', 'wb'))
#     p.dump(outDB, open('data/allExtractionDBs.p', 'wb'))
#     for extraction in outDB:
#         print "Number of ",extraction," reps and path reps equiv", len(outDB[extraction])
#     print "Num extractions", len(outDB)
#     print "num extractions over 500 reps", len([ extraction for extraction in types if len(outDB[extraction]) > 500 ])
#     print "Num path reps", len(outDBReps)
#     print "Num path rep IDs", len(outDBRepIds)
#     assert len(outDBReps) > 5000
#     assert len(outDBRepIds) > 5000

#     return outDB, outDBReps


# ## redReps: Paths aligned with redcap. All pathreps should have tahianGold = 1
# ## pathReps: all 100k pathreps
# ## Objective redump (ReportsDB) and essentially merge redReps with pathReps
# def exportRepDB(redReps, pathReps):
#     ## First build Dict of redReps counting on aligning MRN, Inst, Report_Text, Date, Breaside
#     ## Enforce no dups
#     ## go thoguh path reps, if find something in dict, replace and edump

#     #Build Dict
#     redDict = {}
#     for red in redReps:
#         repId = red['ReportID']
#         redDict[repId] = red

#     for indx, path in enumerate(pathReps):
#         pathId = path['ReportID']
#         if pathId in redDict:
#             pathReps[indx] = redDict[pathId]

#     if not len(redReps)  == len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1]):
#         print 'len(redReps)', len(redReps)
#         print "len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1])", len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1])
#     assert len(redReps) == len( [r for r in pathReps if 'TaghianGold' in r and r['TaghianGold'] == 1])

#     p.dump(pathReps, open('../reportDB+red.p','wb'))    
    


# parseXLSBool = False
# parseMapBool = False
# parseExternal = False
# preprocessDBBool = True
# findMatchingReportsBool = True
# buildDBsBool = True
# exportToRepsDBBool= True
# rawDBPath = '../rawBreastPathReport.p'

# if __name__ == "__main__":

#     allPathReps = p.load(open(rawDBPath, 'rb'))
#     # print "Validate all path", rawDBPath
#     # validateRepsDB(allPathReps, True)


#     if parseXLSBool:
#         redcap = parseRedCapXLS()

#     if parseMapBool:
#         redmap = parseMapXLS()

#     if parseExternal:
#         grades = parseGradesLS()

#     if preprocessDBBool:
#         print 'Running preprocessDB'
#         if not parseXLSBool:
#             print "Loading redcap file and map"
#             redcap = p.load(open('data/redcap.p', 'rb'))
#             redmap = p.load(open('data/redmap.p', 'rb'))
#         mrnDB = preprocessDB(redcap, True)

#     if findMatchingReportsBool:
#         print "Running findMatchingReports"
#         if not preprocessDBBool:
#             print "Loading redcapMRNDB.p"
#             mrnDB = p.load(open('data/redcapMRNDB.p','rb'))
#         joinedDB = findMatchingReports(mrnDB, allPathReps, True)
    
#     if buildDBsBool:
#         if findMatchingReportsBool:
#             allPathReps = p.load(open(rawDBPath, 'rb'))

#         if not findMatchingReportsBool:
#             joinedDB =  p.load(open('data/redcapWithPathReps.p', 'rb'))
#         if not parseXLSBool:
#             redmap = p.load(open('data/redmap.p', 'rb'))
#         if not parseExternal:
#             grades = p.load(open('data/grades.p','rb'))
#         dBs, redReps = buildDB(joinedDB, grades, redmap, allPathReps,  True)

#     if exportToRepsDBBool:
#         if not buildDBsBool:
#             redReps =     p.load(open('data/allExtractionReps.p', 'rb'))
#         print "Validate red path reps", 'data/allExtractionReps.p'
#         # validateRepsDB(redReps, True, True)
#         exportRepDB(redReps, allPathReps)



