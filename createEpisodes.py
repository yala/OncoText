import pickle as p
import re
import random
from genBoostexaFiles import diagnoses
from genBoostexaFiles import genTrainTestFiles
from genBoostexaFiles import filterGold
import datetime
import pprint
from operator import itemgetter
import json
from constants import *

random.seed(1)
if MODE == "TAGHIAN":
    labelDict = p.load(open('redLabelDict.p', 'rb'))

# Set write to true to generate train and test files for classification. 
# Set write to false to collace files for export
def binarizeFilesForClassification(write = True):
    allData = p.load(open(dataPath, 'rb'))

    if MODE == "Breast":
        goldKey = 'Correct' 
        ## This datapath contains rule based generated anotations for diagnoses
        allData = p.load(open(dataPath, 'rb'))
    elif MODE == 'TAGHIAN':
        ## This datapath contains ML generated anotations for diagnoses
        allData = p.load(open(redRawDBPath, 'rb'))
        goldKey = 'TaghianGold'

    goldData = [d for d in allData if goldKey in d and not( d[goldKey] == 0)]

    print "Num gold Data with DOBs", len([d for d in goldData if 'DOBPlusX' in d and not d['DOBPlusX'] == 0]), "/", len(goldData)

    remainData = [d for d in allData if not(goldKey in d) or d[goldKey] == 0]
    print "Num remainData with DOBs", len([d for d in remainData if 'DOBPlusX' in d and not d['DOBPlusX'] == 0]), "/", len(remainData)
    
    export = not write
    trainReports, trainLabels = getLabelsAndReports(goldData, export)
    restReports,  restLabels = getLabelsAndReports(remainData, export)

    stem = allDataStem

    if write:
        genTrainTestFiles(trainReports, trainLabels, restReports, restLabels, stem)

    else:
        exportableData = {}

        print "Parse Result Files"
        if MODE == "Breast":
            classifierLabels = parseResultsFiles( "classification_results/Breast/class_results_all_")
        elif MODE == "TAGHIAN":
            classifierLabels = parseResultsFiles( "classification_results/Breast/red_class_results_all_")

        print "Retag Labels"
        restLabels = retagLabels(restLabels, classifierLabels)
        
        print "Exporting"
        buildExport(exportableData, trainLabels, 0)
        print "num DOBs retag train" , len([d for d in exportableData if 'DOBPlusX' in exportableData[d]])
        assert len(exportableData) == len(trainLabels)
        buildExport(exportableData, restLabels, len(trainLabels))
        print "num DOBs retag rst" , len([d for d in exportableData if 'DOBPlusX' in exportableData[d]])
        assert len(exportableData) == len(trainLabels) + len(restLabels)

        for key in exportableData:
            r = exportableData[key]
        
            if r['BreastSide'] == 'RIGHT':
                r['BreastSide'] = 1
            if r['BreastSide'] == 'LEFT':
                r['BreastSide'] = 0

        return exportableData

    return "NOT EXPORTING"

def retagLabels(oldLabels, newLabels):
    assert len(oldLabels)== len(newLabels)
    assert len(oldLabels[0]) == len(cols) or not 'DOBPlusX' in oldLabels[0]
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
            if col in  ['Report_Date_TimePlusX', 'DOBPlusX']:
                date = colVals[j]
                if date == 0 or isinstance(date, datetime.datetime):
                    record[col] = date
                    continue

                yyyymmdd = date.split('T')[0]
                try:
                    date = datetime.datetime.strptime(yyyymmdd, '%Y-%m-%d')
                    record[col] = date
                except Exception, e:
                    print yyyymmdd
                    record[col] = yyyymmdd
                    raw_input()
            else:
                record[col] = colVals[j]
        exportData[startIdx+i] = record


def preprocessReports(reports):
    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]

    return cleanReports

