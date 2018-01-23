# MGH Breast Cancer Pathology Report Project

# File Usage <br />
There is a file system set up under ```Dropbox (Partners HealthCare)/Extraction``` designed to make usage as simple and customizable as possible. 

The folder schema is as follows:
```
Dropbox (Partners HealthCare)
|__ ...
|
|__ Extraction
|   |
|   |__ diagnoses.xlsx -> follow the current format to add/rearrange keys and possible values
|   | 
|   |   ***************** TRAINING *****************
|   |__ ForTrainingXML -> add xml files for training
|   |   |__ ...
|   |   
|   |__ PastTraining -> previously trained files are stored here
|   |   |__ ...
|   |   |__ TrainMarkersOct26.xml
|   |   |__ TrainOct20.xml
|   |   
|   |   ***************** PARSING *****************
|   |__ ForParsingXML -> add xml or xlsx files for labeling
|   |   |__ ...
|   |   
|   |__ ForParsingHL7 -> add hl7 files for labeling
|   |   |__ ...
|   |  
|   |__ ParsedCSV -> labeled reports from the ForParsing folders will be stored here as csv files
|   |   |__ ...
|   |   |__ NewMammoplastiesOct2017.csv
|   |   |__ PathologyExtraThatWasMissingSept2017.csv
|   |  
|   |__ PastReports -> finished xml and hl7 files will be moved here
|   |   |__ ...
|   |   |__ NewMammoplastiesOct2017.xlsx
|   |   |__ PathologyExtraThatWasMissingSept2017.xml
|   |  
|   |__ CorruptReports -> invalid files from ForParsing folders
|   |   |__ ...
|   |  
|   |   ***************** EVALUATION *****************
|   |__ EvalSets -> add xlsx files for evaluation
|   |   |__ ...
|   |   |__ evalDB.xlsx
|   |   |__ pakisDB.xlsx
|   |  
|   |__ Results -> category scores from the evaluation will be stored here as xlsx files
|   |   |__ ...
|   |   |__ evalDB_YEAR_DAY_MONTH.xlsx
|   |   |__ pakisDB_YEAR_DAY_MONTH.xlsx
|   |  
```


# How to start service? <br />
You can either setup a docker machine with the right environment to run/use the API, or use the rosetta2 service.   
## Docker Setup 
If you need to run this locally instead of hitting the MIT API, we recommend Docker.
 [dockerfile](dockerfile) shows a working example.

## MIT Server / MGH Server 
If you need to restart it, do: 
export FLASK_APP=classifierAPI.py; 
flask run


# API Usage  <br />
The following API let's you add training data, train models, and get predictions for given reports. Under the hood, it uses boosting for annotation sparse classes and CNN for annotation rich classes. 


For example usage see apiDemo.py, which does everything using the python requests library. 
The api is available at: https://172.17.140.132:5000/\[endpoint\] (under mgh firewall) and https://rosetta7.csail.mit.edu:5000 (upon request in order to avoid hogging gpu resources)

For questions, please ping @yala on slack.
