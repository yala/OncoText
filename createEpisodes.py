import pickle as p
import re
import random
from genBoostexaFiles import diagnoses
from genBoostexaFiles import genTrainTestFiles
from genBoostexaFiles import filterGold
import datetime
import pprint


random.seed(1)
dataPath = "deidentifiedPathReports.p"
outPath = "episodicDB.p"

metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution', 'BreastSide']

SIX_MONTHS=365/2


cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text", "filitiredOut"]


# Set write to true to generate train and test files for classification. 
# Set write to false to collace files for export
def binarizeFilesForClassification(write = True):
    allData = p.load(open(dataPath, 'rb'))
    goldData = [d for d in allData if 'Correct' in d]
    remainData = [d for d in allData if not 'Correct' in d]
    
    trainReports, trainLabels = getLabelsAndReports(goldData, write, True)
    restReports,  restLabels = getLabelsAndReports(remainData, write)

    retagedLabels = parseResultsFiles()

    stem = "boostexer/pathology_all"

    
    if write:
        genTrainTestFiles(trainReports, trainLabels, restReports, restLabels, stem)
    else:
        filiteredData = {}
        
        buildExport(filiteredData, trainLabels, 0)
        assert len(filiteredData) == len(trainLabels)
        buildExport(filiteredData, restLabels, len(trainLabels))
        assert len(filiteredData) == len(trainLabels) + len(remainData)

        return filiteredData

    return "NOT EXPORTING"

def buildExport(exportData, data, startIdx):
    for i in range(len(data)):
        record = {}
        colVals  = data[i]
        for j, col in enumerate(cols):
            if col == 'Report_Date_TimePlusX':
                date = colVals[j]
                yyyymmdd = date.split('T')[0]
                year, mo, day = [int(d) for d in yyyymmdd.split('-')]
                date = datetime.strptime(yyyymmdd, '%Y-%m-%d')
                record[col] = date
            else:
                record[col] = colVals[j]
        exportData[startIdx+i] = record


def preprocessReports(reports):
    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]

    return reports

def getLabelsAndReports(data, write = True):
    reports = [d['Report_Text'] for d in data]
    cleanReports = preprocessReports(reports)

    labels = []

    for i in range(len(data)):
        diags = []
        sample = data[i]
        for diag in diagnoses:
            if write:
                if diag in sample and sample[diag] == '1':
                    diags.append(diag)
                else:
                    diags.append('no_'+diag)
            else:
                diags.append(int(diag in sample and sample[diag] == '1'))

            if not write:
                for meta in metaData:
                    assert meta in sample
                    diags.append(sample[meta])

                diags.append(sample['Report_Text'])
                diags.append(cleanReports[i])

            labels.append(diags)

    filteredReport, filteredLabel = filterGold(cleanReports, labels)

    if write:
        cleanReports = filteredReport
        labels = filteredLabel

        return cleanReports, labels
    else:
        for report, label in zip(cleanReports, labels):
            label.append(report in filteredReport)
        return cleanReports, labels

def say(s):
    pprint.pprint(s)

def parseResultsFiles(debug = False):
    stem = "classification_results/class_results_all_"
    results = []
    i = 0
    for diag in diagnoses:
        with open(stem+diag+".txt", "rb") as f:
            samples = f.readlines()
        if i == 0:
            for k in range(len(samples)):
                results.append([])

        labels = [int(float(s.split()[2]) > 0) for s in samples]

        if debug:
            numExamples  = 10
            print "Raw class results"
            say(samples[:numExamples])
            print "Resulting labels"
            say(labels[:numExamples])

        for idx, l in enumerate(labels):
            results[idx].append(l)

        i += 1

    if debug:
        print 'len(results)', len(results)
        print 'len(results)[0]', 'len(diagnoses):', len(results[0]), len(diagnoses)
    return results

#TODO: Label MaxDX from labels
def getMaxDX(labels):
    return False

if __name__ == "__main__":

    train = False
    if train:
        binarizeFilesForClassification()


    buildExportBool = True
    if buildExportBool:
        exportData = binarizeFilesForClassification(buildExportBool)