# Function takes [ reports ] and returns a tuple or reports, labels
# If export is true, returns only diagnoses, if false, also returns metaData
def getLabelsAndReports(data, export = False):
    reports = [d['Report_Text'] for d in data]
    cleanReports = preprocessReports(reports)

    labels = []

    for i in range(len(data)):
        diags = []
        sample = data[i]

        for diag in diagnoses:
            if MODE == "Breast":
                if diag == u'BreastSide':
                    if u'BreastSide' in sample:
                        diags.append(sample[diag])
                    else:
                        diags.append("LEFT")
                else:
                    if diag in sample and sample[diag] == '1':
                        diags.append(1)
                    else:
                        diags.append(0)
            elif MODE == 'TAGHIAN':
                if diag in sample and not sample[diag] == None:
                    diags.append(sample[diag])
                    assert replaceSpaces(sample[diag]) in labelDict[diag]
                else:
                    diags.append('PLACEHOLDER')


        if export:
            for meta in metaData:
                if (meta == "Correct"  or meta == "DOBPlusX") and not meta in sample:
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

def parseResultsFiles(stem, debug = False):
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

#Iterate though reports in data-dict and get maxDx
def getMaxDX(data):
    for key in data:
        report = data[key]
        report['MaxDX'] = getMaxDXSingleReport(report)
        data[key] = report
    return False

def getMaxDXSingleReport(report):
    if report['Medullary'] == 1:
        return 'Medullary'
    elif report['ILC'] == 1:
        return  'ILC'
    elif report['IDC'] == 1:
        return  'IDC'
    elif report['TubularCancer'] == 1:
        return  'TubularCancer'
    elif report['CancerNOS'] == 1:
        return  'CancerNOS'
    elif report['DCIS'] == 1:
        return  'DCIS'
    elif report['CancerInvInsituNOS'] == 1:
        return  'CancerInvInsituNOS'
    elif report['Borderline'] == 1:
        return  'Borderline'
    elif report['InsituNOS'] == 1:
        return  'InsituNOS'
    elif report['LCIS'] == 1:
        return  'LCIS'
    elif report['ALH'] == 1:
        return  'ALH'
    elif report['LobularNeoplasia'] == 1:
        return  'LobularNeoplasia'
    elif report['ADH'] == 1:
        return  'ADH'
    elif report['Phylodes'] == 1:
        return  'Phylodes'
    else:
        return 'None'


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

