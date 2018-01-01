from operator import itemgetter
from flask import Flask
from flask import render_template
from flask import request
from datetime import date, datetime
import numpy as np
import cPickle as p
import MySQLdb
import xlsxwriter
import subprocess
import sys, os
import json
import copy
import re
from random import shuffle
from constants import *
sys.path.append("/home/nlp/pathology/")
sys.path.append("/home/nlp/pathology/rnn")
import createEpisodes
import preprocessTrain
import preprocessUnlabeled
import exportToJSON
import generateClassifierFilesForProd
import preprocessRawDb
import getAtypias
import evalModelRun


app = Flask(__name__)
app.config.from_object(__name__)
CURR_PATH = "/home/nlp/pathology/"
DB_TRAIN_PATH = CURR_PATH + "reportDBAPI_train.p"
# DB_TRAIN_PATH = CURR_PATH + "reportDBAPI_train_small.p"
DB_UNLABLED_PATH = CURR_PATH + "reportDBAPI_test.p"
# DB_UNLABLED_PATH = CURR_PATH + "reportDBAPI_test_small.p"


# Handle relevant initialization of files

rawPath = CURR_PATH + "reportDB+red+clean.p"
additPath = CURR_PATH + "additionalTrainRepsMar10.p"
raws = p.load(open(rawPath, 'rb')) + p.load(open(additPath, 'rb'))


def hasCat(r, cat, loose=False):
    for c in cat:
        if not loose:
            if r[c] == '1':
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
    db_train = p.load(open(DB_TRAIN_PATH, 'rb'))
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
except Exception, e:
    # Data doesn't exist so init base and preprocess neural min
    print "Init db_train"
    db_train = {'default': base}
    db_unlabeled = {'default': base[ :10]}
    neuralTrain = preprocessTrain.main(base)
    p.dump(neuralTrain, open(CURR_PATH + 'rnn/diagDictTrain.p', 'wb'))
    p.dump(db_train, open(DB_TRAIN_PATH, 'wb'))
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))


RequiredPreprocessFields = ['Report_Text', "Report_Date_TimePlusX"]
RequiredTrainDbFields = ['ReportID', 'Report_Text_Segmented']

global boost_diags1, boost_diags2, boost_diags3, boost_diags4, boost_diags5, boost_diags6
boost_diags = [replaceSpaces(l) for l in boostexer_diagnoses]
inds = [0, (len(boost_diags)/6), (len(boost_diags)/3), (len(boost_diags)/2), (2*len(boost_diags)/3), (5*len(boost_diags)/6), len(boost_diags)]
boost_diags1 = (".".join(boost_diags[inds[0]:inds[1]]))
boost_diags2 = (".".join(boost_diags[inds[1]:inds[2]]))
boost_diags3 = (".".join(boost_diags[inds[2]:inds[3]]))
boost_diags4 = (".".join(boost_diags[inds[3]:inds[4]]))
boost_diags5 = (".".join(boost_diags[inds[4]:inds[5]]))
boost_diags6 = (".".join(boost_diags[inds[5]:inds[6]]))


