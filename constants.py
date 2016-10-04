import datetime
import pickle as p

MODE = "TAGHIAN"
analyzeBoth = False
if analyzeBoth:
  submode = "Analyze both"
else:
  submode = "no"

baseline = False

#Shared constants for creating episodes
dataPath = "rawBreastPathReport.p"
outPath = "reportDB.p"
episodePath = "episodeDB.p"
goldDataPath = 'goldPathReports.p'
JSONReportPath = "reportDB.json"
JSONEpisodePath = "episodeDB.json"

def replaceSpaces(label):
    return '_'.join(str(label).split())

metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution', 'DOBPlusX']

SIX_MONTHS = datetime.timedelta(365/2)

hueLabels = []
if MODE == "Breast":
    reportTextKey = "Report_Text_Segmented"
    #Outcomes constants
    diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'IDC', u'LCIS', \
                 u'ADH',\
                 u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis',  u'ALH']#, 'cancer', 'atypia']#, 'ADH_DCIS', 'Phylodes']

    if analyzeBoth:
      diagnoses = [ u'BreastSide', u'Red_DCIS', u'Red_ILC', u'Red_IDC', u'Red_LCIS', \
                 u'Red_ADH',\
                 u'LobularNeoplasia', u'FlatEpithelial',  
                 u'BluntAdenosis',  u'Red_ALH']
                 

    #Contants for creating episodes

    cols = diagnoses + metaData + ['Report_Text_Segmented', 'Report_Text', "Preprocessed_Report_Text"] 

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/breast/labled/pathology.data"
    testOutPath = "boostexer/breast/labled/pathology.test"
    devOutPath = "boostexer/breast/labled/pathology.dev"

    allDataStem = "boostexer/breast/unlabled/pathology_all"


elif MODE == "ALL_CANCER":
    print "MODE IS ALL CANCER"

elif MODE == "TAGHIAN":
  reportTextKey = "Report_Text_Segmented"

  lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5}
  maxedOutDictToIndx = {'Oncotype score':-1, 'Oncotype date':-1}  
  maxedOutList = ['Oncotype score', 'Oncotype date']
  externalList = ['TumorGrade']  

  filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
  'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'Micro or Gross',
  'Number of LN with < =0.02 cm', 'Method size', 'Radical Mastectomy']
  # TODO Remove ECE and debug why bad class name    Micro or Gross   Number of LN with < =0.02 cm Method size

  diagnoses = [
  u'Are there positive LN?', u'ITC ', u'PR',  
  u'Her2 (Fish)', u'ER', 'ECE', 'LVI', 'BVI',
  'Red ILC', 'Red ALH','Red DCIS', 'Red LCIS', 'Red IDC', 
  'Red ADH', 'Red BreastSide', 'Red FlatEpithelial','Red BluntAdenosis', 
  'Red LobularNeoplasia', 'cancer', 'atypia']#, 'BiopsyType']

  if baseline:
    diagnoses = [
    'Red ILC', 'Red ALH','Red DCIS', 'Red LCIS', 'Red IDC', 
    'Red ADH', 'Red BreastSide', 'Red FlatEpithelial','Red BluntAdenosis', 
    'Red LobularNeoplasia']

  #'Oncotype score']

  # diagnoses = ['Oncotype score']

  HueAnotationSource= ['DCIS', 'LCIS', 'IDC', 'ILC', 'ALH', 'ADH', 'BreastSide', 'FlatEpithelial', 'BluntAdenosis', 'LobularNeoplasia']
  diagSkip = ['ALH', 'ILC']
  BiopAnotationSource= [a + " Biop" for a in HueAnotationSource  if not a in diagSkip]
  SurgAnotationSource= [a + " Surg" for a in HueAnotationSource  if not a in diagSkip]


  MixedAnotations= ["Red "+d for d in HueAnotationSource]


  redRawDBPath = 'reportDB+red+clean.p'

  defaultLabelDict = { 'Are there positive LN?': 'No', 'Type of sampled LN (choice=None)':'Unchecked', 'ITC ':'No', 'PR':'Unknown',
      'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': 'Unchecked', 'Type of Surgery':'not_surgery', 'BiopsyType':'No_breast_biopsy',
      'Simple Mastectomy':'Unchecked', 'Her2 (Fish)':'Unknown', 'ER': 'Unknown', 'Nipple sparing Mastectomy':'Unchecked',
      'Type of sampled LN (choice=ALND (Axillary LN Dissection))':'Unchecked', 'ECE':'No', 
      'LVI': 'Not_reported', 'BVI': 'Not_reported', 'TumorGrade': 'Not_assessed', 'Red DCIS':'Absent', 'Red LCIS':'Absent', 'Red IDC':'Absent', 'Red ILC':'Absent',
      'Red ALH':'Absent', 'Red ADH':'Absent', 'Red BreastSide':'RIGHT', 'Red FlatEpithelial':'Absent','Red BluntAdenosis':'Absent', 'Red LobularNeoplasia': 'Absent',
      'cancer':'Absent', 'atypia':'Absent',
      'Oncotype score':'Low_risk'}


  extractions = [u'Max Tumor Size', 'Non Sentinel LN (# Malignant)', 'Sentinel LN (# Sampled)']

