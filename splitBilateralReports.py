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

    allData = p.load(open('rawBreastPathReport.p', 'rb'))
    newData = []

    seen = 0
    seenStrg = 0
    maxStrg = 10
    maxSeen = -1
    
    for rep in allData:
        lowerCaseText = rep['Report_Text'].lower()

        if not ("right" in lowerCaseText or "left" in lowerCaseText):
            if seenStrg < maxStrg:
                seenStrg += 1
                print rep['Report_Text']
                raw_input()
            continue        

        if "right" in lowerCaseText and "left" in lowerCaseText:

            newTexts = splitRep(rep['Report_Text'])

            if 'BreastSide' in rep:

                relevantSideText = newTexts[rep['BreastSide']]
                rep['Report_Text'] = relevantSideText

                newData.append(rep)

            else:
                for side in ["RIGHT", "LEFT"]:
                    newRep = copy.deepcopy(rep)
                    newRep['Report_Text'] =  newTexts[side]

                    newData.append(newRep)

                    if seen < maxSeen:
                        seen +=1 
                        print "orig Text", lowerCaseText
                        print "new text", newTexts[side]
                        print "side", side
                        raw_input()

        else:
            newData.append(rep)


    


    print "New Data has len", len(newData), "As compared to", len(allData)
    raw_input("Dump back to base db?")
    p.dump(newData, open('rawBreastPathReport.p', 'wb'))
