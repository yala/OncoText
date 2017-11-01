import pickle as p
import re
import random
import datetime
import pprint
from operator import itemgetter
import sys
import copy
sys.path.append("/home/nlp/pathology")
#sys.path.append('/home/nlp/pathology/preprocessDataset')
import preprocessRawDb
from constants import *
random.seed(1)
labelDict = constantValidLabelDict

# Read boost result files and consolidate into a single database format
def aggregateResults(allData, stem, export_as_list=False):

    #valid input db isn't corrupted

    def isGold(r):
        isTaghian = 'TaghianGold' in r and r['TaghianGold'] == 1
        isHughes = 'Correct' in r and r['Correct'] == 'Y'
        return isTaghian or isHughes

    for r in allData:
        if not "MRNPlusX" in r:
            r["MRNPlusX"]= "0"
            r["Institution"] ="Kinyas"
            r["Report_Date_TimePlusX"] = datetime.datetime.now().isoformat()
    
    trainData = [d for d in allData if isGold(d)]
        

    # For taghian, because TaghianGold has a different number of things annotated per diagnosis in gold
    # Using gold labels by themselves would be a pain, so we will re-annotate the whole thing.
    # Since the training error is ~0, this wont hurt us.
    
    remainData = allData
    print "Num remainData with DOBs", len([d for d in remainData if 'DOBPlusX' in d and not d['DOBPlusX'] == 0]), "/", len(remainData)
    
    ## gen train data

    trainReports, trainLabels = getLabelsAndReports(trainData)
    restReports,  restLabels =  getLabelsAndReports(remainData)
    assert len(restReports) == len(remainData)


    exportableData = {}

    print "Parse Result Files"
    
    classifierLabels = parseResultsFiles(stem)

    print "Retag Labels"
    restLabels = retagLabels(restLabels, classifierLabels)
    
    print "Exporting"
    
    assert len(exportableData) == 0

    buildExport(exportableData, restLabels, len(exportableData))
    print "num DOBs retag rst" , len([d for d in exportableData if 'DOBPlusX' in exportableData[d]])

    validateRepsDB([exportableData[k] for k in exportableData], flex=True)

    assert len(exportableData) == len(restLabels)

    if export_as_list:
        db_as_list = [exportableData[k] for k in exportableData]
	return db_as_list
    return exportableData

# HELPER: read the result files and return the tags
def retagLabels(oldLabels, newLabels):
    print  "db labels, classifier labels", len(oldLabels), len(newLabels)
    assert len(oldLabels)== len(newLabels)
    assert len(oldLabels[0]) == len(cols) or not 'DOBPlusX' in oldLabels[0]
    results = []
    for i in range(len(oldLabels)):
        if not len(newLabels[i]) == len(boostexer_diagnoses):
            print newLabels[i], "has len", len(newLabels[i]), "!=", len(boostexer_diagnoses)
        assert len(newLabels[i]) == len(boostexer_diagnoses)
        combinedLabels = newLabels[i] + oldLabels[i][len(boostexer_diagnoses):]
        if 'PLACEHOLDER' in combinedLabels:
            print "newLabels", zip(cols,newLabels)
            print "old Labels", zip(cols, oldLabels)
            print "oldSupPart", zip(cols, oldLabels)[len(boostexer_diagnoses):]
            raw_input()
        assert not 'PLACEHOLDER' in combinedLabels
        results.append( combinedLabels)
    return results

# HELPER
def buildExport(exportData, data, startIdx):
    for i in range(len(data)):
        record = {}
        colVals  = data[i]
        for j, col in enumerate(cols):
            if col in  ['Report_Date_TimePlusX', 'DOBPlusX']:
                date = colVals[j]
                if date == 0 or isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
                    record[col] = date
                    continue
                yyyymmdd = date.split('T')[0]
                try:
                    date = preprocessRawDb.utcToDate(date)#datetime.datetime.strptime(yyyymmdd, '%Y-%m-%d')
                    record[col] = date
                except Exception, e:
                    print date
                    record[col] = date
                    print "unlabled to parse", date,"into datetime datetime object"
                    #assert False
            else:
                record[col] = colVals[j]
        exportData[startIdx+i] = record