# Given a JSON list of dicts, where  each dict represent a report:
# Parse the dict for daignoses, and add annotations if found
# @name specifies user, izzy don't worry about this
# @raw specifies if the data has been preprocessed before,
# Example:
# [ {Report_Text: }]
# @return: 0
@app.route("/addTrain", methods=['POST'])
def addTrainData():
    db_train = p.load(open(DB_TRAIN_PATH, 'rb'))
    data = json.loads(request.data) or []
    name = request.args.get("name") or "default"
    # return "S"
    if len(data) > 0:
        print "data has keys", data[0].keys()
    print "len data is", len(data)
    print "name is", name

    if not validateTrainDb(data):
        data = preprocessReports(data)

    if name not in db_train:
        print "Adding", name, "to db_train"
        db_train[name] = base
    
    # mark the files to note as annoations
    trainTexts = [r['Report_Text_Segmented'] for r in db_train[name] if 'Report_Text_Segmented' in r]
    #trainTexts = []
    trainKeys = []
    for r in db_train[name]:
        for k in r:
            if k not in trainKeys:
                trainKeys.append(k)

    newData = []
    newDevReps = []
    for r in data:
        if r['Report_Text_Segmented'] not in trainTexts:
            r['Owner'] = name
            for d in diagnoses:
                if d in r:
                    r['TaghianGold'] = 1
            
        newKeys = [key for key in diagnoses if key not in trainKeys and key in r]
        #print(newKeys)
        if len(newKeys) > 0:
            newDevReps.append(r)
            #print(newKeys)
        else:
            newData.append(r)

    #print newDevReps
    if len(newDevReps) > 0:
        shuffle(newDevReps)
        # 40% devReps, 20% gold set, 40% normal train
        partInds = [int(len(newDevReps)*0.2), int(len(newDevReps)*0.2), int(len(newDevReps)*0.6)]
        #add different values to rnn dev reps until it reaches 40% of new data
        evalReps = []
        keyPool = {}
        for k in diagnoses:
            valPool = {}
            for v in diagnoses[k]:
                pool = [r for r in newDevReps if k in r and r[k] == v]
                valPool[v] = pool
            keyPool[k] = valPool
        while len(evalReps) < partInds[0]:
            for k in keyPool:
                for v in keyPool[k]:
                    if len(keyPool[k][v]) == 0:
                        continue
                    else:
                        for i in range(len(keyPool[k][v])-1, -1, -1):
                            if keyPool[k][v][i] in evalReps:
                                keyPool[k][v].pop(i)
                            else:
                                evalReps.append(keyPool[k][v][i])
                                newDevReps.remove(keyPool[k][v][i])
                                keyPool[k][v].pop(i)
                                break
        vocabIndxDict = p.load(open('rnn/vocabIndxDict.p', 'rb'))
        for r in evalReps:
            for k in r:
                if k in diagnoses:
                    temp = r[k]
                    r[k] = np.zeros(len(diagnoses[k]))
                    r[k][diagnoses[k].index(temp)] = 1.
            sent = r['Report_Text_Segmented']
            words = sent.split(" ")
            indices = [vocabIndxDict[w] for w in words if w in vocabIndxDict]
            r['NN_Text'] = np.array(indices)
        devReps = p.load(open(PATHOLOGYDIR + 'rnn/devReps.p'))
        devReps.extend(evalReps)
        p.dump(devReps, open(PATHOLOGYDIR + 'rnn/devReps.p', 'wb'))

        # # make gold set from 20%
        # newGold = newDevReps[ :partInds[1]]
        # dbKeys = [k for k in columnKeys if k in newGold[0]]

        # outputFile = EVALDIR + "".join(newKeys)+'DB.xlsx'
        # workbook = xlsxwriter.Workbook(outputFile)
        # worksheet = workbook.add_worksheet()

        # row = 0
        # for key in dbKeys:
        #     col = dbKeys.index(key)
        #     worksheet.write(row, col, key)
        # row = 1
        # for r in newGold:
        #     for k in r:
        #         try:
        #             col = dbKeys.index(k)
        #             worksheet.write(row, col, r[k])
        #         except ValueError:
        #             pass
        #     row += 1

        # workbook.close()

        # rest goes to normal training
        #newData.extend(newDevReps[partInds[1]: ])
        newData.extend(newDevReps)

    db_train[name].extend(newData)
    print "Len train", len(db_train[name])
    p.dump(db_train, open(DB_TRAIN_PATH, 'wb'))
    print db_train.keys()
    return "Success"


