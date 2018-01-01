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
    # trainTexts = [r['Report_Text_Segmented'] for r in db_train[name] if 'Report_Text_Segmented' in r]
    trainTexts = []
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

        newKeys = [key for key in r if key not in trainKeys and key in post_diagnoses]
        if len(newKeys) > 0:
            newDevReps.append(r)
        else:
            newData.append(r)

    if len(newDevReps) > 0:
        # 40% goes to normal training
        newData.extend(newDevReps[int(len(newDevReps)*0.4): ])

        # make gold set from 20%
        newGold = newDevReps[int(len(newDevReps)*0.2):int(len(newDevReps)*0.4)]
        dbKeys = [k for k in columnKeys if k in newGold[0]]

        outputFile = EVALDIR + "".join(newKeys)+'DB.xlsx'
        workbook = xlsxwriter.Workbook(outputFile)
        worksheet = workbook.add_worksheet()

        row = 0
        for key in dbKeys:
            col = dbKeys.index(key)
            worksheet.write(row, col, key)
        row = 1
        for r in newGold:
            for k in r:
                try:
                    col = dbKeys.index(k)
                    worksheet.write(row, col, r[k])
                except ValueError:
                    pass
            row += 1

        workbook.close()

        # with open(outputFile, 'wb') as output_file:
        #     dict_writer = csv.DictWriter(output_file, dbKeys, extrasaction='ignore')
        #     dict_writer.writeheader()
        #     dict_writer.writerows(newGold)

        # rest is processed and added to rnn/devReps.p
        vocabIndxDict = p.load(open('rnn/vocabIndxDict.p', 'rb'))
        for r in newDevReps[ :int(len(newDevReps)*0.2)]:
            for k in r:
                if k in post_diagnoses:
                    temp = r[k]
                    r[k] = np.zeros(len(post_diagnoses[k]))
                    r[k][post_diagnoses[k].index(temp)] = 1.
            sent = r['Report_Text_Segmented']
            words = sent.split(" ")
            indices = [vocabIndxDict[w] for w in words if w in vocabIndxDict]
            r['NN_Text'] = np.array(indices)
        devReps = p.load(open(PATHOLOGYDIR + 'rnn/devReps.p'))
        devReps.extend(newDevReps[ :int(len(newDevReps)*0.2)])
        p.dump(devReps, open(PATHOLOGYDIR + 'rnn/devReps.p', 'wb'))

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




# Kicks off job to retrain model and label the corresping data
@app.route("/train", methods=['GET'])
def train():
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
    p.dump(reportDB, open('returnedDB_'+name+'.p', 'w'))

    updateAccesDB(copy.deepcopy(reportDB))
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


def predictHelper(name):
    # run boost predict
    mode = "Prod"
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./runModel.sh "+mode+"_"+name+"_ "+boost_diags1+" "+boost_diags2+" "+boost_diags3+" "+boost_diags4+" "+boost_diags5+" "+boost_diags6
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)

    # aggregate boost predict
    stem = "classification_results/API/Prod_"+name+"_"
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))[name]
    reportDBBoost = createEpisodes.aggregateResults(db_unlabeled, stem, export_as_list=True)
    p.dump(reportDBBoost, open('boostDB_'+name+'.p', 'w'))
    # reportDBBoost = p.load(open('boostDB_'+name+'.p', 'r'))
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
    reportDB = mergeDBs(reportDBBoost, reportDBCNN)
    corrections = p.load(open(DB_TRAIN_PATH, 'rb'))[name]
    applyCorrections(reportDB, corrections)
    p.dump(reportDB, open("validateDB_"+name+".p", "w"))
    print "num reps pre rules", len(reportDB)
    return reportDB


if __name__ == "__main__":
    print "Begin API"
    app.run(host="0.0.0.0")
    db_train.close()
