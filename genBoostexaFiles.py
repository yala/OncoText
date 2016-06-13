import pickle as p
import re
import random

random.seed(1)
dataPath = "deidentifiedPathReports.p"
goldDataPath = 'goldPathReports.p'
trainOutPath = "boostexer/pathology.data"
testOutPath = "boostexer/pathology.test"

diagnoses = [ u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS',  \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS']

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

def filterGold(reports, labels):
    reportLabelDict = {}

    filtered_reports = []
    filtered_labels = []
    for i in range(len(goldData)):
        report = reports[i]
        label = labels[i]

        if not ( report.strip() == "PATIENT  REMOVED_PATIENT_NAME" or \
            "Accession Number  REMOVED_ACCESSION_ID Report Status  Preliminary Type  Surgical Pathology Report not finalized SPECIMEN TYPE  BREAST   EXCISIONAL TISSUE W MARGINS  report_end" ==  report.strip()):
            if report in reportLabelDict:
                assert label == reportLabelDict[report]
            reportLabelDict[report]= label

    for r in reportLabelDict:
        filtered_reports.append(r)
        filtered_labels.append(reportLabelDict[r])

    return filtered_reports, filtered_labels

def printLabelDist(trainLabels, trainReports, testLabels, testReports):
        print "Label dist for train, label dist for tet"
        numTrainSamples = len(trainReports)
        numTestSamples = len(testReports)
        print 'diagnoses', diagnoses
        for z in diagnoses:
            print 'diag', z
            print "TRAIN:", sum([z in l  for l in trainLabels]) * 1. / numTrainSamples
            print "TEST:", sum([z in l  for l in testLabels]) * 1. / numTestSamples
            print "---------------------"
        #Print no diagnosis case
        print 'diag', "none"
        print "TRAIN:", sum([processLabels(l) == ["no"] for l in trainLabels]) * 1. / numTrainSamples
        print "TEST:" , sum([processLabels(l) == ["no"] for l in testLabels]) * 1. / numTestSamples
        print "---------------------"
        print numTrainSamples, numTestSamples

def interpretMistakes(mistakesIds, reports, labels):

    for diag in mistakesIds:
        mistakes = mistakesIds[diag]

        wanted = []
        if not diag in wanted: 
            continue

        for idx in mistakes:
            print "-------------------"
            print "diagnosis:", diag
            print "IDX", idx
            print "Gold", labels[idx]
            print "Report", reports[idx]
            raw_input()




if __name__ == "__main__":

    goldData = getGoldTags()

    labels = []
    for i in range(len(goldData)):
        diags = []
        sample = goldData[i]
        for diag in diagnoses:
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

    filteredReport, filteredLabel = filterGold(cleanReports, labels)

    cleanReports = filteredReport
    labels = filteredLabel
    assert len(cleanReports) == len(set(cleanReports))

    test_Size = 500

    idx = range(len(cleanReports))
    random.shuffle(idx)

    trainReports = [cleanReports[i] for i in idx[:-500]]
    trainLabels = [labels[i] for i in idx[:-500]]
    testReports = [cleanReports[i] for i in idx[-500:]]
    testLabels = [labels[i] for i in idx[-500:]]


    verbose = False

    if verbose:
        printLabelDist(trainLabels, trainReports, testLabels, trainReports)

    debugMistakes = False

    if debugMistakes:
        mistakesIds = p.load(open('mistakes.p', 'rb'))
        interpretMistakes(mistakesIds, testReports, testLabels)

    write = False
    if write:

        with open(trainOutPath, "wb") as f: 
            for a in range(len(trainReports)):
                label = processLabels( trainLabels[a])
                report = trainReports[a]
                assert not "\n" in report
                f.write(report + ", " + " ".join(label) + '.\n')
        print "Saved", trainOutPath

        with open(testOutPath, "wb") as f: 
            for b in range(len(testReports)):
                label =  processLabels(testLabels[b])
                report = testReports[b]
                assert not "\n" in report
                f.write(report + ", " + " ".join(label) + '.\n')
        print "Saved", testOutPath