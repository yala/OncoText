# OncoText - Information Extraction for Breast Cancer Pathology Reports

## About
OncoText is an information extraction service designed to parse structured data out of pathology reports. Currently, the system has pretrained models for categories like "DCIS", "LCIS", "ER Status", and around 20 more categories. Each extraction is modeled as document classification, and not as a tagging task.  The first version of the system and following technical extensions are described in:

   - [Using Machine Learning to Parse Breast Pathology Reports ](https://link.springer.com/article/10.1007%2Fs10549-016-4035-1). BCRT 2016
   - [Rationalizing Neural Predictions](https://people.csail.mit.edu/taolei/papers/emnlp16_rationale.pdf). EMNLP 2016


All pretrained models are available on a [docker image](https://hub.docker.com/r/yala/oncotext/), and were trained/developed in a collaboration with Dr. Kevin Hughes from Mass General, and Regina Barzilay's Lab at MIT CSAIL. All models were trained on Partners Healthcare Pathology reports, and results may transfer poorly to pathology reports from other venues, if the phrasing there is significantly diferent. OncoText is currently deployed at Mass General and is designed to support adding new categories, new training data, and new sets of documents to parse. In principle, this can be used on any free text reports given you provide training data via the API. It's setup as a webservice and can be accessed through HTTP requests.

You can run the docker as follows:
```

 sudo nvidia-docker run -it -p 5000:5000 -e LOGFILE=/OncoText/LOGS -e PICKLE_DIR=/OncoText/oncotext_files -e SNAPSHOT_DIR=/OncoText/snapshot -e CONFIG_XLSX=/OncoText/config.xlsx  -v PATH_TO_YOUR_LOGFILE:/OncoText/LOGS  -v PATH_TO_DB_DIR:/OncoText/oncotext_files  -v PATH_TO_CONFIG_EXCEL:/OncoText/config.xlsx -v PATH_TO_SNAPSHOT:/OncoText/snapshot  yala/oncotext:0.1.0

```

You can download the model snapshots from:
https://s3.amazonaws.com/oncotext-models/model-snapshots.tar.gz

<br/>

## System Requirements
[Docker](https://docs.docker.com/install/) is the only real requirment. 
We recommend a GPU machine for larger databases and heavier training loads. If running OncoWeb, it should be run a seperate CPU instance such that it doesn't compete for resources. A working docker can be found at [here](https://hub.docker.com/r/yala/oncotext/), and please look to the docker file if you wish to set this up on your server.

<br/>

## Configuration
All system configuration in managed in ```config.py```.

### Environment Variables
In order to use OncoText, you have to set the following environment variables:

    - PICKLE_DIR : This is the directory where to store the various train / raw databases you may way to parse.
    - SNAPSHHOT_DIR : This is the directory where to store model snapshots.
    - LOGFILE : Where the system will write all error/warning/info logs via pylogger
    - CONFIG_XLSX : The path of the category configuration excel file. See ``sample_category_excel.xlsx`` for an example. OncoText loads this excel file and interprets all rows with several column entries as categories to try to parse from the path reports.


### Neural net configuation settings
All Neural Net configuration, including the generation of rationales is defined in config.py. Please post an issue and ask if you'd like advice on tuning this. All the Neural Net code is in [text_nn](https://github.com/yala/text_nn), and lacks full documentation, but given interest, we will work on making that more public suitable.
<br/>


## API
You can interact with OncoText via the following HTTP Methods. In general, all requests take a query parameter of "name". Each name can be thought of as a user of oncotext, which its unique training data and data to parse. If training data / trained models are not available for a given user "name", then the pretrained default models will be used if available.

For a detailed look at how this works, I recommend looking at ```scripts/app.py```, and the tester ```test/api_test.py```.

### addTrain
You can ``POST`` new training data to OncoText via ```/addTrain```. OncoText preprocess the data, and add it to its train database. The next time OncoText is trained, it will train on the new data (in addition to the old).

```
addTrainResp = requests.post("http://localhost:5000/addTrain", data=json.dumps(newTrainData), params={"name":'default')
assert addTrainResp.status_code==200
```

### addUnlabeled
Adding unlabeled reports is quite similar to adding new train files. If you would like to label a set of new pathology reports, you can ``POST`` the data to OncoText, and it will perform the parse the new reports (in addition to the old) the next time it predicts.
```
addUnlabeledResp = requests.post("http://localhost:5000/addUnlabeled", data=json.dumps(newUnlabeledData), params={"name":'default'})
assert addUnlabeledResp.status_code==200
```

### train
This request tells OncoText to train its neural net based on the training reports you've previously added through ``addTrain``. This trains a seperate neural network for each extraction. In practice, we found indepdent models out performed ones jointly trained. OncoText will return Development set accuracies in the HTTP Response. 
```
trainResp = requests.get("http://localhost:5000/train", params={"name":'default'})
assert trainResp.status_code==200
```

### predict
After OncoText has trained, this request tells OncoText to run its prediction algorithm on the unlabeled reports you have previously added through ``addUnlabeled``. You also send a set of evaluation sets, and OncoText will score it's predictions on the unlabled set against matching records in the evaluation set. The accuracies are returned in the HTTP response. 
```
predResp = requests.get("http://localhost:5000/predict", params={"name":'default'}, data=json.dumps({"evaluation_set_filename": evaluation_set}))
assert predResp.status_code==200
```
<br/>



## OncoText Report Structure
OncoText relies on a couple special keys to know whats what. Under the hood, it stores all databases a as python lists of python dictionaries. Each dictionary represents a Pathology report for a single breas the ```RAW_REPORT_TEXT_KEY``` indicated the key of the full text. There are several other special keys, all of which specified in ```config.py```, and the handle things like post prediction pruning, what field is the date field, etc. For questions about this, feel free to reach out to @yala or post an issue. If there is interest, I'll update the documentation accordingly.


<br/>



## Intergration and Deployment
Oncotext is primarily used in conjunction with [OncoManage](https://github.com/yala/OncoManage). OncoManage sets up a folder structure where new training and unlabeled reports will automatically be added OncoText, and manages reporting on evaluation sets. It also handles exports to various databases, email notifications, and interfacing with a OncoWeb. OncoWeb is a [user interface](https://github.com/clarali/OncoWeb) for users to access and correct the machine's predictions. We are in the process of preparing all linked repos for public release. Some things are more tightly linked with our deployment at Mass General, but we hope that these tools will prove useful to the community.

<br/>

## Next Release
OncoText is still in alpha and at 0.1.0. The next release will include supporting rationale extraction on predict, and more sophisticated evaluation measures. 
