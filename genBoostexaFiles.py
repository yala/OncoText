import pickle as p
import re
import random
from constants import *
import datetime

random.seed(1)

labelDict = constantValidLabelDict

def writeNameFiles(stem):
    for diag in diagnoses:
        with open(stem+"_"+replaceSpaces(diag)+".names", "wb") as f:
            if MODE == "Breast":
                if diag == u'BreastSide':
                    labels = "RIGHT, LEFT.\n"
                else:
                    labels = diag + ", " + "no_"+diag+".\n"
            elif MODE == "TAGHIAN":
                labels = ", ".join(labelDict[diag])+".\n"
            features = "pathReport : text.\n"
            f.write(labels)
            f.write(features)


def processLabels(labels):
    debug = False

    if debug:
        print "--------Process labels-----------"
        print labels
    whitelist = ["RIGHT", "LEFT"]
    result =  [lab if lab in whitelist else lab for indx, lab in enumerate(labels) if lab == 1 or lab in whitelist or lab in diagnoses]
    if len(result) == 0:
        result = ['no']

    if debug:
        print result
        raw_input()
    return result

def getGoldTags(dumpGold = False):
    if dumpGold:
        allData = p.load(open(dataPath, 'rb'))
        goldData = [d for d in allData if 'Correct' in d]
        p.dump(goldData, open(goldDataPath, 'wb'))
    else:
        goldData = p.load(open(goldDataPath, 'rb'))
    return goldData

## Function throws away duplicate or meaningless reports and returns the rest
def filterGold(reports, labels, debug = False):
    reportLabelDict = {}
    countWut = 0
    filtered_reports = []
    filtered_labels = []
    for i in range(len(reports)):
        report = reports[i]
        label = labels[i]

        if not ( report.strip() == "PATIENT  REMOVED_PATIENT_NAME" or \
            "Accession Number  REMOVED_ACCESSION_ID Report Status  Preliminary Type  Surgical Pathology Report not finalized SPECIMEN TYPE  BREAST   EXCISIONAL TISSUE W MARGINS  report_end" ==  report.strip()):
            if report in reportLabelDict:
                if not label == reportLabelDict[report]:
                    if debug:
                        print "report with diff labels"
                        print report
                        print label
                        print reportLabelDict[report]
                    countWut +=1
            reportLabelDict[report]= label

    for r in reportLabelDict:
        filtered_reports.append(r)
        filtered_labels.append(reportLabelDict[r])

    assert len(filtered_reports) == len(filtered_labels)
    if debug:
        print "NUM REPORTS", len(filtered_reports)
        print "COUNT WIERD DUPS", countWut
    return filtered_reports, filtered_labels




def genTrainTestFiles(trainReports, trainLabels, testReports, testLabels, stem):
    writeNameFiles(stem)
    for indx, diag in enumerate(diagnoses):
        trainStem, trainSuf = trainOutPath.split('.')
        trainStem = stem
        with open(trainStem+"_"+replaceSpaces(diag)+"."+trainSuf, "wb") as f: 
            for a in range(len(trainReports)):                
                if trainLabels[a][indx] in labelDict[diag]:
                    label = trainLabels[a][indx]
                else:
                    continue

                report = trainReports[a]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", trainStem+"_"+replaceSpaces(diag)+"."+trainSuf

    
        testStem, testSuf = testOutPath.split('.')
        testStem = stem
        with open(testStem+"_"+replaceSpaces(diag)+"."+testSuf, "wb") as f: 
            for b in range(len(testReports)):   
                if testLabels[b][indx] in labelDict[diag]:
                    label = testLabels[b][indx]
                else:
                    label = defaultLabelDict[diag]

                report = testReports[b]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", testStem+"_"+replaceSpaces(diag)+"."+testSuf