# Given a JSON list of dicts, where  each dict represent a report:
# Parse the dict for daignoses, and add annotations if found
# @name specifies user, izzy don't worry about this
# @raw specifies if the data has been preprocessed before,
# Example:
# [{Report_Text: }]
# @return: 0
@app.route("/addUnlabeled", methods=['POST'])
def addUnlabeledData():
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
    data = json.loads(request.data) or []
    name = request.args.get("name") or "default"
    raw = request.args.get("raw") or False
    # return "S"
    print "name is", name
    # Preprocess bilaterals if need be
    if raw:
        data = preprocessReports(data)

    validateTrainDb(data)

    if name not in db_unlabeled:
        print "Adding", name, "to db_unlabeled"
        db_unlabeled[name] = []
    # mark the files to note as annoations
    unlabeledTexts = [r['Report_Text_Segmented'] for r in db_unlabeled[name] if 'Report_Text_Segmented' in r]
    #unlabeledTexts = []
    newData = []
    for r in data:
        r['Report_Text_Segmented'] = preprocessText(r['Report_Text_Segmented'])
        if r['Report_Text_Segmented'] not in unlabeledTexts:
            r['Owner'] = name
            for d in diagnoses:
                if d in r:
                    r['TaghianGold'] = 1
            newData.append(r)

    db_unlabeled[name].extend(newData)
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
    print db_unlabeled.keys()
    return "Success"


# Does all necessary preprocessing on the training set for a given user
# Return 0
@app.route("/updateTrainSet", methods=['GET'])
def updateTrainSet():
    # return "S"
    db_train = p.load(open(DB_TRAIN_PATH, 'rb'))
    name = request.args.get("name") or "default"
            
    # Generate relevant files in some directory with a name path
    trainDb = db_train[name]
    #stem = "boostexer/breast/api/"+"Prod"+"_"+name+"_"
    trainDb = db_train[name] + db_train['default']
    #generateClassifierFilesForProd.binarizeFilesForClassification(trainDb, stem, writeTrain=True, writeTest=False)
    preprocessTrain.main(trainDb)

    diagDictNew = preprocessTrain.main(trainDb)
    p.dump(diagDictNew, open('rnn/diagDictTrain_'+name+".p", 'wb'))
    return "Success"


# Does all necessary preprocessing for test data given a batch_id in the unlabled data
# Script will prepare neural model and boosting model to evaluate on all reps where r['batch_id'] is in
# the list of id's specified. If batch_id's is ommited, this will run across all unlabled data which may be very expensive.
# Return 0
@app.route("/updateUnlabeledSet", methods=['GET'])
def updateUnlabeledSet():
    # return "S"
    db_test_all = p.load(open(DB_UNLABLED_PATH, 'rb'))
    name = request.args.get("name") or "default"
    batch_id = request.args.get("batch_id") or "none"
    db_test = db_test_all[name]
    test_filt = db_test if batch_id == "none" else [d for d in db_test if "batch_id" in d and d["batch_id"] in batch_id]
    # Generate relevant files in some directory with a name path
    #stem = "boostexer/breast/api/"+"Prod"+"_"+name+"_"
    #generateClassifierFilesForProd.binarizeFilesForClassification(test_filt, stem, writeTrain=False, writeTest=True)
    preprocessUnlabeled.main(test_filt, False, outname='rnn/unlalbeldReps_'+name+".p")
    return "Success"


# Kicks off job to retrain model and label the corresping data
@app.route("/train", methods=['GET'])
def train():
    # return "S"
    name = request.args.get("name") or "default"
    mode = request.args.get("mode") or "Prod"
    #shellScript1 = "cd boostexer/breast/api/"
    #shellScript2 = "./trainModel.sh "+mode+"_"+name+"_ "+boost_diags1+" "+boost_diags2+" "+boost_diags3+" "+boost_diags4+" "+boost_diags5+" "+boost_diags6
    #subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    neuralFlags = {'unlabled_mode': False, 'trainPath': 'diagDictTrain_'+name+".p"}
    p.dump(neuralFlags, open('rnn/flags.p', 'wb'))
    shellScript1 = "cd rnn; rm -rf logsIndep_"+name + "; mkdir logsIndep_"+name
    shellScript2 = "./run.sh runIndep.py logsIndep_"+name
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    return "Success"