def buildEpisodes(data, debug = False):

    mrns = {}
    for i in range(len(data)):
        data[i]['ReportID'] = i

        if not data[i]['MRNPlusX'] in mrns:
            mrns[data[i]['MRNPlusX']] = {}

        if not data[i]['BreastSide'] in mrns[data[i]['MRNPlusX']]:
            mrns[data[i]['MRNPlusX']][data[i]['BreastSide']] = [data[i]]
        else:
            mrns[data[i]['MRNPlusX']][data[i]['BreastSide']].append(data[i])

    #Structure : List of Reports with Episode IDs
    reportsDB = []
    episodesAggregator = {} # Use to construct episodes DB
    for mrn in mrns:
        patient = mrns[mrn]
        episodeId = -1    
        for side in patient:
            patient[side] = sorted( patient[side], key=itemgetter('Report_Date_TimePlusX') )
            for idx, rep in enumerate(patient[side]):
                #Correct labeling of Correct Flag
                rep['Correct'] = 1 if rep['Correct'] == 'Y' else 0

                if idx == 0:
                    episodeId += 1
                    rep['EpisodeID'] = episodeId
                else:
                    prevVisit = patient[side][idx - 1]
                    if rep['Report_Date_TimePlusX'] - prevVisit['Report_Date_TimePlusX'] < SIX_MONTHS:
                        rep['EpisodeID'] = prevVisit['EpisodeID']
                    else:
                        episodeId += 1
                        rep['EpisodeID'] = episodeId

                aggregatorKey = mrn+"ep"+str(episodeId)
                if aggregatorKey in episodesAggregator:
                    episodesAggregator[aggregatorKey].append(rep)
                else:
                    episodesAggregator[aggregatorKey] = [rep]

                patient[side][idx] = rep

                reportsDB.append(rep)


    #Structure: List of Episodes where-all constituent reports are combined or-wise
    episodeDB = []


    for aggKey in episodesAggregator:
        episode = {}
        reports = episodesAggregator[aggKey]
        reports = sorted( reports, key=itemgetter('Report_Date_TimePlusX'))
        endTime = reports[-1]['Report_Date_TimePlusX']

        episode['EndEpisode_Date_TimePlusX'] = endTime
        episode['Report_Date_TimePlusX'] = reports[0]['Report_Date_TimePlusX']
        episode['EpisodeID'] = reports[0]['EpisodeID']

        assert reports[0]['EpisodeID'] == reports[-1]['EpisodeID']
        for label in metaData:
            if label == 'Report_Date_TimePlusX' or label == 'Institution':
                continue
            episode[label] = reports[0][label]

        for diag in diagnoses:
            orResults = 0
            for rep in reports:
                orResults = orResults or rep[diag]
            episode[diag] = orResults

        episode['MaxDX'] = getMaxDXSingleReport(episode)
        episode['Num_Reports'] = len(reports)
        episode['Institution'] = reports[-1]['Institution']
        assert set(episode.keys() + ['DOBPlusX']) == set(diagnoses + metaData + ['MaxDX', 'EndEpisode_Date_TimePlusX', 'Num_Reports', 'EpisodeID', 'DOBPlusX'])

        episodeDB.append(episode)

    return reportsDB, episodeDB



def portToJSON(data, path):
    for report in data:    
        report['Report_Date_TimePlusX'] = report['Report_Date_TimePlusX'].isoformat()

        if 'EndEpisode_Date_TimePlusX' in report:
            report['EndEpisode_Date_TimePlusX'] = report['EndEpisode_Date_TimePlusX'].isoformat()

        if not report['DOBPlusX'] == 0 :
            report['DOBPlusX'] = report['DOBPlusX'].isoformat()


        for diag in diagnoses:
            sample = report[diag]
            if not (sample == 1 or sample == 0):
                if "no_" in sample:
                    report[diag] = 0
                else:
                    if diag == "BreastSide":
                        if sample == "RIGHT":
                            report[diag] = 1 
                        else:
                            report[diag] = 0
                    elif not sample == diag:
                        print sample, diag
                        raw_input()
                    report[diag] = 1

    jsonData = json.dumps(data)
    print "Len data to dump to JSON", len(jsonData)
    with open(path, 'wb') as f:
        f.write(jsonData)

if __name__ == "__main__":

    train = True
    if train:
        binarizeFilesForClassification()


    buildExportBool = False
    if buildExportBool:
        print "Calling export"
        reportDB = binarizeFilesForClassification(False)
        print "dumping to ", outPath
        p.dump( reportDB, open(outPath, 'wb'))
    else: 
        reportDB = p.load(open(outPath, 'rb'))

    labelMaxDXBool = False
    if labelMaxDXBool:
        getMaxDX(reportDB)
        raw_input("Dump again? Press any key to continue")
        p.dump( reportDB, open(outPath, 'wb'))

    buildEpisodesBool = False
    if buildEpisodesBool:
        reportDB, episodeDB = buildEpisodes(reportDB)
        raw_input("Dump again? Press any key to continue")
        p.dump( reportDB, open(outPath, 'wb'))
        p.dump( episodeDB, open(episodePath, 'wb'))
    else:
        reportDB = p.load( open(outPath, 'rb'))
        episodeDB = p.load( open(episodePath, 'rb'))

    portToJSONBool = False
    if portToJSONBool:
        portToJSON(reportDB, JSONReportPath)
        portToJSON(episodeDB, JSONEpisodePath)



