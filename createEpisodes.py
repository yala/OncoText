import pickle as p
import re
import random
from genBoostexaFiles import diagnoses
from genBoostexaFiles import genTrainTestFiles
from genBoostexaFiles import filterGold


random.seed(1)
dataPath = "deidentifiedPathReports.p"
outPath = "episodicDB.p"

metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution', 'BreastSide']

def binarizeFilesForClassification():
    allData = p.load(open(dataPath, 'rb'))
    goldData = [d for d in allData if 'Correct' in d]
    remainData = [d for d in allData if not 'Correct' in d]

    trainReports, trainLabels = getLabelsAndReports(goldData)
    restReports,  restLabels = getLabelsAndReports(remainData)
    stem = "boostexer/pathology_all"
    genTrainTestFiles(trainReports, trainLabels, restReports, restLabels, stem)


def getLabelsAndReports(data):
    labels = []
    for i in range(len(data)):
        diags = []
        sample = data[i]
        for diag in diagnoses:
            if diag in sample and sample[diag] == '1':
                diags.append(diag)
            else:
                diags.append('no_'+diag)
        labels.append(diags)


    reports = [d['Report_Text'] for d in data]

    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]

    filteredReport, filteredLabel = filterGold(cleanReports, labels)

    cleanReports = filteredReport
    labels = filteredLabel

    return cleanReports, labels


#TODO: Label MaxDX from labels

if __name__ == "__main__":

    train = True
    if train:
        binarizeFilesForClassification()


    readClassifications = True