# Kicks off job to run model on the corresping data
# Will return all unlabeled data
@app.route("/predict", methods=['GET'])
def predict():
    name = request.args.get("name") or "default"
    if request.args.get("debug") == "True":
        reportDB = p.load(open('validateDB_'+name+'.p', 'rb'))
    else:
        reportDB = predictHelper(name)

    for r in reportDB:
        if 'MRN_Type' in r:
            r['Institution'] = r['MRN_Type']
    reportDB = aggregateEpisodes(reportDB)
    reportDB = exportToJSON.portToJSON(reportDB)
    print "len reportDB", len(reportDB)
    p.dump(reportDB, open('validateDB_'+name+'.p', 'w'))

    reportDB = updateAccesDB(copy.deepcopy(reportDB))
    p.dump(reportDB, open('returnedDB_'+name+'.p', 'w'))
    getAtypias.main()
    evalModelRun.main()
    # pruneNonBreast(reportDB, name)
    for r in reportDB:
        for k in r:
            if isinstance(r[k], (datetime.datetime, datetime.date)):
                r[k] = r[k].isoformat()
            if isinstance(r[k], np.ndarray):
                r[k] = ""
    return json.dumps({'reportDB': reportDB})


################ Helpers ######################
def pruneNonBreast(reportDB, name):
    print("Loading db_unlabeled...")
    # reportDB = p.load(open('/home/nlp/pathology/validateDB_'+name+'.p'))
    nonbreast_path = '/home/nlp/pathology/reportDBAPI_nonbreasts.p'
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
    print("Finding non-breast reports...")
    
    if os.path.exists(nonbreast_path):
        nonbreasts_unlabeled = p.load(open(nonbreast_path, 'rb'))
    else:
        nonbreasts_unlabeled = {name: []}

    count = 0
    for r in reportDB:
        if r['Organ'].lower() != '1':
            matchingReports = [i for i in range(len(db_unlabeled[name])) if db_unlabeled[name][i]['Report_Text_Segmented'] == r['Report_Text_Segmented']]
            # print(matchingReports, r['Organ'])
            count += len(matchingReports)
            for j in reversed(matchingReports):
                nonbreasts_unlabeled[name].append(db_unlabeled[name].pop(j))

    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
    p.dump(nonbreasts_unlabeled, open(nonbreast_path, 'wb'))
    print("Moved "+str(count)+" non-breast reports to "+nonbreast_path+"!")


def pruneEvals(name):
    print("Loading db_unlabeled...")
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
    print("Finding gold reports...")
    count = 0
    for r in reversed(db_unlabeled[name]):
        if 'filename' in r and r['filename'] in os.listdir(EVALDIR):
            db_unlabeled[name].remove(r)
            count += 1
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
    print("Deleted "+str(count)+" gold reports!")


def predictHelper(name):
    # run boost predict
    mode = "Prod"
    neuralFlags = {'unlabled_mode': True, 'unlabeledPath': 'unlalbeldReps_'+name+".p", 'outPath': 'lableledReps_'+name+'.p'}

    p.dump(neuralFlags, open('rnn/flags.p', 'w'))
    assert p.load(open('rnn/flags.p', 'rb')) == neuralFlags
    shellScript1 = "cd rnn "
    shellScript2 = "./run.sh runIndep.py logsIndep_"+name
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    reportDBCNN = p.load(open('rnn/lableledReps_'+name+'.p', 'rb'))
    for r in reportDBCNN:
        if 'NN_Text' in r:
            del r['NN_Text']
    p.dump(reportDBCNN, open('cnnDB_'+name+'.p', 'wb'))
    # reportDBCNN = p.load(open('cnnDB_'+name+'.p', 'r'))
    reportDB = reportDBCNN #mergeDBs(reportDBBoost, reportDBCNN)
    corrections = p.load(open(DB_TRAIN_PATH, 'rb'))[name]
    applyCorrections(reportDB, corrections)
    p.dump(reportDB, open("validateDB_"+name+".p", "w"))
    print "num reps pre rules", len(reportDB)
    return reportDB


