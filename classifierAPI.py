import pickle as p
from constants import *
import sys
sys.path.append("buildNewDataset")
sys.path.append("trainClassifier")
sys.path.append("preprocessDataset")
sys.path.append("analysis")
import createEpisodes
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

app = Flask(__name__)


rawPath = "reportDB+red+clean.p"
dbPath = "reportDB.p"


raws = p.load(open(rawPath,'rb'))
def isAnnotation(r):
    return ('TaghianGold' in r and 'TaghianGold' == 1 ) or ('Correct' in r and r['Correct'] == 'Y')
base = []
for r in raws:
    r['Owner'] = 'default'
    if isAnnotation(r):
        base.append(r)

try:
    db = p.load(open(dbPath, 'rb'))
except Exception, e:
    print "Init db"
    db = {'default': base }

RequiredPreprocessFields = ['Report_Text']
RequiredTrainDbFields = ['ReportID', 'Report_Text_Segmented']
models = ['Boost', 'MaxEnt', 'CNN'] # MaxEnt and CNN not ready


## Given a JSON list of dicts, where  each dict represent a report:
## Parse the dict for daignoses, and add annotations if found
##  @name specifies user, izzy don't worry about this
## @raw specifies if the data has been preprocessed before, 
## @save specifies if i should resave what you gave me to the db file
## Example:
## [ {Report_Text: }]
## @return: 0
@app.route("/addData", methods=['POST'])
def addData():#data, name='default', raw=False, save=False):
    data = request.form.get("data") or []
    name = request.form.get("name") or "default"
    raw = request.form.get("raw") or False
    save = request.form.get("save") or False

    if not data == []:
        data = json.loads(data)
    # Preprocess bilaterals if need be
    if raw:
        data = preprocessReports(data)

    validateTrainDb(data)

    if not name in db:
        print "Adding", name, "to db"
        db[name] = base
    ## mark the files to note as annoations
    for r in data:
        r['Owner'] = name
        for d in diagnoses:
            if d in r:
                r['TaghianGold'] = 1

    db[name].extend(data)

    if save:
        p.dump(db, open(dbPath))

    return "Success"

## Does all necessary preprocessing for the model on the dataset
## model specifies the underlying model used, Boost is what Adam used
## mode refers to training the model for development (so you can call evaluate and 
## interpretDb) or Prod for production, where all annotations are used
## Return 0
@app.route("/updateTrainSet", methods=['GET'])
def updateTrainSet():#name='default', model='Boost', mode="Dev"):
    name = request.args.get("name") or "default"
    model = request.args.get("model") or "Boost"
    mode = request.args.get("mode") or "Prod"
    assert model in models
    assert mode in ["Prod", "Dev"]
    if model == "Boost":
        ## Generate relevant files in some directory with a name path
        stem = "boostexer/breast/api/"+mode+"_"+name+"_"
        if mode == "Prod":
            generateClassifierFilesForProd.binarizeFilesForClassification(db[name], stem)
        else:
            generateClassifierFilesForDev.binarizeFilesForClassification(db[name], stem)
        

    elif model == "MaxEnt" or model == "CNN":
        ## Run vectorizer to get features
        raise NameError("Model type not supported")
    return "Success"

## Kicks off job to retrain model and label the corresping data
## Use dev to train model without heldout test to get numbers
## use prod to use all labeled data as train, and then run on all unlabeled
@app.route("/trainAndPredict", methods=['GET'])
def trainAndPredict():#name="default", mode="Dev"):
    name = request.args.get("name") or "default"
    mode = request.args.get("mode") or "Prod"
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./trainModel.sh "+mode+"_"+name+"_"
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    return "Success"

## Kicks off job to run model on the corresping data
## Use dev to train model without heldout test to get numbers
## use prod to Prod Trained model on all unlabeled data
@app.route("/predict", methods=['GET'])
def predict():#name="default", mode="Dev"):
    name = request.args.get("name") or "default"
    mode = request.args.get("mode") or "Dev"    
    shellScript1 = "cd boostexer/breast/api/"
    shellScript2 = "./runModel.sh "+mode+"_"+name+"_"
    subprocess.call(shellScript1 + ";" + shellScript2, shell=True)
    return "Success"




## Assume evaluate has been run. Interpret results from last eval
@app.route("/results", methods=['GET'])
def getResults():#name='default'):
    name = request.args.get("name") or "default"
    results = interpretResults.main("classification_results/API/Dev_"+name+"_")    

    return json.dumps(results)

## Asume predict / trainPredict has been run, this consolidates the predict raw files into a DB 
## returns reportDb, episodeDB
## reportDb -> reportlevel details (keep repID const) for all extractions on all unlabeled
## episodeDb -> reportDb consolidated into windows of diff reports on same month in 6 month
## consecutive period
@app.route("/getPredictions", methods=['GET'])
def getPredictions():#name='default'):
    name = request.args.get("name") or "default"
    stem = "classification_results/API/Prod_"+name+"_"
    filtData = createEpisodes.removeUnexpectedColumns(db[name])
    print "Calling export"
    reportsDBAll = createEpisodes.aggregateResults(filtData, stem)
    rawData  = sorted( db[name], key=itemgetter('ReportID') )

    reportDB = {}
    for i in range(len(rawData)):
        raw = rawData[i]
        rep = reportsDBAll[i]
        assert rep['Report_Text'] == raw['Report_Text']
        if raw['Owner'] == name:
            for k in rawData[i]:
                if not k in cols and not k in reportsDBAll[i]:
                    reportsDBAll[i][k] = rawData[i][k]
            reportDB[i] = reportsDBAll[i]
    
    print "Calling labelMaxDXBool"
    createEpisodes.getMaxDX(reportDB)

    print "Calling build episode"
    reportDB, episodeDB = createEpisodes.buildEpisodes(reportDB, True)

    reportDBJ = exportToJSON.portToJSON(reportDB)  
    episodeDBJ = exportToJSON.portToJSON(episodeDB,episodeMode=True)    
    
    postProcessRules(reportDBJ)
    postProcessRules(episodeDBJ)

    return json.dumps({'reportDB':reportDBJ, 'episodeDB': episodeDBJ})

################ Helpers ######################
def validateTrainDb(trainDb):
    for r in trainDb:
        assert 'Report_Text_Segmented' in r and 'ReportID' in r

        for d in diagnoses:
            if d in r:
                assert r[d] in constantValidLabelDict[d]

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


def hasCat(r, cat):
    for c in cat:
        if r[c] == 'Present':
            return True
    return False


## Runs enforces global constraints like ER/PR NA given no cancer
def postProcessRules(db):
    for r in db:
        if hasCat(r, const_cancers):
            r['cancer'] = 'Present'

        if hasCat(r, const_atypias):
            r['atypia'] = 'Present'

        if r['cancer'] == 'Absent':
            for k in ['ER','PR','Her2 (Fish)', 'ECE', 'LVI','BVI', 'Are there positive LN?', 'ITC ']:
                r[k] = 'NA'

## Call this to start appex
if __name__ == "__main__":
    print "Begin API"
    app.run(host="0.0.0.0")
