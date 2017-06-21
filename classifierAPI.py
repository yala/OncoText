import cPickle as p
from constants import *
import sys
sys.path.append("buildNewDataset")
sys.path.append("trainClassifier")
sys.path.append("preprocessDataset")
sys.path.append("analysis")
sys.path.append("rnn")
sys.path.append("adhoc")
import createEpisodes
import preprocessTrain
import preprocessUnlabeled
import exportToJSON
import generateClassifierFilesForProd
import generateClassifierFilesForDev
import preprocessRawDb
import interpretResults
import getAtypias
import evalModelRun
from operator import itemgetter
import subprocess
from flask import Flask
from flask import render_template
from flask import request
import json
from datetime import datetime
import re
import MySQLdb
import copy
import time

app = Flask(__name__)
app.config.from_object(__name__)
DB_TRAIN_PATH = "reportDBAPI_train.p"
DB_UNLABLED_PATH = "reportDBAPI_test.p"



## Handle relevant initialization of files

rawPath = "reportDB+red+clean.p"
additPath = "additionalTrainRepsMar10.p"
raws = p.load(open(rawPath,'rb')) + p.load( open(additPath,'rb'))

def hasCat(r, cat, loose=False):
    for c in cat:
        if not loose:
            if r[c] == 'Present':
                return True
        else:
            if c in r:
                return True
    return False

def isAnnotation(r):
    return hasCat(r, diagnoses, loose=True)

limDefault = True
base = []
for r in raws:
    r['Owner'] = 'default'
    if isAnnotation(r) and limDefault:
        base.append(r)
print "Len base", len(base)

try:
    db_train = p.load(open(DB_TRAIN_PATH,'rb'))
    db_unlabeled = p.load(open(DB_UNLABLED_PATH,'rb'))
except Exception, e:
    ## Data doesn't exist so init base and preprocess neural min
    print "Init db_train"
    db_train = {'default':base}
    db_unlabeled = {'default': base[:10]}
    neuralTrain = preprocessTrain.main(base)
    p.dump(neuralTrain, open('rnn/diagDictTrain.p','wb'))
    p.dump(db_train, open(DB_TRAIN_PATH,'wb'))
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH,'wb'))



RequiredPreprocessFields = ['Report_Text', "Report_Date_TimePlusX"]
RequiredTrainDbFields = ['ReportID', 'Report_Text_Segmented']


## Given a JSON list of dicts, where  each dict represent a report:
## Parse the dict for daignoses, and add annotations if found
##  @name specifies user, izzy don't worry about this
## @raw specifies if the data has been preprocessed before,
## Example:
## [ {Report_Text: }]
## @return: 0
@app.route("/addTrain", methods=['POST'])
def addTrainData():
    db_train = p.load(open(DB_TRAIN_PATH,'rb'))
    data = json.loads(request.data) or []
    name = request.args.get("name") or "default"
    #return "S"
    if len(data) > 0:
        print "data has keys", data[0].keys()
    print "len data is", len(data)
    print "name is", name

    if not validateTrainDb(data):
        data = preprocessReports(data)

    if not name in db_train:
        print "Adding", name, "to db_train"
        db_train[name] = base

    ## mark the files to note as annoations
    for r in data:
        r['Owner'] = name
        for d in diagnoses:
            if d in r:
                r['TaghianGold'] = 1

    db_train[name].extend(data)
    print "Len train", len(db_train[name])
    p.dump(db_train, open(DB_TRAIN_PATH,'wb'))
    print db_train.keys()
    return "Success"