# Function takes [ reports ] and returns a tuple or reports, labels
# If export is true, returns only diagnoses, if false, also returns metaData
def getLabelsAndReports(data):
    reports = [d[reportTextKey] for d in data]

    labels = []

    for i in range(len(data)):
        diags = []
        sample = data[i]

        for diag in boostexer_diagnoses:    
            if diag in sample and not sample[diag] == None and sample[diag] in labelDict[diag]:
                diags.append(sample[diag])

                assert replaceSpaces(sample[diag]) in labelDict[diag]

            else:
                diags.append('PLACEHOLDER')

        for meta in metaData:
            if (meta == "Correct"  or meta == "DOBPlusX") and not meta in sample:
                diags.append(0)
            else:
                if not "Institution" in sample:
                    sample["Institution"] = "Unkown"
                if not meta in sample:
                    print "Meta",meta, "missing from sample:", sample,"!"

                assert meta in sample
                diags.append(sample[meta])

        diags.append(sample['Report_Text_Segmented'])
        diags.append(sample['Report_Text'])

        labels.append(diags)

    return reports, labels


def say(s):
    pprint.pprint(s)

def parseResultsFiles(stem, debug = False):
    results = []
    i = 0
    for diag in boostexer_diagnoses:
        with open(stem+replaceSpaces(diag)+".txt", "rb") as f:
            samples = f.readlines()

        if len(samples) == 0:
            print "Following file missing annotations"
            print diag
            assert False
        if i == 0:
            for k in range(len(samples)):
                results.append([])

       
        labels = []
        for sample in samples:
            rawProbs = [float(s) for s in sample.split()]
            rawGuessProbs = rawProbs[len(rawProbs)/2:]
            guessIndx = rawGuessProbs.index(max(rawGuessProbs))
            guessText = labelDict[diag][guessIndx]
            labels.append(guessText)

        if debug:
            numExamples  = 10
            print "Diag", diag
            print "Raw class results"
            say(samples[:numExamples])
            print "Resulting labels"
            say(labels[:numExamples])

        for idx, l in enumerate(labels):
            results[idx].append(l)

        i += 1

    if debug:
        print 'len(results)', len(results)
        print 'len(results)[0]', 'len(boostexer_diagnoses):', len(results[0]), len(boostexer_diagnoses)
    return results

#Iterate though reports in data-dict and get maxDx
def getMaxDX(data):
    for key in data:
        report = data[key]
        report['MaxDX'] = getMaxDXSingleReport(report)
        data[key] = report
    return False

def getMaxDXSingleReport(report):
    if 'Medullary' in report and report['Medullary'] == 1:
        return 'Medullary'
    elif ('ILC' in report and report['ILC'] == 1) or ('Red ILC' in report and report['Red ILC'] == 'Present'):
        return  'ILC'
    elif ('IDC' in report and report['IDC'] == 1) or ('Red IDC' in report and report['Red IDC'] == 'Present'):
        return  'IDC'
    elif 'TubularCancer' in report and report['TubularCancer'] == 1:
        return  'TubularCancer'
    elif 'CancerNOS' in report and report['CancerNOS'] == 1:
        return  'CancerNOS'
    elif ('DCIS' in report and report['DCIS'] == 1) or ('Red DCIS' in report and report['Red DCIS']=="Present"):
        return  'DCIS'
    elif 'CancerInvInsituNOS' in report and report['CancerInvInsituNOS'] == 1:
        return  'CancerInvInsituNOS'
    elif 'Borderline' in report and report['Borderline'] == 1:
        return  'Borderline'
    elif 'InsituNOS' in report and report['InsituNOS'] == 1:
        return  'InsituNOS'
    elif ('LCIS' in report and report['LCIS'] == 1) or ('Red LCIS' in report and report['Red LCIS'] == 'Present'):
        return  'LCIS'
    elif ('ALH' in report and report['ALH'] == 1) or ('Red ALH' in report and report['Red ALH'] == 'Present'):
        return  'ALH'
    elif 'LobularNeoplasia' in report and report['LobularNeoplasia'] == 1:
        return  'LobularNeoplasia'
    elif ('ADH' in report and report['ADH'] == 1) or ('Red ADH' in report and report['Red ADH'] == 'Present'):
        return  'ADH'
    elif 'Phylodes' in report and report['Phylodes'] == 1:
        return  'Phylodes'
    else:
        return 'None'


