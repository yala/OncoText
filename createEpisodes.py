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
    labelDict = constantValidLabelDict

# Set write to true to generate train and test files for classification. 
# Set write to false to collace files for export
def binarizeFilesForClassification(write = True):
    allDataPath = redRawDBPath if MODE == "TAGHIAN" else dataPath
    allData = p.load(open(allDataPath, 'rb'))

    #valid input db isn't corrupted
    print "Validate source allData array from", allDataPath
    validateRepsDB(allData, flex= True)

    if MODE == "Breast":
        goldKey = 'Correct' 
        ## This datapath contains rule based generated anotations for diagnoses
        allData = p.load(open(dataPath, 'rb'))
    elif MODE == 'TAGHIAN':
        ## This datapath contains ML generated anotations for diagnoses
        goldKey = 'TaghianGold'

    goldData = [d for d in allData if goldKey in d and not( d[goldKey] == 0)]
   
    print "Num gold Data with DOBs", len([d for d in goldData if 'DOBPlusX' in d and not d['DOBPlusX'] == 0]), "/", len(goldData)
    remainData = [d for d in allData if not(goldKey in d) or d[goldKey] == 0]

    # For taghian, because TaghianGold has a different number of things annotated per diagnosis in gold
    # Using gold labels by themselves would be a pain, so we will re-annotate the whole thing.
    # Since the training error is ~0, this wont hurt us.
    if MODE == "TAGHIAN":
        remainData = allData
    print "Num remainData with DOBs", len([d for d in remainData if 'DOBPlusX' in d and not d['DOBPlusX'] == 0]), "/", len(remainData)
    
    export = not write

    trainReports, trainLabels = getLabelsAndReports(goldData, export)
    restReports,  restLabels =  getLabelsAndReports(remainData, export)
    assert len(restReports) == len(remainData)

    stem = allDataStem

    if write:
        genTrainTestFiles(trainReports, trainLabels, restReports, restLabels, stem)

    else:
        exportableData = {}

        print "Parse Result Files"
        if MODE == "Breast":
            classifierLabels = parseResultsFiles( "classification_results/Breast/class_results_")
        elif MODE == "TAGHIAN":
            classifierLabels = parseResultsFiles( "classification_results/Breast/red_class_results_all_")

        print "Retag Labels"
        restLabels = retagLabels(restLabels, classifierLabels)
        
        print "Exporting"
        if MODE == "Breast":
            buildExport(exportableData, trainLabels, 0)
            print "num DOBs retag train" , len([d for d in exportableData if 'DOBPlusX' in exportableData[d]])
            assert len(exportableData) == len(trainLabels)

        if MODE == "TAGHIAN":
            assert len(exportableData) == 0

        buildExport(exportableData, restLabels, len(exportableData))
        print "num DOBs retag rst" , len([d for d in exportableData if 'DOBPlusX' in exportableData[d]])

        validateRepsDB([exportableData[k] for k in exportableData], flex=True)

        if MODE == "Breast":
            assert len(exportableData) == len(trainLabels) + len(restLabels)
        else:
            assert len(exportableData) == len(restLabels)

        for key in exportableData:
            r = exportableData[key]
        
            if r['BreastSide'] == 'RIGHT':
                r['BreastSide'] = 1
            if r['BreastSide'] == 'LEFT':
                r['BreastSide'] = 0

        return exportableData

    return "NOT EXPORTING"

def retagLabels(oldLabels, newLabels):
    print  "db labels, classifier labels", len(oldLabels), len(newLabels)
    assert len(oldLabels)== len(newLabels)
    assert len(oldLabels[0]) == len(cols) or not 'DOBPlusX' in oldLabels[0]
    results = []
    for i in range(len(oldLabels)):
        print len(newLabels[i]) , len(diagnoses)
        assert len(newLabels[i]) == len(diagnoses)
        combinedLabels = newLabels[i] + oldLabels[i][len(diagnoses):]
        if 'PLACEHOLDER' in combinedLabels:
            print "newLabels", zip(cols,newLabels)
            print "old Labels", zip(cols, oldLabels)
            print "oldSupPart", zip(cols, oldLabels)[len(diagnoses):]
            raw_input()
        assert not 'PLACEHOLDER' in combinedLabels
        results.append( combinedLabels)
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
    reports = [d[reportTextKey] for d in data]
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
                    if diag in sample and str(sample[diag]) == '1':
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
                    if MODE == "TAGHIAN" and meta in hueLabels:
                        if not( sample[meta] in [0,1]):
                            print "meta", meta
                            print sample[meta]
                            assert False
                    diags.append(sample[meta])

            diags.append(sample['Report_Text_Segmented'])
            diags.append(sample['Report_Text'])
            diags.append(cleanReports[i])

        labels.append(diags)

    return cleanReports, labels


def say(s):
    pprint.pprint(s)

def parseResultsFiles(stem, debug = False):
    results = []
    i = 0
    for diag in diagnoses:
        with open(stem+replaceSpaces(diag)+".txt", "rb") as f:
            samples = f.readlines()
        if i == 0:
            for k in range(len(samples)):
                results.append([])

        if MODE == "Breast":
            labels = [int(float(s.split()[2]) > 0) for s in samples]
        elif MODE == "TAGHIAN":
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
def validateRepsDB(reps, flex = False, dirty = False):
    for r in reps:
        checks = diagnoses + hueLabels if MODE == "TAGHIAN" else diagnoses
    
        for c in checks:
            assert flex or c in r

            if MODE == "TAGHIAN":
                if c in diagnoses:
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



