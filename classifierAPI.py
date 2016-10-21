import pickle as p

rawPath = "reportDB+red+clean.p"

diagnoses = [
  u'Are there positive LN?', u'ITC ', u'PR',  
  u'Her2 (Fish)', u'ER', 'ECE', 'LVI', 'BVI',
  'Red ILC', 'Red ALH','Red DCIS', 'Red LCIS', 
  'Red IDC', 'Red ADH', u'LobularNeoplasia', 
  'FlatEpithelial', 'BluntAdenosis','BreastSide',
  'cancer', 'atypia']

diagToValue = {'Are there positive LN?': ['Yes', 'No'],
    'ECE': ['Yes', 'No'],
    'ER': ['Unknown', 'Negative', 'Positive'],
    'Her2 (Fish)': ['Unknown', 'Negative', 'Positive'],
    'ITC ': ['Yes', 'No'],
    'Nipple sparing Mastectomy': ['Checked', 'Unchecked'],
    'PR': ['Unknown', 'Negative', 'Positive'],
    'Simple Mastectomy': ['Checked', 'Unchecked'],
    'Type of Surgery': ['Mastectomy',  '2nd_Re-Excision', 'not_surgery', '1st_Re-Excision', 'Excisional_biopsy_(Lumpectomy)'],
    'Type of biopsy': ['Incisional_biopsy',  'Fine_needle_aspiration_(FNA)', 'No_breast_biopsy', 'Core_biopsy', 'Needle_biopsy'],
    'Type of sampled LN (choice=ALND (Axillary LN Dissection))': ['Checked', 'Unchecked'],
    'Type of sampled LN (choice=None)': ['Checked', 'Unchecked'],
    'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': ['Checked', 'Unchecked'],
    'ECE': ['Yes', 'No'],
    'LVI': ['Yes', 'No', 'Not_reported'],
    'BVI': ['Yes', 'No', 'Not_reported'],
    'TumorGrade': ['Well_differentiated_(grade_I)', 'Moderate_(grade_II)', 'Poor_(grade_III)_Undifferentiated', 'Not_assessed'],
    'Red DCIS':  ['Present','Absent'], 
    'Red LCIS': ['Present','Absent'], 
    'Red IDC': ['Present','Absent'], 
    'Red ILC': ['Present','Absent'], 
    'Red ALH': ['Present','Absent'], 
    'Red ADH': ['Present','Absent'],
    'FlatEpithelial': ['Present','Absent'],
    'BluntAdenosis' : ['Present','Absent'],
    'BreastSide' : ['Right', 'Left']
    'cancer': ['cancer','no_cancer'],
    'atypia': ['atypia','no_atypia'],
    }



## Given a list of dicts, where  each dict represent a report:
## Parse the dict for daignoses, and add annotations if found
## Example:
## [ {Report_Text: }]
## @return: 0
def addTraining(trainDB):
    ## Can assume reports all ready preprocessed into left/right
    ## Some annotations per report
    ## gen boostexer files, and continue training. add to existing files
    return 0

## Generates test files for given testDB, and kick off model. Note, this is async.
## Return 0
def evaluate(testDB=None, name='default'):
    ## if testDB specified (#global), then make that test/set
    ## Hit's bash script to run and eval on that testset
    return 0


## Takes all unlabled data and produces relevant files, and kick off classification. 
## Note, this is async.
## Return 0
def predict(testDB=None, name='default'):
    ## if testDB specified (#global), then make that test/set
    ## Hit's bash script to run and eval on that testset
    return 0

## Assume evaluate has been run. Interpret results from last eval
def interpretResults(name='default'):
    ##
    return 0

## Asume predict has been run, this consolidates the predict raw files into a DB 
## returns reportDb, episodeDB
## reportDb -> reportlevel details (keep repID const) for all extractions on all unlabeled
## episodeDb -> reportDb consolidated into windows of diff reports on same month in 6 month
## consecutive period
def getPredictions(db, name='default'):
    reportDb, episodeDb = []
    return 0

## Kicks off job to retrain model
## Return 0
def retrain()
    return 0



## Notes:
# Handling namespaces. Want to support diff people having diff unlabled data to view
# One cannical train source

def populateDefault():


## Convert legacy db format to format specified in daigToValue
def normalizeDb()