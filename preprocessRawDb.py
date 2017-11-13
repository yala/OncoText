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

def utcToDate(date):
        if isinstance(date, datetime.date):
            return datetime.datetime( date.year, date.month, date.day)
        if isinstance(date, datetime.datetime):
            return date
        try:
            yyyymmdd = date[:8]
            return datetime.datetime.strptime(yyyymmdd, '%Y%m%d')
        except Exception, e:
            try:             
                yyyymmdd = date[:8]
                year, mo, day = int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8])
                return datetime.date(year,mo,day)
            except Exception, e:
                try:
                    yyyymmdd = date[:10]
		    return datetime.datetime.strptime(yyyymmdd, '%Y-%m-%d')
                except Exception, e:
                    try: 
                        mmddyyyy = date.split()[0]
                        return datetime.datetime.strptime(mmddyyyy, '%m/%d/%Y')
                    except Exception, e:
                        print "error cant convert to date", date
                        return datetime.date(1900,1,1)

def unicodeToDatetime(db):
    
    newDb = db
    for b in newDb:
        b['Report_Date_TimePlusX'] = utcToDate(b['Report_Date_TimePlusX']) if "Report_Date_TimePlusX" in b and not isinstance(b['Report_Date_TimePlusX'],int) else (utcToDate(b['Report_Date_Time']) if 'Report_Date_Time' in b else 0)
        if b == 0:
            print "WARNING, DATE SET TO 0!"

    return newDb


def main(allData):
    newData = []

    reportCount = 0
    rowCount = 0
    repId = 0
    
    for rep in allData:
        lowerCaseText = rep['Report_Text'].lower()
        if 'BreastSide' in rep:
            rep['ruleBreastSide'] = copy.deepcopy(rep['BreastSide'])
        
        reportCount +=1 

        ## Handle Bilaterals
        if "right" in lowerCaseText and "left" in lowerCaseText:
            rowCount += 2
            newTexts = splitRep(rep['Report_Text'])

            ## Do not make 2 reps for golds for simplicty
            if ('BreastSide' in rep and 'Correct' in rep and rep['Correct'] == 'Y'):
                b_key = 'BreastSide'
                relevantSideText = newTexts[rep[b_key]]
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

    return newData


if __name__ == "__main__":

    allData = p.load(open('../rawBreastPathReport.bak.p', 'rb'))
    newData = main(allData)
    p.dump(newData, open('../rawBreastPathReport.p', 'wb'))