## Flex (for flexible) flag means we runs asserts on a label only if it is present in the sample
## We don't enforce that all labels are present. this is useful for pre-complete dbs
## dirty flag is useful for when we aren't enforcing that the values are in the label dict, pre-preprocess
def validateRepsDB(reps, flex = False, dirty = False):
    for r in reps:
        checks = boostexer_diagnoses + hueLabels if MODE == "TAGHIAN" else boostexer_diagnoses
    
        for c in checks:
            assert flex or c in r

            if MODE == "TAGHIAN":
                if c in boostexer_diagnoses:
                    if flex:
                        if c in r and not( replaceSpaces(r[c]) in labelDict[c] or dirty):
                            print 'r[c]',  r[c]
                            print 'c', c
                            print labelDict[c]
                        assert not (c in r) or replaceSpaces(r[c]) in labelDict[c] or dirty
                    else:
                        assert c in r and (replaceSpaces(r[c]) in labelDict[c] or dirty)
                else:
                    assert c in hueLabels
                    if c in r and not (r[c] in [0,1,'RIGHT','LEFT', '0', '1']):
                        print "C", c
                        print "r[c]", r[c]
                        assert False


# Aggregate reports into list of dicts for ReportDB format, and a list of flattened report sequences for EpisodeDB format
def buildEpisodes(data, labelMaxDXBool, debug = False):
    for i in data:
        d = data[i]
        d['MRNPlusX'] = d['MRN'] if 'MRN' in d else d['MRNPlusX']
        d['Report_Date_TimePlusX'] = preprocessRawDb.utcToDate(d['Report_Date_Time'] if 'Report_Date_Time' in d else d['Report_Date_TimePlusX'])
        data[i] = d
    mrns = {}
    for i in range(len(data)):

        if not data[i]['MRNPlusX'] in mrns:
            mrns[data[i]['MRNPlusX']] = {}

        if not data[i]['Red BreastSide'] in mrns[data[i]['MRNPlusX']]:
            mrns[data[i]['MRNPlusX']][data[i]['Red BreastSide']] = [data[i]]
        else:
            mrns[data[i]['MRNPlusX']][data[i]['Red BreastSide']].append(data[i])

    #Structure : List of Reports with Episode IDs
    reportsDB = []
    episodesAggregator = {} # Use to construct episodes DB
    episodeDateDict = {} ## Use this to store Date -> episode Id for each MRN. use this to reorder episodes by date
    episodeRelabelDict = {} ## Use this to store episoideID to new Episode ID
    for mrn in mrns:
        patient = mrns[mrn]
        episodeId = -1    
        episodeDateDict[mrn] = []
        for side in patient:
            patient[side] = sorted( patient[side], key=itemgetter('Report_Date_TimePlusX') )
            for idx, rep in enumerate(patient[side]):
                #Correct labeling of Correct Flag
                rep['Correct'] = 1 if rep['Correct'] == 'Y' else 0

                if idx == 0:
                    episodeId += 1
                    rep['EpisodeID'] = 't'+str(episodeId)
                    episodeDateDict[mrn].append( {'EpStartTime':rep['Report_Date_TimePlusX'], 'epID':'t'+str(episodeId) })
                else:
                    prevVisit = patient[side][idx - 1]
                    if rep['Report_Date_TimePlusX'] - prevVisit['Report_Date_TimePlusX'] < SIX_MONTHS:
                        rep['EpisodeID'] = prevVisit['EpisodeID']
                    else:
                        episodeId += 1
                        rep['EpisodeID'] = 't'+str(episodeId)
                        episodeDateDict[mrn].append( {'EpStartTime':rep['Report_Date_TimePlusX'], 'epID':'t'+str(episodeId) })

                aggregatorKey = mrn+"ep"+str(episodeId)
                if aggregatorKey in episodesAggregator:
                    episodesAggregator[aggregatorKey].append(rep)
                else:
                    episodesAggregator[aggregatorKey] = [rep]

                patient[side][idx] = rep

                reportsDB.append(rep)


    ## Relabel MRNs with better chronological episode numbers
    for mrn in mrns:
        patient = mrns[mrn]
        episodeRelabelDict[mrn] = {}
        epDates = sorted( episodeDateDict[mrn], key=itemgetter('EpStartTime') )
        for indx, dateDict in enumerate(epDates):
            epID = dateDict['epID']
            episodeRelabelDict[mrn][epID] = indx

        assert len(episodeDateDict[mrn]) == len(epDates)
    assert len(episodeRelabelDict) == len(mrns)


    for rep in reportsDB:
        oldID = rep['EpisodeID']
        newID = episodeRelabelDict[rep['MRNPlusX']][oldID]
        rep['EpisodeID'] = newID
        assert isinstance(rep['EpisodeID'] , int)
        
    #Run assert to makesure report DB is what we expect
    validateRepsDB(reportsDB)

    #Structure: List of Episodes where-all constituent reports are combined or-wise
    episodeDB = []
    countWeird = {}

    for diag in labelsForEpisodes:
        countWeird[diag] = 0

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


        for diag in boostexer_diagnoses:
            res = defaultLabelDict[diag]
            lastRep = ''
            for rep in reports:
                assert rep[diag] in labelDict[diag]
                if rep[diag] not in defaultLabelDict[diag]:
                    if not(res == defaultLabelDict[diag] or res == rep[diag]):
                        countWeird[diag] +=1
                        if countWeird[diag] < 5 and debug:
                            print "DIAG", diag
                            print "Former", res
                            print 'formerText', lastRep
                            print "Current", rep[diag]
                            print "current text", rep[reportTextKey]
                            raw_input()
                        lastRep = rep[reportTextKey]
                        res += ', ' + rep[diag]
                    else:
                        res = rep[diag]
            if not res in labelDict[diag] and debug:
                print "Diag", diag, "is", res
            episode[diag] = res

            if labelMaxDXBool:
                episode['MaxDX'] = getMaxDXSingleReport(episode)
            episode['Num_Reports'] = len(reports)
            episode['Institution'] = reports[-1]['Institution']

            
        assert set(episode.keys() + ['DOBPlusX']) == set(labelsForEpisodes + hueLabels + metaData + (['MaxDX'] if labelMaxDXBool else [] )+['EndEpisode_Date_TimePlusX', 'Num_Reports', 'EpisodeID', 'DOBPlusX'])                

        episodeDB.append(episode)


    for diag in labelsForEpisodes:
        print "count double label in ", countWeird[diag], "for diag", diag

    print "Num Reps", len(reportsDB)
    print "Num Epis", len(episodeDB)

    return reportsDB, episodeDB


def run(allData, stem, save=False):
    filtData = removeUnexpectedColumns(allData)     
    print "Calling export"
    reportDB = aggregateResults(filtData, stem)
    print "Calling labelMaxDXBool"
    getMaxDX(reportDB)
    print "Calling build episode"
    reportDB, episodeDB = buildEpisodes(reportDB, True)
    if save:
        p.dump( reportDB, open(outPath, 'wb'))
        p.dump( episodeDB, open(episodePath, 'wb'))
    reportDB, episodeDB

# Remove unexpected cols for code safety
def removeUnexpectedColumns(allData):
    cleanData = []
    for r in allData:
        c = {}
        for k in r:
            if k in cols:
                c[k] = r[k]
        cleanData.append(c)
    return cleanData

if __name__ == "__main__": 
    allDataPath = '/home/nlp/pathology/reportDBAPI_test.p'
    allData = p.load(open(allDataPath, 'rb'))['mghMar']
    aggregateResults(allData, "/home/nlp/pathology/classification_results/API/Prod_mghMar_")





