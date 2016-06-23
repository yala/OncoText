import pickle as p
import re
import random
from genBoostexaFiles import diagnoses
from genBoostexaFiles import genTrainTestFiles
from genBoostexaFiles import filterGold
import datetime
import pprint
from operator import itemgetter

random.seed(1)
dataPath = "deidentifiedPathReports.p"
outPath = "episodicDB.p"
goldDataPath = 'goldPathReports.p'
lilyYedidDBPath = "EpisodesThatStartWithNeedleBiopsy.p"


metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution']

SIX_MONTHS = datetime.timedelta(365/2)


cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]


# Set write to true to generate train and test files for classification. 
# Set write to false to collace files for export
def binarizeFilesForClassification(write = True):
    allData = p.load(open(dataPath, 'rb'))
    goldBreastData = p.load(open(goldDataPath, 'rb'))
    goldData = [d for d in allData if 'Correct' in d]

    for i in range(len(goldData)):
        if 'BreastSide' in goldBreastData[i]:
            goldData[i]['BreastSide'] = goldBreastData[i]['BreastSide']

        for diag in diagnoses:
            sample1 = goldData[i]
            sample2 = goldBreastData[i]

            if diag in sample1:
                assert diag in sample2
                assert sample2[diag] == sample1[diag]
            else:
                assert diag not in sample2


    remainData = [d for d in allData if not 'Correct' in d]
    
    export = not write
    trainReports, trainLabels = getLabelsAndReports(goldData, export)
    restReports,  restLabels = getLabelsAndReports(remainData, export)

    assert len(trainReports) == len(trainReports)

    stem = "boostexer/pathology_all"

    if write:
        genTrainTestFiles(trainReports, trainLabels, restReports, restLabels, stem)

    else:
        exportableData = {}

        print "Parse Result Files"
        classifierLabels = parseResultsFiles()
        print "Retag Labels"
        restLabels = retagLabels(restLabels, classifierLabels)
        
        print "Exporting"
        buildExport(exportableData, trainLabels, 0)
        assert len(exportableData) == len(trainLabels)
        buildExport(exportableData, restLabels, len(trainLabels))
        assert len(exportableData) == len(trainLabels) + len(restLabels)

        return exportableData

    return "NOT EXPORTING"

def retagLabels(oldLabels, newLabels):
    assert len(oldLabels)== len(newLabels)
    assert len(oldLabels[0]) == len(cols)
    assert len(newLabels[0]) == len(diagnoses)
    results = []
    for i in range(len(oldLabels)):
        results.append( newLabels[i] + oldLabels[i][len(diagnoses):] )
    return results


def buildExport(exportData, data, startIdx):
    for i in range(len(data)):
        record = {}
        colVals  = data[i]
        for j, col in enumerate(cols):
            if col == 'Report_Date_TimePlusX':
                date = colVals[j]
                yyyymmdd = date.split('T')[0]
                year, mo, day = [int(d) for d in yyyymmdd.split('-')]
                date = datetime.datetime.strptime(yyyymmdd, '%Y-%m-%d')
                record[col] = date
            else:
                record[col] = colVals[j]
        exportData[startIdx+i] = record


def preprocessReports(reports):
    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]

    return cleanReports

def getLabelsAndReports(data, export = False):
    reports = [d['Report_Text'] for d in data]
    cleanReports = preprocessReports(reports)

    labels = []

    for i in range(len(data)):
        diags = []
        sample = data[i]
        for diag in diagnoses:
            if diag == u'BreastSide':
                if u'BreastSide' in sample:
                    diags.append(sample[diag])
                else:
                    diags.append("LEFT")
            else:
                if diag in sample and sample[diag] == '1':
                    diags.append(diag)
                else:
                    diags.append('no_'+diag)

        if export:
            for meta in metaData:
                if meta == "Correct" and not meta in sample:
                    diags.append(0)
                else:    
                    diags.append(sample[meta])

            diags.append(sample['Report_Text'])
            diags.append(cleanReports[i])

        labels.append(diags)

    filteredReport, filteredLabel = filterGold(cleanReports, labels)

    cleanReports = filteredReport
    labels = filteredLabel

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

def getMaxDX(data):
    for reportId in data:
        labels = data[reportId]
        if labels['Medullary'] == 1:
            labels['MaxDX'] = 'Medullary'
        elif labels['ILC'] == 1:
            labels['MaxDX'] = 'ILC'
        elif labels['IDC'] == 1:
            labels['MaxDX'] = 'IDC'
        elif labels['TubularCancer'] == 1:
            labels['MaxDX'] = 'TubularCancer'
        elif labels['CancerNOS'] == 1:
            labels['MaxDX'] = 'CancerNOS'
        elif labels['DCIS'] == 1:
            labels['MaxDX'] = 'DCIS'
        elif labels['CancerInvInsituNOS'] == 1:
            labels['MaxDX'] = 'CancerInvInsituNOS'
        elif labels['Borderline'] == 1:
            labels['MaxDX'] = 'Borderline'
        elif labels['InsituNOS'] == 1:
            labels['MaxDX'] = 'InsituNOS'
        elif labels['LCIS'] == 1:
            labels['MaxDX'] = 'LCIS'
        elif labels['ALH'] == 1:
            labels['MaxDX'] = 'ALH'
        elif labels['LobularNeoplasia'] == 1:
            labels['MaxDX'] = 'LobularNeoplasia'
        elif labels['ADH'] == 1:
            labels['MaxDX'] = 'ADH'
        elif labels['Phylodes'] == 1:
            labels['MaxDX'] = 'Phylodes'
        else:
            labels['MaxDX'] = 'None'

    return False