## Given a JSON list of dicts, where  each dict represent a report:
## Parse the dict for daignoses, and add annotations if found
##  @name specifies user, izzy don't worry about this
## @raw specifies if the data has been preprocessed before,
## Example:
## [ {Report_Text: }]
## @return: 0
@app.route("/addUnlabeled", methods=['POST'])
def addUnlabeledData():
    db_unlabeled = p.load(open(DB_UNLABLED_PATH,'rb'))
    data = json.loads(request.data) or []
    name = request.args.get("name") or "default"
    raw = request.args.get("raw") or False
    #return "S"
    print "name is", name
    # Preprocess bilaterals if need be
    if raw:
        data = preprocessReports(data)

    validateTrainDb(data)

    if not name in db_unlabeled:
        print "Adding", name, "to db_unlabeled"
        db_unlabeled[name] = []
    ## mark the files to note as annoations
    for r in data:
        r['Owner'] = name
        for d in diagnoses:
            if d in r:
                r['TaghianGold'] = 1

    db_unlabeled[name].extend(data)
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH,'wb'))
    print db_unlabeled.keys()
    return "Success"




## Does all necessary preprocessing on the training set for a given user
## Return 0
@app.route("/updateTrainSet", methods=['GET'])
def updateTrainSet():
    #return "S"
    db_train = p.load(open(DB_TRAIN_PATH,'rb'))
    name = request.args.get("name") or "default"

    ## Generate relevant files in some directory with a name path
    trainDb = db_train[name]
    stem = "boostexer/breast/api/"+"Prod"+"_"+name+"_"
    trainDb = db_train[name] + db_train['default']
    generateClassifierFilesForProd.binarizeFilesForClassification(trainDb, stem, writeTrain=True, writeTest=False)
    preprocessTrain.main(trainDb)

    diagDictNew = preprocessTrain.main(trainDb)
    p.dump(diagDictNew, open('rnn/diagDictTrain_'+name+".p",'wb'))
    return "Success"


## Does all necessary preprocessing for test data given a batch_id in the unlabled data
## Script will prepare neural model and boosting model to evaluate on all reps where r['batch_id'] is in
## the list of id's specified. If batch_id's is ommited, this will run across all unlabled data which may be very expensive.
## Return 0
@app.route("/updateUnlabeledSet", methods=['GET'])
def updateUnlabeledSet():
    #return "S"
    db_test_all = p.load(open(DB_UNLABLED_PATH,'rb'))
    name = request.args.get("name") or "default"
    batch_id = request.args.get("batch_id") or "none"
    db_test = db_test_all[name]
    test_filt = db_test if batch_id == "none" else [d for d in db_test if "batch_id" in d and d["batch_id"] in batch_id]
    ## Generate relevant files in some directory with a name path
    stem = "boostexer/breast/api/"+"Prod"+"_"+name+"_"
    generateClassifierFilesForProd.binarizeFilesForClassification(test_filt, stem, writeTrain=False, writeTest=True)
    preprocessUnlabeled.main(test_filt,False,outname='rnn/unlalbeldReps_'+name+".p" )
    return "Success"


## Kicks off job to retrain model and label the corresping data
@app.route("/train", methods=['GET'])
def train():
    #return "S"
    name = request.args.get("name") or "default"
    mode = request.args.get("mode") or "Prod"
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./trainModel.sh "+mode+"_"+name+"_"
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    neuralFlags = { 'unlabled_mode':False, 'trainPath':'diagDictTrain_'+name+".p"}
    p.dump( neuralFlags, open('rnn/flags.p','wb'))
    shellScript1 = "cd rnn; rm -rf logsIndep_"+name + "; mkdir logsIndep_"+name
    shellScript2 = "./run.sh runIndep.py logsIndep_"+name
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    return "Success"

## Kicks off job to run model on the corresping data
## Will return all unlabeled data
@app.route("/predict", methods=['GET'])
def predict():
    #return p.load(open('returnedDB_'+name+'.p','w'))
    name = request.args.get("name") or "default"
    reportDB = predictHelper(name)
    #reportDB = p.load(open('validateDB_'+name+'.p','rb'))
    for r in reportDB:
        if 'MRN_Type' in r:
            r['Institution'] = r['MRN_Type']
    reportDB = aggregateEpisodes(reportDB)
    reportDB_Conv = exportToJSON.portToJSON(reportDB)
    reportDBJ = []
    reportDB_Eval = []
    reportDB_Pakis = []
    for r in reportDBJ:
        if 'test_set' in r and r['test_set']:
            reportDB_Eval.append(r)
        elif 'pakistani' in r and r['pakistani']:
            reportDB_Pakis.append(r)
        else:
            reportDBJ.append(r)
    print "len reportDB", len(reportDBJ)
    print "len test set", len(reportDB_Eval)
    print "len pakistani set", len(reportDB_Pakis)

    p.dump(reportDBJ, open('returnedDB_'+name+'.p','w'))
    p.dump(reportDB_Eval, open('evalDB_'+name+'.p','w'))
    p.dump(reportDBJ_Pakis, open('pakistaniDB_'+name+'.p','w'))

    updateAccesDB(copy.deepcopy(reportDBJ))
    getAtypias.main()
    evalModelRun.main()
    return json.dumps({'reportDB':reportDBJ})