def buildEpisodes(data, labelMaxDXBool, debug = False):

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

    if MODE == "TAGHIAN":
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
        
        if MODE == "Breast":
            for diag in diagnoses:
                orResults = 0
                for rep in reports:
                    orResults = orResults or rep[diag]
                episode[diag] = orResults

        if MODE == "TAGHIAN":
            for diag in hueLabels:
                orResults = 0
                for rep in reports:
                    orResults = orResults or rep[diag]
                episode[diag] = orResults


            for diag in labelsForEpisodes:
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

            if MODE == "Breast":
                assert set(episode.keys() + ['DOBPlusX']) == set(diagnoses + metaData + (['MaxDX'] if labelMaxDXBool else [] )+['EndEpisode_Date_TimePlusX', 'Num_Reports', 'EpisodeID', 'DOBPlusX'])
            
            if MODE == "TAGHIAN":
                assert set(episode.keys() + ['DOBPlusX']) == set(labelsForEpisodes + hueLabels + metaData + (['MaxDX'] if labelMaxDXBool else [] )+['EndEpisode_Date_TimePlusX', 'Num_Reports', 'EpisodeID', 'DOBPlusX'])

        episodeDB.append(episode)

    if MODE == "TAGHIAN":
        for diag in labelsForEpisodes:
            print "count double label in ", countWeird[diag], "for diag", diag

    print "Num Reps", len(reportsDB)
    print "Num Epis", len(episodeDB)

    return reportsDB, episodeDB



def portToJSON(data, path, episodeMode = False):
    for report in data:
        try:
            if not isinstance(report['Report_Date_TimePlusX'], str):
                report['Report_Date_TimePlusX'] = report['Report_Date_TimePlusX'].isoformat()

            if 'EndEpisode_Date_TimePlusX' in report:
                if not isinstance(report['EndEpisode_Date_TimePlusX'], str):
                    report['EndEpisode_Date_TimePlusX'] = report['EndEpisode_Date_TimePlusX'].isoformat()

            if not report['DOBPlusX'] == 0  and not( isinstance(report['DOBPlusX'], str)):
                report['DOBPlusX'] = report['DOBPlusX'].isoformat()
        except Exception, e:
            print 'wtf'
            print report
            raw_input()

        if MODE == "Breast":
            breastLabels = diagnoses
        if MODE == "TAGHIAN":
            breastLabels = hueLabels
    
        for diag in breastLabels:
            if MODE == "TAGHIAN" and "Red "+ diag in diagnoses:
                print "skip"
                continue
            assert not diag== "Red DCIS"
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

        if MODE == "TAGHIAN":
            if episodeMode:
                redLabels = labelsForEpisodes
            else:
                redLabels = diagnoses
            
            for label in redLabels:
            
                if report[label] in JSONLabelDict:
                    report[label] = JSONLabelDict[report[label]]

                #Replace spaces in label name because otherwise website will breast
                assert "Red DCIS" in JSONLabelNameDict
                if label in JSONLabelNameDict:
                    temp = report[label]
                    del report[label]
                    assert not label in report
                    report[ JSONLabelNameDict[label] ] = temp

        mrn =  report["MRNPlusX"]
        del report["MRNPlusX"]
        report["FakeMRN"] = mrn
        
    chunkLen = len(data)/10
    for i in range(10):    
        jsonData = json.dumps(data[i* chunkLen : (i+1)*chunkLen])
        print "Len data to dump to JSON", len(jsonData)
        with open(path.split('.')[0]+'_'+str(i)+".json", 'wb') as f:
            f.write(jsonData)

if __name__ == "__main__":

    verbose = False

    train = False
    if train:
        binarizeFilesForClassification()


    buildExportBool = True
    if buildExportBool:
        print "Calling export"
        reportDB = binarizeFilesForClassification(False)
        print "dumping to ", outPath
        p.dump( reportDB, open(outPath, 'wb'))
    else: 
        reportDB = p.load(open(outPath, 'rb'))

    labelMaxDXBool = True
    if labelMaxDXBool:
        print "Calling labelMaxDXBool"
        getMaxDX(reportDB)
        if verbose:
            raw_input("Dump again? Press any key to continue")
        else:
            print "Dumping report db after max dx labeling"
        p.dump( reportDB, open(outPath, 'wb'))

    buildEpisodesBool = True
    if buildEpisodesBool:
        print "Calling build episode"
        reportDB, episodeDB = buildEpisodes(reportDB, labelMaxDXBool)
        if verbose:
            raw_input("Dump again? Press any key to continue")
        else:
            print "Dumping build episode"
        p.dump( reportDB, open(outPath, 'wb'))
        p.dump( episodeDB, open(episodePath, 'wb'))
    else:
        reportDB = p.load( open(outPath, 'rb'))
        episodeDB = p.load( open(episodePath, 'rb'))

    portToJSONBool = True
    if portToJSONBool:
        print "Dumping ReportDB"
        portToJSON(reportDB, JSONReportPath)
        print "Dumping EpisodeDB"
        portToJSON(episodeDB, JSONEpisodePath, True)



