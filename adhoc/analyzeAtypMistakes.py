import pickle as p
import openpyxl as xl
import re

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

def clean(report):
    reports = [report]
    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]

    return cleanReports[0]

export = p.load(open('atypiaExport.p'))
molly = parseXLS('../externalDataSources/MasterAtypiaDev.xlsx', 'mollyCorrections.p')

mistakesOfIntr = [3,4,5,15]

mistakeReps = {}
numMistakes = 0
numUsualDuctal = 0
HistCount = 0
for rep in molly:
    key = 'WhyNotCorrectCodedForAdam'
    if not key in rep or rep[key] == None:
        continue
    codes = [int(c.strip()) for c in rep[key].split(',')] if  not isinstance(rep[key],long) else [rep[key]]

    numMistakes +=1
    if 'Usual Ductal' in rep and not rep['Usual Ductal'] == None:
        numUsualDuctal+=1

    if 'ClinicalHistory' in rep and not rep['ClinicalHistory'] == None:
        HistCount +=1

    for code in codes:
        if not code in mistakeReps:
            mistakeReps[code] = []

        mistakeReps[code].append(rep)
print [(code,len(mistakeReps[code])) for code in mistakeReps ]
print "Num mistakes", numMistakes, "Len reps", len(molly)
print "Num usual ductul", numUsualDuctal
print "num clinical hist", HistCount


avgLen = 0
denom = 0
for k in mistakeReps:
    denom += len(mistakeReps[k])
    for rep in mistakeReps[k]:

        avgLen += len(rep['Report_Text'].split())
        # raw_input()
        # print "#########################"

avgLen /= denom
print "AvgLen of mistake", avgLen

with open("../boostexer/breast/debug/pathology_all_LobularNeoplasia.test", 'wb') as f:
    for rep in mistakeReps[15]:
        f.write(clean(rep['Report_Text']).lower() +" , LobularNeoplasia.\n")