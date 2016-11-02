# MGH Breast Cancer Pathology Report Project

# API Usage
The following API let's you add training data, train models, get performance information on a development set, and get results on the whole cohort. Currently, the model only supports a boosting based extractor, but it is built to easily support other approachs like CNNs

# Endpoints

## addData/
Method: Post
Params: Data, Name, Raw, Save
Description: The way to add labeled or unlabled data to the tool. 

Data - The list of pathology reports, strucuted as a json list of dicts. Empty by default.
Name - Specifies user, default is mgh user, which is named "default"
Raw  - Specifies if the data has been preprocess already. For Validator, show be False, for Global, should be True.
Save - Probably healthy to save db storing all the data to a file from time to time.

Example: curl -X "POST" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/addData"

## updateTrainSet/
Method: Get
Params: Name, Model, Mode
Description: Generates a set of files necessary for training and using the model. Must be done everytime you addData, labeled or unlabeled. 
--
Name - Specifies user, default is mgh user, which is named "default"
Model- Specifies model to run. Currently only Boosting is supported, and default is "Boost"
Mode - Options are "Dev" or "Prod". Dev generates a splits the annotated data into a training and heldout test set. This can be useful to validate F-scores are as expected and we aren't getting noisy annotations. "Prod" uses all annotations to train the calssifier, and predicts values for the entire dataset (of mostly unlabeled data).

Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/updateTrainSet"

## trainAndPredict/
Method: Get
Params: Name, Mode
Description: Trains the boosting model on previously generated datafiles from updateTrainSet/. Once training complete, runs the model on the Test or Unlabeled set. 

Name - Specifies user, default is mgh user, which is named "default"
Mode - Options are "Dev" or "Prod". Dev run's the model on the Train/Test split of annotations, while "Prod" predicts values for the entire dataset (of mostly unlabeled data).

Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/trainAndPredict"

## predict/
Method: Get
Params: Name, Model, Mode
Description: Same as trainAndPredict, but does not retrain the model. 

Name - Specifies user, default is mgh user, which is named "default"
Mode - Options are "Dev" or "Prod". Dev run's the model on the Train/Test split of annotations, while "Prod" predicts values for the entire dataset (of mostly unlabeled data).

Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/predict"

## results/
Method: Get
Params: Name
Description: Given a "Dev" model has called train and predict, this returns a josn dictionary of dictionaries where each dict is the performance (accuracy, fscore) of an extracted category on the test set. 

Name - Specifies user, default is mgh user, which is named "default"

Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/results"


## getPredictions/
Method: Get
Params: Name
Description: Given a "Prod" model has called train and predict, this returns a json blob of "ReportDB" and "EpisodeDB". ReportDB is all the reports added for that user (specified through name) with the preictied extractions. EpisodeDB is a useful aggregation of reports about the same events into episodes of care. 

Name - Specifies user, default is mgh user, which is named "default"

Example: curl -X "GET" -H "Cache-Control: no-cache" "http://rosetta2.csail.mit.edu:5000/getPredictions"
