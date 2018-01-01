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
logger = logger.get_logger(LOGNAME, LOGPATH)


CURR_PATH = "/home/nlp/pathology/"
DB_TRAIN_PATH = CURR_PATH + "reportDBAPI_train.p"
# DB_TRAIN_PATH = CURR_PATH + "reportDBAPI_train_small.p"
DB_UNLABLED_PATH = CURR_PATH + "reportDBAPI_test.p"
# DB_UNLABLED_PATH = CURR_PATH + "reportDBAPI_test_small.p"


# Handle relevant initialization of files

RequiredPreprocessFields = ['Report_Text', "Report_Date_TimePlusX"]
RequiredTrainDbFields = ['ReportID', 'Report_Text_Segmented']



@app.route("/addReports", methods=['POST'])
def addTrainData():
    '''
    TODO: implement initdb, preprocess reports, contains annotations, etc.
    '''
    data = json.loads(request.data) or []
    name = request.args.get("name") or "default"
    # return "S"
    if len(data) > 0:
        logger.info( "addTrain - data has keys {}".format( data[0].keys()))
    logger.info("addTrain - [{}] len data {}".format(name, len(data)))

    data = preprocessReports(data)

    if not contains_annotations(data):
        logger.warning("addTrain - did not include any reports with labels. No op.")
        return 200

    db_train = pickle.load(open(DB_TRAIN_PATH, 'rb'))

    if name not in db_train:
        logger.info("Adding {} to db_train".format(name))
        db_train[name] = init_db(config, logger)

    db_train[name].extend(newData)

    logger.info("addTrain - Len train {}".format(len(db_train[name])))
    pickle.dump(db_train, open(DB_TRAIN_PATH, 'wb'))
    return "addTrain success", 200



@app.route("/addUnlabeled", methods=['POST'])
def addUnlabeledData():
    '''
    '''
    data = json.loads(request.data) or []

    if len(data) == 0:
        logger.warning("addUnlabeled - did not include any reports. No op.")
        return 200

    name = request.args.get("name") or "default"
    data = preprocessReports(data)
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))

    if name not in db_unlabeled:
        logger.info( "addUnlabeled - Adding {} to db_unlabeled".format(name))
        db_unlabeled[name] = []

    db_unlabeled[name].extend(data)
    logger.info( "addUnlabeled - Adding {} reports to db_unlabeled".format(len(data)))
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
    return 200





@app.route("/train", methods=['GET'])
def train():
    '''
    '''
    name = request.args.get("name") or "default"
    rationale_net_wrapper.train(name, config, logger)
    return 200


# Kicks off job to run model on the corresping data
# Will return all unlabeled data
@app.route("/predict", methods=['GET'])
def predict():
    name = request.args.get("name") or "default"
    if request.args.get("debug") == "True":
        reportDB = p.load(open('validateDB_'+name+'.p', 'rb'))
    else:
        reportDB = rationale_net_wrapper.label_reports(name, config, logger)

    reportDB = aggregateEpisodes(reportDB)
    reportDB = exportToJSON.portToJSON(reportDB)

    p.dump(reportDB, open('returnedDB_'+name+'.p', 'w'))

    run_exports(reportDB)
    # pruneNonBreast(reportDB, name)
    return json.dumps({'reportDB': reportDB})

def run_exports(reportDB):
    updateAccesDB(copy.deepcopy(reportDB))
    getAtypias.
    evalModelRun.main()


if __name__ == "__main__":
    print "Begin API"
    app.run(host="0.0.0.0")
