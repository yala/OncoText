import pickle as p
import sys
sys.path.append("..")
from constants import *
import copy
import re

def splitRep(txt):
    leftTxt = ""
    rightTxt = ""

    leftIndx = txt.lower().index("left") if "left" in txt.lower() else len(txt)
    rightIndx = txt.lower().index("right") if "right" in txt.lower() else len(txt)

    leadTxtIndx = min(rightIndx, leftIndx)
    leftTxt += txt[:leadTxtIndx]
    rightTxt += txt[:leadTxtIndx]
    mode = "left" if leftIndx < rightIndx else "right"
    txt = txt[leadTxtIndx:]
    while "left" in txt.lower() or "right" in txt.lower() :
        leftIndx = txt.lower().index("left") if "left" in txt.lower() else len(txt)
        rightIndx = txt.lower().index("right") if "right" in txt.lower() else len(txt)

        leadTxtIndx = rightIndx if mode == "left" else leftIndx

        if mode == "left":
            leftTxt += txt[:leadTxtIndx]
        else:
            rightTxt += txt[:leadTxtIndx]

        txt = txt[leadTxtIndx:]

        mode = "right" if mode == "left" else "left"


    return {"LEFT":leftTxt, "RIGHT": rightTxt}

def unicodeToDatetime(db):
    def utcToDate(date):
        yyyymmdd = date.split('T')[0]
        try:
            date = datetime.datetime.strptime(yyyymmdd, '%Y-%m-%d')
            return date
        except Exception, e:
            print yyyymmdd
            record[col] = yyyymmdd
            raw_input()
            return 0

    newDb = db
    for b in newDb:
        b['Report_Date_TimePlusX'] = utcToDate(b['Report_Date_TimePlusX'])

    return newDb

if __name__ == "__main__":

    allData = p.load(open('../rawBreastPathReport.bak.p', 'rb'))
    print "Len all data, then num patients", len(allData), len(set([r['MRNPlusX'] for r in allData]))
    newData = []

    seen = 0
    seenStrg = 0
    maxStrg = -1
    maxSeen = -1

    reportCount = 0
    rowCount = 0
    repId = 0
    
    for rep in allData:
        lowerCaseText = rep['Report_Text'].lower()
        if 'BreastSide' in rep:
            rep['ruleBreastSide'] = copy.deepcopy(rep['BreastSide'])

        if not ("right" in lowerCaseText or "left" in lowerCaseText) or not 'breast' in lowerCaseText:
            if seenStrg < maxStrg:
                seenStrg += 1
                print rep['Report_Text']
                raw_input()
            continue
        else:
            reportCount +=1 

        ## Handle Bilaterals
        if "right" in lowerCaseText and "left" in lowerCaseText:
            rowCount += 2
            newTexts = splitRep(rep['Report_Text'])

            ## Do not make 2 reps for golds for simplicty
            if 'BreastSide' in rep and 'Correct' in rep and rep['Correct'] == 'Y':

                relevantSideText = newTexts[rep['BreastSide']]
                rep['Report_Text_Segmented'] = relevantSideText
                rep['ReportID'] = repId
                repId +=1
                newData.append(rep) 


            ## Make 2 reps for rest of bilats
            else:
                for side in ["RIGHT", "LEFT"]:
                    newRep = copy.deepcopy(rep)
                    newRep['Report_Text_Segmented'] =  newTexts[side]
                    newRep['BreastSide'] = side
                    newRep['ReportID'] = repId
                    repId +=1
                    newData.append(copy.deepcopy(newRep))

                    if seen < maxSeen:
                        seen +=1 
                        print "orig Text", lowerCaseText
                        print "new text", newTexts[side]
                        print "side", side
                        raw_input()

        else: ## unilat case,
            rowCount += 1
            rep['Report_Text_Segmented'] = rep['Report_Text']
            rep['ReportID'] = repId
            if not 'BreastSide' in rep:
                if 'left' in rep['Report_Text'].lower():
                    rep['BreastSide'] = 'LEFT'
                else: ##okay for this to be noisy because we'll reannotate this anyways
                    rep['BreastSide'] = 'RIGHT'

            repId +=1
            newData.append(rep)


    
    ## Validate segmenting work
    for rep in newData:
        assert not( "right" in rep['Report_Text_Segmented'].lower() and "left" in rep['Report_Text_Segmented'].lower())

    # Clean dates to python datetime
    newData = unicodeToDatetime(newData)

    ## Print out data dist 
    printDataDist = False
    if printDataDist:
        print "New Data has len", len(newData), "As compared to", len(allData)
        print "Num reports", reportCount, "over ", len(set([r['MRNPlusX'] for r in allData])), "aka", len(newData), "rows"
        print "rowcount should be", rowCount
        key = "Report_Text"
        for inst in ["MGH", "NWH", "BWH"]:
            print inst
            instReps = [r for r in newData if r['Institution']==inst]
            numReps = len(instReps)
            numPatients = len(set( [r['MRNPlusX'] for r in instReps ] ))
            avgLen = sum([ len(r[key].split()) for r in instReps])/ numReps 
            range =  max([ len(r[key].split()) for r in instReps]) - min([ len(r[key].split()) for r in instReps])
            print "avglen", avgLen, "range", range, "numreps", numReps
            print "num paitents", numPatients
        
        print "Avglen overall", sum([len(r[key].split() ) for r in newData])/len(newData)
        
        print "overallRange", max([len(r[key].split() ) for r in newData]) - min([len(r[key].split() ) for r in newData])
    
        
    p.dump(newData, open('../rawBreastPathReport.p', 'wb'))