##TODO
##  getList = ['LVI','ECE', 'BVI' , 'Grade', Max Tumor Size, num lymph node pos vs neg, ]
##  Make Interface labels clearer
## Support categorical filtering

  constantValidLabelDict = {'Are there positive LN?': ['Yes', 'No'],
    'ECE': ['Yes', 'No'],
    'ER': ['Unknown', 'Negative', 'Positive'],
    'Her2 (Fish)': ['Unknown', 'Negative', 'Positive'],
    'ITC ': ['Yes', 'No'],
    'Nipple sparing Mastectomy': ['Checked', 'Unchecked'],
    'PR': ['Unknown', 'Negative', 'Positive'],
    'Simple Mastectomy': ['Checked', 'Unchecked'],
    'Type of Surgery': ['Mastectomy',  '2nd_Re-Excision', 'not_surgery', '1st_Re-Excision', 'Excisional_biopsy_(Lumpectomy)'],
    'BiopsyType': ['Incision', 'Excision', 'No_breast_biopsy'],
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
    'Red FlatEpithelial':['Present','Absent'],
    'Red BluntAdenosis':['Present','Absent'],
    'Red LobularNeoplasia':['Present','Absent'],
    'cancer': ['Present','Absent'],
    'atypia': ['Present','Absent'],
    'Red BreastSide': ['RIGHT', 'LEFT'],
    'Oncotype score': ['Low_risk', 'Mid_risk', 'High_risk']
    }

  analysisLabelDict = {'Are there positive LN?': ['Yes', 'No'],
    'ER': ['Unknown', 'Negative', 'Positive'],
    'Her2 (Fish)': ['Unknown', 'Negative', 'Positive'],
    'ITC ': ['Yes', 'No'],
    'PR': ['Unknown', 'Negative', 'Positive'],    
    'ECE': ['Yes', 'No'],
    'LVI': ['Yes', 'No', 'Not_reported'],
    'BVI': ['Yes', 'No', 'Not_reported'],
    'TumorGrade': ['Well_differentiated_(grade_I)', 'Moderate_(grade_II)', 'Poor_(grade_III)_Undifferentiated'],
    'Red DCIS':  ['Present','Absent'], 
    'Red LCIS': ['Present','Absent'], 
    'Red IDC': ['Present','Absent'], 
    'Red ILC': ['Present','Absent'], 
    'Red ALH': ['Present','Absent'], 
    'Red ADH': ['Present','Absent'],
    'Red FlatEpithelial':['Present','Absent'],
    'Red BluntAdenosis':['Present','Absent'],
    'Red LobularNeoplasia':['Present','Absent'],
    'Red BreastSide': ['RIGHT', 'LEFT'],
    'cancer': ['cancer','no_cancer'],
    'atypia': ['atypia','no_atypia'],
    'BiopsyType': ['Incision', 'Excision', 'No_breast_biopsy']

    }


  JSONLabelDict = {
  }

  JSONLabelNameDict = {
    'Her2 (Fish)': 'Her2',
    'Type of Surgery':'Type_of_Surgery',
    'BiopsyType': 'BiopsyType',
    'Type of sampled LN (choice=ALND (Axillary LN Dissection))': 'Axillary_LN_Dissection',
    'Type of sampled LN (choice=None)': 'No_Sampled_LN',
    'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': 'Sentinel_LN_Biopsy',
    'ITC ': 'ITC',
    'ECE': 'EIC',
    'Are there positive LN?':'PositiveLN',
    'Red DCIS':   'DCIS',
    'Red LCIS':  'LCIS',
    'Red IDC':  'IDC',
    'Red ILC':  'ILC',
    'Red ALH':  'ALH',
    'Red ADH':  'ADH',
    'Red FlatEpithelial': 'FlatEpithelial',
    'Red BluntAdenosis': 'BluntAdenosis',
    'Red LobularNeoplasia': 'LobularNeoplasia',
    'Red BreastSide':'BreastSide'}
  labelsForEpisodes = diagnoses

  hueLabels = []

      # Constants for genBoostexaFiles
  trainOutPath = "boostexer/breast/taghian/red.data"
  testOutPath = "boostexer/breast/taghian/red.test"
  devOutPath = "boostexer/breast/taghian/red.dev"


  allDataStem = "boostexer/breast/unlabled/red_all"

  if submode == "Analyze both":

    redLabels = diagnoses    

    for label in hueLabels:
      if not label in constantValidLabelDict:
        constantValidLabelDict[label] = [1, 0]

    diagnoses = redLabels + hueLabels + ['cancer', 'atypia']
    print "len(diag), diag", len(diagnoses), diagnoses

  metaData = hueLabels + metaData

  cols = diagnoses + metaData + ['Report_Text_Segmented', 'Report_Text', "Preprocessed_Report_Text"]

  outPath = "reportDB+new.p"
  episodePath = "episodeDB+new.p"
  JSONReportPath = "reportDB+red.json"
  JSONEpisodePath = "episodeDB+red.json"



  