################ Helpers ######################
def predictHelper(name):
    ## run boost predict
    mode = "Prod"
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./runModel.sh "+mode+"_"+name+"_"
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)

    ## aggregate boost predict
    stem = "classification_results/API/Prod_"+name+"_"
    db_unlabeled = p.load(open(DB_UNLABLED_PATH,'rb'))[name]
    reportDB = createEpisodes.aggregateResults(db_unlabeled, stem)
    print "Calling labelMaxDXBool"
    createEpisodes.getMaxDX(reportDB)
    print "Calling build episode"
    reportDBBoost, episodeDB = createEpisodes.buildEpisodes(reportDB, True)
    p.dump(reportDBBoost, open('boostDB_'+name+'.p','w'))
    #reportDBBoost = p.load(open('boostDB_'+name+'.p','r'))
    neuralFlags = { 'unlabled_mode':True, 'unlabeledPath':'unlalbeldReps_'+name+".p", 'outPath':'lableledReps_'+name+'.p'}

    p.dump( neuralFlags, open('rnn/flags.p','w'))
    assert p.load(open('rnn/flags.p','rb')) == neuralFlags
    shellScript1 = "cd rnn "
    shellScript2 = "./run.sh runIndep.py logsIndep_"+name
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    reportDBCNN = p.load( open('rnn/lableledReps_'+name+'.p','rb'))
    for r in reportDBCNN:
        if 'NN_Text' in r:
            del r['NN_Text']
    p.dump(reportDBCNN, open('cnnDB_'+name+'.p','wb'))
    #reportDBCNN = p.load(open('cnnDB_'+name+'.p','r'))
    reportDB = mergeDBs(reportDBBoost, reportDBCNN)
    corrections = p.load(open(DB_TRAIN_PATH,'rb'))[name]
    applyCorrections(reportDB, corrections)
    p.dump(reportDB, open("validateDB_"+name+".p","w"))
    print "num reps pre rules", len(reportDB)
    return reportDB