def multikeysort(items, debug = False):
    sortedItems = []
    for i in range(len(items)):
        items[i]['ReportID'] = i
        sortedItems.append(items[i])
    if debug:
        print " items pre"
        say(sortedItems)
        raw_input('Press any key to continue')
    for c in columns:
        sortedItems = sorted(sortedItems, key=itemgetter(c))
        if debug:
            print "Sorted by ", c
            say(sortedItems)
            raw_input('Press any key to continue')

    return sortedItems

def buildEpisodes(data):

    mrns = {}
    for i in range(len(data)):
        data[i]['ReportID'] = i

        if not data[i]['MRNPlusX'] in mrns:
            mrns[data[i]['MRNPlusX']] = {}

        if not data[i]['BreastSide'] in mrns[data[i]['MRNPlusX']]:
            mrns[data[i]['MRNPlusX']][data[i]['BreastSide']] = [data[i]]
        else:
            mrns[data[i]['MRNPlusX']][data[i]['BreastSide']].append(data[i])

    assert len(mrns) == 37729
    
    episodes = []
    episodeId = -1    
    for mrn in mrns:
        patient = mrns[mrn]
        for side in patient:
            patient[side] = sorted( patient[side], key=itemgetter('Report_Date_TimePlusX') )
            for idx, rep in enumerate(patient[side]):
                if idx == 0:
                    episodeId += 1
                    rep['EpisodeID'] = 'E'+str(episodeId)
                else:
                    prevVisit = patient[side][idx - 1]
                    if rep['Report_Date_TimePlusX'] - prevVisit['Report_Date_TimePlusX'] < SIX_MONTHS:
                        rep['EpisodeID'] = str(prevVisit['EpisodeID'])
                    else:
                        episodeId += 1
                        rep['EpisodeID'] = 'E'+str(episodeId)

                episodes.append(rep)

    return episodes

def isNeedleBiop(report, debug = False):
    reportText = report['Preprocessed_Report_Text']
    reportTextSaysNeedleBool = "NEEDLE BIOPSY".lower() in reportText.lower()

    typesOfCarcinoma = ["DCIS", "ILC", "IDC", "LCIS", "TubularCancer", \
                            "CancerNOS", "InsituNOS", "CancerInvInsituNOS",\
                            "ClingingCarcinoma", "Medullary", "ADH_DCIS"] 
    noCarcinomaBool  = not bool( sum( [report[c] == 1 for c in typesOfCarcinoma]))
    
    if debug:    
        print 'noCarcinomaBool', noCarcinomaBool
        print reportText
        print 'reportTextSaysNeedleBool', reportTextSaysNeedleBool
        raw_input()
    return reportTextSaysNeedleBool and noCarcinomaBool

def isExcision(report, debug = False):
    reportText = report['Preprocessed_Report_Text']
    return not "NEEDLE BIOPSY".lower() in reportText.lower()


def buildNeedleStartEpDB(data):
    resDB = []

    episodes = {}
    
    for rep in data:
        if rep['EpisodeID'] in episodes:
            episodes[rep['EpisodeID']].append(rep)
        else:
            episodes[rep['EpisodeID']] = [rep]

    for epId in episodes:
        episodes[epId] = sorted( episodes[epId], key=itemgetter('Report_Date_TimePlusX') )
        startAsNeedle = isNeedleBiop(episodes[epId][0])
        laterExcision = False
        for rep in episodes[epId][1:]: 
            if isExcision(rep):
                laterExcision = True
                break
        if startAsNeedle and laterExcision:
            resDB.append(episodes[epId])

    return resDB

if __name__ == "__main__":

    train = False
    if train:
        binarizeFilesForClassification()


    buildExportBool = False
    if buildExportBool:
        print "Calling export"
        exportData = binarizeFilesForClassification(False)
        print "dumping"
        p.dump( exportData, open(outPath, 'wb'))
    else: 
        exportData = p.load(open(outPath, 'rb'))

    labelMaxDXBool = False
    if labelMaxDXBool:
        getMaxDX(exportData)
        raw_input("Dump again? Press any key to continue")
        p.dump( exportData, open(outPath, 'wb'))

    buildEpisodesBool = False
    if buildEpisodesBool:
        exportData = buildEpisodes(exportData)
        raw_input("Dump again? Press any key to continue")
        p.dump( exportData, open(outPath, 'wb'))

    buildLilysDB = True
    if buildLilysDB:
        lilyDB = buildNeedleStartEpDB(exportData)
        print "Num Records in lilyDB", len(lilyDB)
        raw_input("Dump Lily's DB? Press any key to continue")
        p.dump(lilyDB, open(lilyYedidDBPath, 'wb'))