# sends all breast reports to the AccessDB
def updateAccesDB(reportDB):
    reportDB = postProcessRules(reportDB)
    reportDB = aggregateEpisodes(reportDB)
    # reportDB = exportToJSON.portToJSON(reportDB)
    reportDB_nongold = [r for r in reportDB if ('filename' not in r or r['filename'] not in os.listdir(EVALDIR))]
    reportDBJ = [r for r in reportDB_nongold if r['Organ'] == '1']
    reportDBO = [r for r in reportDB_nongold if r['Organ'] == '0']
    print "Exporting", len(reportDBJ), "breast records"
    print "Exporting", len(reportDBO), "other records"

    p.dump(reportDBJ, open('/home/nlp/pathology/reportDB_access.p', 'wb'))

    db = MySQLdb.connect(host="localhost", user="root", passwd="nlpdb", db="reports")
    cur = db.cursor()
    dbKeys, placeholders = [k for k in columnKeys if k in reportDBJ[0]], ["%s" for i in columnKeys if i in reportDBJ[0]]

    try:
        cur.execute("DROP TABLE " + backupTableName)
    except Exception as e:
        print str(e)
        pass

    try:
        cur.execute("DROP TABLE " + backupNoBreastTableName )
    except Exception, e:
        print str(e)
        pass

    print "Moving breast reports to backup table..."
    cur.execute("CREATE TABLE " + backupTableName + " LIKE " + reportsTableName)
    cur.execute("INSERT INTO " + backupTableName + " SELECT * FROM " + reportsTableName)
    db.commit()
    cur.execute("DROP TABLE " + reportsTableName)
    cur.execute("CREATE TABLE " + reportsTableName + " (" + " TEXT, ".join(dbKeys) + " TEXT)")
    db.commit()
    print "done."

    print "Exporting breast records..."
    sql = ("INSERT INTO " + reportsTableName + " (" + ", ".join(dbKeys) + ") VALUES (" + ", ".join(placeholders) + ")")
    for report in reportDBJ:
        try:
            values = [report[k] for k in dbKeys]
        except Exception, e:
            print e
            print report.keys(), "but looking for keys", [k for k in dbKeys]
            continue

        try:
            cur.execute(sql, tuple(values))
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
            print("MySQL TypeError", e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError", e)
            print report
            return None
    db.commit()
    print "done."

    print "Moving non breast reports to backup table..."
    cur.execute("CREATE TABLE " + backupNoBreastTableName + " LIKE " + reportsNoBreastTableName)
    cur.execute("INSERT INTO " + backupNoBreastTableName + " SELECT * FROM " + reportsNoBreastTableName)
    db.commit()
    cur.execute("DROP TABLE " + reportsNoBreastTableName)
    cur.execute("CREATE TABLE " + reportsNoBreastTableName + " (" + " TEXT, ".join(dbKeys) + " TEXT)")
    db.commit()
    print "done."

    print "Exporting non breast records..."
    sql = ("insert into " + reportsNoBreastTableName + " (" + ", ".join(dbKeys) + ") VALUES (" + ", ".join(placeholders) + ")")
    # print reportDBO[0]
    for report in reportDBO:
        try:
            values = [report[k] for k in dbKeys]
        except Exception, e:
            print e
            print report.keys(), "but looking for keys", [k for k in dbKeys]
            continue

        try:
            cur.execute(sql, tuple(values))
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
            print("MySQL TypeError", e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError", e)
            print report
            return None
    db.commit()
    print "done."
    cur.close()
    db.close()

    return reportDB


def validateTrainDb(trainDb):
    for r in trainDb:
        if "Report_Text_Segmented" not in r:
            print "Report_Text_Segmented not found in db!"
            return False

        for d in diagnoses:
            if d in r and not r[d] in diagnoses[d]:
                print "Found "+str(r[d])+" as value for diag "+str(d)+" but valid labels are only", diagnoses[d]
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
    # assert len(boost) == len(cnn)
    textToCNNDict = {}
    textToBoosDict = {}
    for c in cnn:
        textToCNNDict[c['Report_Text_Segmented']] = c
    for b in boost:
        b['Report_Text_Segmented'] = preprocessText(b['Report_Text_Segmented'])
        textToBoosDict[b['Report_Text_Segmented']] = b
    # assert len(textToCNNDict) == len(textToBoosDict)
    for k in textToBoosDict:
        if k not in textToCNNDict:
            continue
        cnnR = textToCNNDict[k]
        boostR = textToBoosDict[k]
        newR = {}
        for d in [k for k in boostexer_diagnoses if k in boostR]:
            newR[d] = boostR[d]
        for d in nn_diagnoses:
            if d in cnnR:
                newR[d] = cnnR[d]
            else:
                newR[d] = ""
        for k in [key for key in cnnR if key not in boostexer_diagnoses + nn_diagnoses]:
            newR[k] = cnnR[k]
        for k in [key for key in boostR if key not in newR]:
            newR[k] = boostR[k]
        mergeDB.append(newR)
    return mergeDB


def applyCorrections(test, gold):
    corrections = 0
    num_match = 0
    textToLabel = {}
    for g in gold:
        textToLabel[preprocessText(g['Report_Text_Segmented'])] = g
    for t in test:
        text = preprocessText(t['Report_Text_Segmented'])
        t['validated'] = text in textToLabel
        if text in textToLabel:
            t['train'] = 1
            for d in textToLabel[text]:
                if d in diagnoses:
                    if d in t and t[d] != textToLabel[text][d]:
                        corrections += 1
                    t[d] = textToLabel[text][d]
                    num_match += 1
    print("num corrected", corrections, num_match)


# Given a list of dicts, where  each dict represent a report:
# If the report text covers a single breast, we assign it an id and nothing happens
# If the report contains 2 breasts, automatically parse it into two reports, assign them
# both ids.
# @return: the preprocessed reports
def preprocessReports(reports):
    # Can assume reports all ready preprocessed into left/right
    # Some annotations per report
    # gen boostexer files, and continue training. add to existing files
    for r in reversed(reports):
        if 'Report_Text' in r and 'Report_Text_Segmented' in r:
            pass
        elif 'Report_Text' not in r and 'Report_Text_Segmented' in r:
            r['Report_Text'] = r['Report_Text_Segmented']
        elif 'Report_Text_Segmented' not in r and 'Report_Text' in r:
            r['Report_Text_Segmented'] = r['Report_Text']
        else:
            print ("report only has keys", r.keys())
            reports.remove(r)
        r['Report_Text'].replace("_x000D_", "\n")
        r['Report_Text_Segmented'].replace("_x000D_", "\n")
        r['Report_Text_Segmented'].replace("_x000d_", "\n")
        

    # assert 'Report_Text' in r or 'Report_Text_Segmented' in r

    results = preprocessRawDb.main(reports)
    return results


# Runs enforces global constraints like ER/PR NA given no cancer
def postProcessRules(db_train):
    print(db_train[0].keys())

    for r in db_train:
        if "filename" not in r:
            r['filename'] = "Unknown"

        if hasCat(r, const_cancers):
            r['cancer'] = '1'
        else:
            r['cancer'] = '0'
        if hasCat(r, const_atypias):
            r['atypia'] = '1'
        else:
            r['atypia'] = '0'

        if r['cancer'] == '0':
            for k in ['ER', 'PR', 'Her2Fish', 'ECE', 'LVI', 'BVI', 'PositiveLN', 'ITC']:
                r[k] = '9'

        if 'Her2Fish' in r and r['Her2Fish'] != '9':
            r['her2'] = r['Her2Fish']
        else:
            if 'Her2_IHC' not in r or r['Her2_IHC'] == '9':
                r['her2'] = '9'
            elif r['Her2_IHC'] == '3':
                r['her2'] = '1'
            elif r['Her2_IHC'] in ['0', '1', '2']:
                r['her2'] = '0'

        for k in r.keys():
            if type(r[k]) is unicode:
                r[k] = r[k].encode('utf-8')
            
    return db_train


def aggregateEpisodes(data):
    data = preprocessRawDb.unicodeToDatetime(data)
    # label episode ids for data
    mrns = {}
    sideKey = "BreastSide"
    assert sideKey in data[0]
    for i in range(len(data)):
        if sideKey not in data[i]:
            print data[i]
            #raw_input('sidekey is ' + sideKey)
        if 'MRN' not in data[i] and 'MRNPlusX' in data[i]:
            data[i]['MRN'] = data[i]['MRNPlusX']
        try:
            if not data[i]['MRN'] in mrns:
                mrns[data[i]['MRN']] = {}
            if not data[i][sideKey] in mrns[data[i]['MRN']]:
                mrns[data[i]['MRN']][data[i][sideKey]] = [data[i]]
            else:
                mrns[data[i]['MRN']][data[i][sideKey]].append(data[i])
        except Exception, e:
            continue
            # print "exception e", e, "with keys", data[i].keys()
            # print "data[i]", data[i]
    # Structure: List of Reports with Episode IDs
    reportsDB = []
    episodeDateDict = {}  # Use this to store Date -> episode Id for each MRN. use this to reorder episodes by date
    episodeRelabelDict = {}  # Use this to store episoideID to new Episode ID
    for mrn in mrns:
        patient = mrns[mrn]
        episodeId = -1
        episodeDateDict[mrn] = []
        for side in patient:
            for r in patient[side]:
                if r['Report_Date_TimePlusX'] == 0:
                    r['Report_Date_TimePlusX'] = datetime(1900, 1, 1)
            patient[side] = sorted(patient[side], key=itemgetter('Report_Date_TimePlusX'))
            for idx, rep in enumerate(patient[side]):

                if idx == 0:
                    episodeId += 1
                    rep['EpisodeID'] = 't'+str(episodeId)
                    episodeDateDict[mrn].append({'EpStartTime': rep['Report_Date_TimePlusX'], 'epID': 't'+str(episodeId)})
                else:
                    prevVisit = patient[side][idx - 1]
                    if rep['Report_Date_TimePlusX'] - prevVisit['Report_Date_TimePlusX'] < SIX_MONTHS:
                        rep['EpisodeID'] = prevVisit['EpisodeID']
                    else:
                        episodeId += 1
                        rep['EpisodeID'] = 't'+str(episodeId)
                        episodeDateDict[mrn].append({'EpStartTime': rep['Report_Date_TimePlusX'], 'epID': 't'+str(episodeId)})

                reportsDB.append(rep)


    # Relabel MRNs with chronological episode numbers (first was chronological per breast)
    for mrn in mrns:
        patient = mrns[mrn]
        episodeRelabelDict[mrn] = {}
        epDates = sorted(episodeDateDict[mrn], key=itemgetter('EpStartTime'))
        for indx, dateDict in enumerate(epDates):
            epID = dateDict['epID']
            episodeRelabelDict[mrn][epID] = indx

        assert len(episodeDateDict[mrn]) == len(epDates)
    assert len(episodeRelabelDict) == len(mrns)

    for rep in reportsDB:
        oldID = rep['EpisodeID']
        newID = episodeRelabelDict[rep['MRN']][oldID]
        rep['EpisodeID'] = newID
        assert isinstance(rep['EpisodeID'], int)

    return reportsDB


# Call this to start appex
if __name__ == "__main__":
    print "Begin API"
    app.run(host="0.0.0.0")
    db_train.close()
