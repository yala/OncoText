import pickle as p
import re
import random

random.seed(1)
dataPath = "deiden_AllRepsRound2.p"
goldDataPath = 'goldPathReports.p'
trainOutPath = "boostexer/pathology.data"
testOutPath = "boostexer/pathology.test"
devOutPath = "boostexer/pathology.dev"


diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']

def writeNameFiles(stem):
    for diag in diagnoses:
        with open(stem+"_"+diag+".names", "wb") as f:
            if diag == u'BreastSide':
                labels = "RIGHT, LEFT.\n"
            else:
                labels = diag + ", " + "no_"+diag+".\n"
            features = "pathReport : text.\n"
            f.write(labels)
            f.write(features)


def processLabels(labels):
    debug = False
    result =  [lab for lab in labels if not "no_" in lab]
    if len(result) == 0:
        result = ['no']

    if debug:
        print "--------Process labels-----------"
        print labels
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
        trainDist = sum([z in l  for l in trainLabels]) * 1. / numTrainSamples
        testDist  = sum([z in l  for l in testLabels]) * 1. / numTestSamples
        print 'diag', z
        print "TRAIN:", trainDist
        print "TEST:", testDist
        print "---------------------"
        sumTrain += trainDist
        sumTest  += testDist
    #Print no diagnosis case
    trainDist = sum([processLabels(l) == ["no"] for l in trainLabels]) * 1. / numTrainSamples
    testDist  = sum([processLabels(l) == ["no"] for l in testLabels]) * 1. / numTestSamples
    print 'diag', "none"
    print "TRAIN:", trainDist 
    print "TEST:" , testDist
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
    for diag in diagnoses:
        trainStem, trainSuf = trainOutPath.split('.')
        trainStem = stem
        with open(trainStem+"_"+diag+"."+trainSuf, "wb") as f: 
            for a in range(len(trainReports)):
                if diag == u'BreastSide':
                    if 'RIGHT' in processLabels(trainLabels[a]):
                        label = 'RIGHT'
                    else:
                        assert 'LEFT' in trainLabels[a]
                        label = 'LEFT'
                else:
                    label = diag if diag in processLabels( trainLabels[a]) else "no_"+diag
                report = trainReports[a]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", trainStem+"_"+diag+"."+trainSuf

    
        testStem, testSuf = testOutPath.split('.')
        testStem = stem
        with open(testStem+"_"+diag+"."+testSuf, "wb") as f: 
            for b in range(len(testReports)):
                
                if diag == u'BreastSide':
                    if 'RIGHT' in processLabels(testLabels[b]):
                        label = 'RIGHT'
                    else:
                        label = 'LEFT'
                else:
                    label =  diag if diag in processLabels(testLabels[b]) else "no_"+diag
                report = testReports[b]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", testStem+"_"+diag+"."+testSuf

if __name__ == "__main__":

    goldData = getGoldTags(True)

    labels = []
    debug = True
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

    reports = [d['Report_Text'] for d in goldData]

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

    learningCurve = True
    if learningCurve:
        for s in [100, 500, 1000, 2000, 4000, 5000, 5500]:
            trainReports= trainReports[:s]
            trainLabels= trainLabels[:s]
            print "Trainining set size", s
            printLabelDist(trainLabels, trainReports, testLabels, testReports)
            genTrainTestFiles(trainReports, trainLabels, testReports, testLabels, "boostexer/learningCurve/pathology_"+str(s))    

    verbose = True

    if verbose:
        printLabelDist(trainLabels, trainReports, testLabels, testReports)

    write = False
    if write:
        genTrainTestFiles(trainReports, trainLabels, testReports, testLabels, "boostexer/pathology")

    debugMistakes = False

    if debugMistakes:
        print "Debug mistakes"
        mistakesIds = { #'DCIS':[19, 36, 41, 166, 219, 365, 434],\
                        'FlatEpithelial':[166, 215, 343, 442]}#,\
                        #'ADH_DCIS':[143, 249, 255, 310, 365, 422, 472] }
        interpretMistakes(mistakesIds, testReports, testLabels)