#sends all breast reports to the AccessDB
def updateAccesDB(reportDB):
    reportDB = postProcessRules(reportDB)
    reportDB = aggregateEpisodes(reportDB)
    #reportDB = exportToJSON.portToJSON(reportDB)

    reportDBJ = [r for r in reportDB if r['Organ']=='1']
    reportDBO = [r for r in reportDB if r['Organ'] == '0']
    print "Exporting", len(reportDBJ), "breast records"
    print "Exporting", len(reportDBO), "other records"

    db = MySQLdb.connect(host="localhost",user="root",passwd="nlpdb",db="reports")
    cur = db.cursor()
    dbKeys, placeholders = [k for k in accessDbKeys if k in reportDBJ[0]], ["%s" for i in accessDbKeys if i in reportDBJ[0] ]

    try:
        cur.execute("DROP TABLE "+backupTableName )
    except Exception, e:
        pass

    try:
        cur.execute("DROP TABLE "+ backupNoBreastTableName )
    except Exception, e:
        pass

    print "Moving breast reports to backup table..."
    cur.execute("CREATE TABLE "+backupTableName+" LIKE "+reportsTableName)
    cur.execute("INSERT INTO "+backupTableName+" SELECT * FROM "+reportsTableName)
    db.commit();
    cur.execute("TRUNCATE TABLE "+reportsTableName)
    db.commit();
    print "done."

    print "Exporting breast records..."
    sql = ("insert into "+reportsTableName+" ("+", ".join(dbKeys)+") VALUES ("+", ".join(placeholders)+")")
    print reportDBJ[0]
    for report in reportDBJ:
        try:
            values = [report[AccessDbToGregDict[k]] for k in dbKeys]
        except Exception , e:
            print e
            print report.keys(), "but looking for keys", [AccessDbToGregDict[k] for k in dbKeys]
            continue

        try:
            cur.execute(sql,tuple(values))
        except MySQLdb.Error, e:
             try:
                 print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                 print report
                 return None
             except IndexError:
                 print "MySQL Error: %s" % str(e)
                 print report
                 return None
        except TypeError, e:
            print("MySQL TypeError",e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError",e)
            print report
            return None
    db.commit()
    print "done."

    print "Moving non breast reports to backup table..."
    cur.execute("CREATE TABLE "+backupNoBreastTableName+" LIKE "+reportsNoBreastTableName)
    cur.execute("INSERT INTO "+backupNoBreastTableName+" SELECT * FROM "+reportsNoBreastTableName)
    db.commit();
    cur.execute("TRUNCATE TABLE "+backupNoBreastTableName)
    db.commit();
    print "done."

    print "Exporting non breast records..."
    sql = ("insert into "+ reportsNoBreastTableName +" ("+", ".join(dbKeys)+") VALUES ("+", ".join(placeholders)+")")
    #print reportDBO[0]
    for report in reportDBO:
        try:
            values = [report[AccessDbToGregDict[k]] for k in dbKeys]
        except Exception , e:
            print e
            print report.keys(), "but looking for keys", [AccessDbToGregDict[k] for k in dbKeys]
            continue

        try:
            cur.execute(sql,tuple(values))
        except MySQLdb.Error, e:
             try:
                 print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                 print report
                 return None
             except IndexError:
                 print "MySQL Error: %s" % str(e)
                 print report
                 return None
        except TypeError, e:
            print("MySQL TypeError",e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError",e)
            print report
            return None
    db.commit()
    print "done."
    cur.close()
    db.close()

    return "Success"

def validateTrainDb(trainDb):
    for r in trainDb:
        if not "Report_Text_Segmented" in r:
            print "Report_Text_Segmented not found in db!"
            return False
        #assert 'Report_Text_Segmented' in r #and 'ReportID' in r

        for d in diagnoses:
            if d in r and not r[d] in constantValidLabelDict[d]:
                print "Found ", r[d], "as value or diag", d, "but validLabels are only", constantValidLabelDict[d]

         #       assert r[d] in constantValidLabelDict[d]
	        return False
    return True

def preprocessText(text):
    cleanText = re.sub(r"\W", " ", text)
    cleanText = ' '.join(cleanText.split('\n'))
    cleanText = re.sub(r"(----)+", "", cleanText)
    cleanText = re.sub(r"(====)+", "", cleanText)
    cleanText = cleanText.lower()
    return cleanText

def mergeDBs(boost, cnn):
    mergeDB = []
    assert len(boost) == len(cnn)
    textToCNNDict = {}
    textToBoosDict = {}
    for c in cnn:
        textToCNNDict[c['Report_Text_Segmented']] = c
    for b in boost:
        b['Report_Text_Segmented'] = preprocessText( b['Report_Text_Segmented'])
        textToBoosDict[ b['Report_Text_Segmented']] = b
    assert len(textToCNNDict) == len(textToBoosDict)
    for k in textToBoosDict:
        cnnR = textToCNNDict[k]
        boostR = textToBoosDict[k]
        newR = {}
        for d in [k for k in boostexer_diagnoses if k in boostR]:
            newR[d] = boostR[d]
        for d in nn_diagnoses:
            newR[d] = cnnR[d]
        for k in [key for key in cnnR if not key in boostexer_diagnoses + nn_diagnoses ] :
            newR[k] = cnnR[k]
        mergeDB.append(newR)
    return mergeDB

def applyCorrections(test, gold):
    corrections = 0
    num_match  = 0
    textToLabel = {}
    for g in gold:
        textToLabel[ preprocessText(g['Report_Text_Segmented']) ] = g
    for t in test:
    	text = preprocessText(t['Report_Text_Segmented'])
        t['validated'] = text in textToLabel
        if text in textToLabel:
            for d in textToLabel[text]:
                if d in t  and d in diagnoses and not t[d] == textToLabel[text][d]:
                    corrections += 1
                t[d] = textToLabel[text][d]
                num_match+=1
    print("num corrected", corrections, num_match)
## Given a list of dicts, where  each dict represent a report:
## If the report text covers a single breast, we assign it an id and nothing happens
## If the report contains 2 breasts, automatically parse it into two reports, assign them
## both ids.
## @return: the preprocessed reports
def preprocessReports(reports):
    ## Can assume reports all ready preprocessed into left/right
    ## Some annotations per report
    ## gen boostexer files, and continue training. add to existing files
    for r in reports:
        assert 'Report_Text' in r

    results = preprocessRawDb.main(reports)
    return results





## Runs enforces global constraints like ER/PR NA given no cancer
def postProcessRules(db_train):
    print(db_train[0].keys())

    for r in db_train:
        if hasCat(r, const_cancers_mod):
            r['cancer'] = 'Present'
        else:
            r['cancer'] = "Absent"
        if hasCat(r, const_atypias_mod):
            r['atypia'] = 'Present'
        else:
            r['atypia'] = "Absent"

        if r['cancer'] == 'Absent':
            for k in ['ER','PR','Her2 (Fish)', 'ECE', 'LVI','BVI', 'Are there positive LN?', 'ITC ']:
                r[k] = 'NA'

        for k in r.keys():
            if type(r[k]) is unicode:
                r[k] = str(r[k])
            if r[k] in ["Present", "Yes", "Positive", "Anatomic", "breast"]:
                r[k] = "1"
            if r[k] in ["Absent", "No", "Negative", "Cytology", "non-breast"]:
                r[k] = "0"
            if r[k] == "NA":
                r[k] = "9"
            if r[k] == "RIGHT":
                r[k] = 'r'
            if r[k] == "LEFT":
                r[k] = "l"
            #TODO change these to ints and reconfigure the db

    return db_train#[d for d in db_train if d['Organ'] == 'breast']

def aggregateEpisodes(data):
    data  = preprocessRawDb.unicodeToDatetime(data)
    # label episode ids for data
    mrns = {}
    sideKey = "Red BreastSide" if "Red BreastSide" in data[0] else "BreastSide"
    assert sideKey in data[0]
    for i in range(len(data)):
        if not sideKey in data[i]:
            print data[i]
	    raw_input('sidekey is '+sideKey)
        if not data[i]['MRN'] in mrns:
            mrns[data[i]['MRN']] = {}
        if not data[i][sideKey] in mrns[data[i]['MRN']]:
            mrns[data[i]['MRN']][data[i][sideKey]] = [data[i]]
        else:
            mrns[data[i]['MRN']][data[i][sideKey]].append(data[i])

    #Structure : List of Reports with Episode IDs
    reportsDB = []
    episodeDateDict = {} ## Use this to store Date -> episode Id for each MRN. use this to reorder episodes by date
    episodeRelabelDict = {} ## Use this to store episoideID to new Episode ID
    for mrn in mrns:
        patient = mrns[mrn]
        episodeId = -1
        episodeDateDict[mrn] = []
        for side in patient:
            patient[side] = sorted( patient[side], key=itemgetter('Report_Date_TimePlusX') )
            for idx, rep in enumerate(patient[side]):

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

                reportsDB.append(rep)


    ## Relabel MRNs with chronological episode numbers (first was chronological per breast)
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
        newID = episodeRelabelDict[rep['MRN']][oldID]
        rep['EpisodeID'] = newID
        assert isinstance(rep['EpisodeID'] , int)

    return reportsDB

## Call this to start appex
if __name__ == "__main__":
    print "Begin API"
    app.run(host="0.0.0.0")
    db_train.close()
