import cPickle as p
from constants import *
import sys
sys.path.append("buildNewDataset")
sys.path.append("trainClassifier")
sys.path.append("preprocessDataset")
sys.path.append("analysis")
sys.path.append("rnn")
import createEpisodes
import preprocessTrain
import preprocessUnlabeled
import exportToJSON
import generateClassifierFilesForProd
import generateClassifierFilesForDev
import preprocessRawDb
import interpretResults
from operator import itemgetter
import subprocess
from flask import Flask
from flask import render_template
from flask import request
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(__name__)
DB_TRAIN_PATH = "reportDBAPI_train.p" 
DB_UNLABLED_PATH = "reportDBAPI_test.p" 



## Handle relevant initialization of files

rawPath = "reportDB+red+clean.p"
raws = p.load(open(rawPath,'rb'))

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
    
    print "len data is", len(data)
    print "name is", name

    validateTrainDb(data)

    if not name in db_train:
        print "Adding", name, "to db_train"
        db_train[name] = []

    ## mark the files to note as annoations
    for r in data:
        r['Owner'] = name
        for d in diagnoses:
            if d in r:
                r['TaghianGold'] = 1

    db_train[name].extend(data)
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
    
    print "data is", data
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
    db_train = p.load(open(DB_TRAIN_PATH,'rb'))
    name = request.args.get("name") or "default"

    ## Generate relevant files in some directory with a name path
    trainDb = db_train[name] 
    stem = "boostexer/breast/api/"+"Prod"+"_"+name+"_"
    trainDb = db_train[name] + db_train['default']    
    generateClassifierFilesForProd.binarizeFilesForClassification(trainDb, stem, writeTrain=True, writeTest=False)
    preprocessTrain.main(trainDb)

    diagDictNew = preprocessTrain.main(trainDb) + p.load(open('rnn/diagDictTrain.p','rb'))
    p.dump(diagDictNew, open('rnn/diagDictTrain_'+name+".p','wb'))
    return "Success"


## Does all necessary preprocessing for test data given a batch_id in the unlabled data
## Script will prepare neural model and boosting model to evaluate on all reps where r['batch_id'] is in 
## the list of id's specified. If batch_id's is ommited, this will run across all unlabled data which may be very expensive.
## Return 0
@app.route("/updateUnlabeledSet", methods=['GET'])
def updateUnlabeledSet():
    db_test = p.load(open(DB_UNLABLED_PATH,'rb'))
    name = request.args.get("name") or "default"
    batch_id = request.args.get("batch_id") or "none"

    test_filt = db_test if batch_id == "none" else [d for d in db_test if "batch_id" in d and d["batch_id"] in batch_id]
    ## Generate relevant files in some directory with a name path
    stem = "boostexer/breast/api/"+"Prod"+"_"+name+"_"
    generateClassifierFilesForProd.binarizeFilesForClassification(test_filt, stem, writeTrain=False, writeTest=True)
    preprocessUnlabeled.main(test_filt,outname='unlalbeldReps_'+name+".p" )
    return "Success"


## Kicks off job to retrain model and label the corresping data
@app.route("/train", methods=['GET'])
def train():
    name = request.args.get("name") or "default"
    mode = request.args.get("mode") or "Prod"
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./trainModel.sh "+mode+"_"+name+"_"
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    neuralFlags = { 'unlabled_mode':False, 'trainPath':'diagDictTrain_'+name+".p"}
    p.dump( neuralFlags, open('rnn/flags.p','wb'))
    shellScript1 = "cd rnn; rm -rf logsIndep_"+name + ";" mkdir logsIndep_"+name
    shellScript2 = "./run.sh runIndep.py logsIndep_"+name
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    return "Success"

## Kicks off job to run model on the corresping data
## Will return all unlabeled data
@app.route("/predict", methods=['GET'])
def predict():
    ## run boost predict
    name = request.args.get("name") or "default"
    mode = "Prod"    
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./runModel.sh "+mode+"_"+name+"_"
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)

    ## aggregate boost predict
    stem = "classification_results/API/Prod_"+name+"_"
    db_unlabeled = p.load(open(DB_UNLABLED_PATH,'rb'))
    for r in db_unlabeled:
        if not "MRNPlusX" in r or not "Report_Date_TimePlusX" in r:
            r["MRNPlusX"]= "0"
            r["Institution"] ="UNK"
            r["Report_Date_TimePlusX"] = datetime.now().isoformat()
    reportsDBAll = createEpisodes.aggregateResults(db_unlabeled, stem)
    print "Calling labelMaxDXBool"
    createEpisodes.getMaxDX(reportDB)
    print "Calling build episode"
    reportDBBoost, episodeDB = createEpisodes.buildEpisodes(reportDB, True)

    neuralFlags = { 'unlabled_mode':True, 'unlabeledPath':'unlalbeldReps_'+name+".p", 'outPath':'lableledReps_'+name+'.p'}
    p.dump( neuralFlags, open('rnn/flags.p','wb'))
    shellScript1 = "cd rnn; rm -rf logsIndep_"+name + ";" mkdir logsIndep_"+name
    shellScript2 = "./run.sh runIndep.py logsIndep_"+name
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    reportDBCNN = p.load( open('lableledReps_'+name+'.p','rb'))
    reportDB = mergeDBs(reportDBBoost, reportDBCNN)
    postProcessRules(reportDB)

    reportDBJ = exportToJSON.portToJSON(reportDB)  
    return json.dumps({'reportDB':reportDBJ})
    return "Success"



################ Helpers ######################
def validateTrainDb(trainDb):
    for r in trainDb:
        assert 'Report_Text_Segmented' in r and 'ReportID' in r

        for d in diagnoses:
            if d in r:
                assert r[d] in constantValidLabelDict[d]

def mergeDBs(boost, cnn):
    return cnn

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
    for r in db_train:
        if hasCat(r, const_cancers):
            r['cancer'] = 'Present'
	else:
	    r['cancer'] = "Absent"
        if hasCat(r, const_atypias):
            r['atypia'] = 'Present'
	else:
	    r['atypia'] = "Absent"

        if r['cancer'] == 'Absent':
            for k in ['ER','PR','Her2 (Fish)', 'ECE', 'LVI','BVI', 'Are there positive LN?', 'ITC ']:
                r[k] = 'NA'

## Call this to start appex
if __name__ == "__main__":
    print "Begin API"
    app.run(host="0.0.0.0")
    db_train.close()
