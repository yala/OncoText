import pickle as p
from constants import *
import copy

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

if __name__ == "__main__":

    allData = p.load(open('rawBreastPathReport.bak.p', 'rb'))
    print "Len all data, then num patients", len(allData), len(set([r['MRNPlusX'] for r in allData]))
    newData = []

    seen = 0
    seenStrg = 0
    maxStrg = -1
    maxSeen = -1

    reportCount = 0
    rowCount = 0
    
    for rep in allData:
        lowerCaseText = rep['Report_Text'].lower()

        if not ("right" in lowerCaseText or "left" in lowerCaseText) or not 'breast' in lowerCaseText:
            if seenStrg < maxStrg:
                seenStrg += 1
                print rep['Report_Text']
                raw_input()
            continue
        else:
            reportCount +=1 

        if "right" in lowerCaseText and "left" in lowerCaseText:
            rowCount += 2
            newTexts = splitRep(rep['Report_Text'])

            if 'BreastSide' in rep and 'Correct' in rep and rep['Correct'] == 'Y':

                relevantSideText = newTexts[rep['BreastSide']]
                rep['Report_Text_Segmented'] = relevantSideText

                newData.append(rep)

            else:
                for side in ["RIGHT", "LEFT"]:
                    newRep = copy.deepcopy(rep)
                    newRep['Report_Text_Segmented'] =  newTexts[side]

                    newData.append(copy.deepcopy(newRep))

                    if seen < maxSeen:
                        seen +=1 
                        print "orig Text", lowerCaseText
                        print "new text", newTexts[side]
                        print "side", side
                        raw_input()

        else:
            rowCount += 1
            rep['Report_Text_Segmented'] = rep['Report_Text']
            newData.append(rep)


    
    for rep in newData:
        assert not( "right" in rep['Report_Text_Segmented'].lower() and "left" in rep['Report_Text_Segmented'].lower())


    print "New Data has len", len(newData), "As compared to", len(allData)
    print "Num reports", reportCount, "over ", len(set([r['MRNPlusX'] for r in allData])), "aka", len(newData), "rows"
    print "rowcount should be", rowCount
    raw_input("Dump back to base db?")
    p.dump(newData, open('rawBreastPathReport.p', 'wb'))
