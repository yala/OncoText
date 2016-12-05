# MGH Breast Cancer Pathology Report Project

# How to start service? <br />
You can either setup a docker machine with the right environment to run/use the API, or use the rosetta2 service.   
## Docker Setup 
If you need to run this locally instead of hitting the MIT API, we recommend Docker.
 [dockerfile](dockerfile) shows a working example.

## MIT Server
If you need to restart it on Rosetta2, do: 
export FLASK_APP=classifierAPI.py; 
flask run

# API Usage  <br />
The following API let's you add training data, train models, get performance information on a development set, and get results on the whole cohort. Currently, the model only supports a boosting based extractor, but it is built to easily support other approachs like CNNs


# Endpoints

## addData/
Method: Post  <br />
Params: Data, Name, Raw, Save <br />
Description: The way to add labeled or unlabled data to the tool.  <br />
Data - The list of pathology reports, strucuted as a json list of dicts. Empty by default. <br />
Name - Specifies user, default is mgh user, which is named "default" <br />
Raw  - Specifies if the data has been preprocess already. For Validator, show be False, for Global, should be True. <br />
Save - Probably healthy to save db storing all the data to a file from time to time. <br />
 <br />
Example: curl -X "POST" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/addData" <br />
Example: curl -X "POST" "http://rosetta2.csail.mit.edu:5000/addData" -d "raw=True&data=[{\"Report_Text\":\"Example Text\", \"Report_Date_TimePlusX\":\"2016-12-4T\" }]"
 <br />
## updateTrainSet/ <br />
Method: Get <br />
Params: Name, Model, Mode <br />
Description: Generates a set of files necessary for training and using the model. Must be done everytime you addData, labeled or unlabeled.  <br />
 <br />
Name - Specifies user, default is mgh user, which is named "default" <br />
Model- Specifies model to run. Currently only Boosting is supported, and default is "Boost" <br />
Mode - Options are "Dev" or "Prod". Dev generates a splits the annotated data into a training and heldout test set. This can be useful to validate F-scores are as expected and we aren't getting noisy annotations. "Prod" uses all annotations to train the calssifier, and predicts values for the entire dataset (of mostly unlabeled data).  <br />
 <br />
Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/updateTrainSet"
 <br />
## trainAndPredict/ <br />
Method: Get <br />
Params: Name, Mode <br />
Description: Trains the boosting model on previously generated datafiles from updateTrainSet/. Once training complete, runs the model on the Test or Unlabeled set.  <br />
 <br />
Name - Specifies user, default is mgh user, which is named "default" <br />
Mode - Options are "Dev" or "Prod". Dev run's the model on the Train/Test split of annotations, while "Prod" predicts values for the entire dataset (of mostly unlabeled data). <br />
 <br />
Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/trainAndPredict" <br />
 <br />
## predict/
Method: Get <br />
Params: Name, Model, Mode <br />
Description: Same as trainAndPredict, but does not retrain the model.  <br />
 <br />
Name - Specifies user, default is mgh user, which is named "default" <br />
Mode - Options are "Dev" or "Prod". Dev run's the model on the Train/Test split of annotations, while "Prod" predicts values for the entire dataset (of mostly unlabeled data). <br />
 <br />
Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/predict" <br />
 <br />
## results/ <br />
Method: Get <br />
Params: Name <br />
Description: Given a "Dev" model has called train and predict, this returns a josn dictionary of dictionaries where each dict is the performance (accuracy, fscore) of an extracted category on the test set.  <br />
 <br />
Name - Specifies user, default is mgh user, which is named "default" <br />

Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/results" <br />
 <br />

## getPredictions/ <br />
Method: Get <br />
Params: Name <br />
Description: Given a "Prod" model has called train and predict, this returns a json blob of "ReportDB" and "EpisodeDB". ReportDB is all the reports added for that user (specified through name) with the preictied extractions. EpisodeDB is a useful aggregation of reports about the same events into episodes of care.  <br />
 <br />
Name - Specifies user, default is mgh user, which is named "default" <br />
 <br />
Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/getPredictions"


### But is it online?
- [x] Online
