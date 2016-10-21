import pickle as p
import re
import random
from constants import *
import datetime

random.seed(1)

if MODE == "TAGHIAN":
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

def printLabelDist(trainLabels, trainReports, testLabels, testReports):
    sumTest = 0
    sumTrain = 0
    print "Label dist for train, label dist for tet"
    numTrainSamples = len(trainReports)
    numTestSamples = len(testReports)
    print 'diagnoses', diagnoses
    
    assert len(trainLabels) == numTrainSamples
    assert numTestSamples   == len(testLabels)

    for z in diagnoses:
        if z == "BreastSide":
            trainNum = sum(["RIGHT" in l  for l in trainLabels])
            trainDist = trainNum * 1. / numTrainSamples
            testNum = sum(["RIGHT" in l  for l in testLabels])
            testDist  = testNum * 1. / numTestSamples
        else:
            trainNum = sum([z in l  for l in trainLabels])
            trainDist = trainNum * 1. / numTrainSamples
            testNum = sum([z in l  for l in testLabels])
            testDist  = testNum * 1. / numTestSamples
        print 'diag', z
        print "TRAIN:", trainNum, "(", trainDist, ")"
        print "TEST:", testNum, "(", testDist, ")"
        print "Overall", trainNum+testNum, (numTestSamples+numTrainSamples) - (trainNum+testNum),  (numTestSamples+numTrainSamples) , (trainNum+testNum)*1./(numTestSamples+numTrainSamples) *100, 100 - ((trainNum+testNum)*1./(numTestSamples+numTrainSamples)*100)
        print "---------------------"
        sumTrain += trainDist
        sumTest  += testDist
    #Print no diagnosis case
    print "---------------------"
    print numTrainSamples, numTestSamples
    sumTrain += trainDist
    sumTest  += testDist
    print "Sum trainDist ", sumTrain
    print "sum testDist  ", sumTest

def interpretMistakes(mistakesIds, reports, labels):
    for diag in mistakesIds:

        mistakes = mistakesIds[diag]

        for idx in mistakes:
            print "-------------------"
            print "diagnosis:", diag
            print "IDX", idx
            print "Gold", labels[idx]
            print "Report", reports[idx]
            raw_input()


def genTrainTestFiles(trainReports, trainLabels, testReports, testLabels, stem):
    writeNameFiles(stem)
    for indx, diag in enumerate(diagnoses):
        trainStem, trainSuf = trainOutPath.split('.')
        trainStem = stem
        with open(trainStem+"_"+replaceSpaces(diag)+"."+trainSuf, "wb") as f: 
            for a in range(len(trainReports)):
                if MODE == "Breast":
                    if diag == u'BreastSide':
                        if 'RIGHT' in processLabels(trainLabels[a]):
                            label = 'RIGHT'
                        else:
                            assert 'LEFT' in trainLabels[a]
                            label = 'LEFT'
                    else:
                        label = diag if diag in processLabels( trainLabels[a]) else "no_"+diag
                elif MODE == "TAGHIAN":
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
                if MODE == "Breast":
                    if diag == u'BreastSide':
                        if 'RIGHT' in processLabels(testLabels[b]):
                            label = 'RIGHT'
                        else:
                            label = 'LEFT'
                    else:
                        label =  diag if diag in processLabels(testLabels[b]) else "no_"+diag
                elif MODE == "TAGHIAN":
                    if testLabels[b][indx] in labelDict[diag]:
                        label = testLabels[b][indx]
                    else:
                        label = defaultLabelDict[diag]

                report = testReports[b]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", testStem+"_"+replaceSpaces(diag)+"."+testSuf

if __name__ == "__main__":

    goldData = getGoldTags(True)

    labels = []
    debug = False
    for i in range(len(goldData)):
        diags = []
        sample = goldData[i]
        for diag in diagnoses:
            if diag == u'BreastSide' and u'BreastSide' in sample:
                diags.append(sample[diag])
                if not sample[diag]  in ['RIGHT', 'LEFT']:
                    print sample[diag]
                    print sample
                    raw_input()
            else:
                if diag in sample and sample[diag] == '1':
                    diags.append(diag)
                else:
                    diags.append('no_'+diag)
        labels.append(diags)

    reports = [d[reportTextKey] for d in goldData]

    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]

    print "Avg num words", sum([ len(r.split()) for r in cleanReports])/len(cleanReports)

    filteredReport, filteredLabel = filterGold(cleanReports, labels)

    cleanReports = filteredReport
    labels = filteredLabel
    assert len(cleanReports) == len(set(cleanReports))

    test_Size = 500

    idx = range(len(cleanReports))
    random.shuffle(idx)

    dev = False
    if dev:
        trainReports = [cleanReports[a] for a in idx[:-600]]
        trainLabels = [labels[b] for b in idx[:-600]]

        testReports = [cleanReports[c] for c in idx[-600:-500]]
        testLabels = [labels[d] for d in idx[-600:-500]]
    else:
        trainReports = [cleanReports[a] for a in idx[:-500]]
        trainLabels = [labels[b] for b in idx[:-500]]

        testReports = [cleanReports[c] for c in idx[-500:]]
        testLabels = [labels[d] for d in idx[-500:]]

    print "dumping ",reportTextKey, "list for test set."
    p.dump([reports[i] for i in idx[-500:]], open('analysis/genBoostexaTestReportDump.p', 'wb'))
    p.dump([goldData[i]['Report_Text'] for i in idx[-500:]], open('analysis/genBoostexaFullTestReportDump.p', 'wb'))


    learningCurve = False
    if learningCurve:
        for s in [10, 50, 100, 500, 1000, 2000, 4000, 5000, 5500]:
            truncTrainReport= trainReports[:s]
            truncTrainLabels= trainLabels[:s]
            print "Trainining set size", s
            printLabelDist(truncTrainLabels, truncTrainReport, testLabels, testReports)
            genTrainTestFiles(truncTrainReport, truncTrainLabels, testReports, testLabels, "boostexer/learningCurve/pathology_"+str(s))    

    verbose = True

    if verbose:
        printLabelDist(trainLabels, trainReports, testLabels, testReports)

    write = True
    if write:
        genTrainTestFiles(trainReports, trainLabels, testReports, testLabels, "boostexer/breast/labeled/pathology")

    debugMistakes = False

    if debugMistakes:
        print "Debug mistakes"
        mistakesIds = { #'DCIS':[19, 36, 41, 166, 219, 365, 434],\
                        'FlatEpithelial':[166, 215, 343, 442]}#,\
                        #'ADH_DCIS':[143, 249, 255, 310, 365, 422, 472] }
        interpretMistakes(mistakesIds, testReports, testLabels)
