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
    result =  [lab for lab in labels if not "no_" in lab]
    if len(result) == 0:
        result = ['no']
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
    print "done labeling bruv"

    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]



    filteredReport, filteredLabel = filterGold(cleanReports, labels)
    print "len diff", len(reports) - len(filteredReport)

    cleanReports = filteredReport
    labels = filteredLabel


    assert len(cleanReports) == len(set(cleanReports))


    assert len(cleanReports) == len(labels)
    assert len(labels[0]) == len(diagnoses)
    print "Sample label", labels[0]
    debug = False
    if debug:
        for i in range(len(reports)):
            print "___________________________________"
            print reports[1]
            print cleanReports[1]
            raw_input()

    test_Size = 500

    idx = range(len(cleanReports))
    random.shuffle(idx)

    trainReports = [cleanReports[i] for i in idx[:-500]]
    trainLabels = [labels[i] for i in idx[:-500]]

    print "Label dist for train"
    print "Sample label", trainLabels[100]

    numTrainSamples = len(trainReports)
    print 'diagnoses', diagnoses
    for z in diagnoses:
        print 'diag', z
        print z, ":", sum([z in l for l in trainLabels]) * 1. / numTrainSamples
    print len(trainLabels)

    testReports = [cleanReports[i] for i in idx[-500:]]
    testLabels = [labels[i] for i in idx[-500:]]
    print "Label dist for test"
    print "Sample label", testLabels[100]
    numTestSamples = len(testReports)
    for w in diagnoses:
        print w, ":", sum([w in l for l in testLabels]) * 1. / numTestSamples
    
    print len(testLabels)

    # mistakeIds = [102, 273, 310]
    # mistakeIds = [85, 213]
    # goldLabels = [testLabels[idx] for idx in mistakeIds]
    # yalaLabel = ['DCIS', 'no_DCIS', 'DCIS', 'DCIS',  'no_DCIS']

    # print 'goldLabels', goldLabels


    # for idx in mistakeIds:
    #     print "************************"
    #     print "MISTAKE ", idx
    #     print "gold", testLabels[idx]
    #     print testReports[idx]
    #     raw_input()

    write = True
    if write:

        with open(trainOutPath, "wb") as f: 
            for i in range(len(trainReports)):
                label = processLabels( trainLabels[i])
                report = trainReports[i]
                assert not "\n" in report
                f.write(report + ", " + " ".join(label) + '.\n')
        print "Saved", trainOutPath

        with open(testOutPath, "wb") as f: 
            for i in range(len(testReports)):
                label =  processLabels(testLabels[i])
                report = testReports[i]
                assert not "\n" in report
                f.write(report + ", " + " ".join(label) + '.\n')
        print "Saved", testOutPath