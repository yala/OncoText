import datetime
import pickle as p

MODE = "TAGHIAN"
submode = "no"

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


if MODE == "Breast":
    #Outcomes constants
    diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
                 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
                 u'ADH', u'CancerInvInsituNOS',\
                 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']
    #Contants for creating episodes

    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"] 

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/breast/labled/pathology.data"
    testOutPath = "boostexer/breast/labled/pathology.test"
    devOutPath = "boostexer/breast/labled/pathology.dev"

    allDataStem = "boostexer/breast/unlabled/pathology_all"


elif MODE == "ALL_CANCER":
    print "MODE IS ALL CANCER"

elif MODE == "TAGHIAN":

  lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }
  filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
  'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'Max Tumor Size', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'ECE', 'Micro or Gross',
  'Number of LN with < =0.02 cm', 'Method size', 'Radical Mastectomy']
  # TODO Remove ECE and debug why bad class name    Micro or Gross   Number of LN with < =0.02 cm Method size

  diagnoses = [u'Are there positive LN?', u'Type of sampled LN (choice=None)', u'ITC ', u'PR',  
  u'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))', u'Type of Surgery',  u'Type of biopsy', u'Simple Mastectomy',
  u'Her2 (Fish)', u'ER',u'Nipple sparing Mastectomy', u'Type of sampled LN (choice=ALND (Axillary LN Dissection))']#, 'ECE']

  redRawDBPath = 'reportDB+red+clean.p'

  defaultLabelDict = { 'Are there positive LN?': 'No', 'Type of sampled LN (choice=None)':'Unchecked', 'ITC ':'Not_Reported', 'PR':'Unknown',
      'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': 'Unchecked', 'Type of Surgery':'not_surgery', 'Type of biopsy':'No_breast_biopsy',
      'Simple Mastectomy':'Unchecked', 'Her2 (Fish)':'Unknown', 'ER': 'Unknown', 'Nipple sparing Mastectomy':'Unchecked',
      'Type of sampled LN (choice=ALND (Axillary LN Dissection))':'Unchecked'#, 'ECE':'Not_Reported'

  }

  constantValidLabelDict = {'Are there positive LN?': ['Yes', 'No'],
    'ECE': ['Yes','Yes_(Micro)', 'No', 'Yes_(Macro)', 'Not_Reported'],
    'ER': ['Unknown', 'Negative', 'Positive'],
    'Her2 (Fish)': ['Unknown', 'Negative', 'Positive'],
    'ITC ': ['Yes', 'No', 'Not_Reported'],
    'Nipple sparing Mastectomy': ['Checked', 'Unchecked'],
    'PR': ['Unknown', 'Negative', 'Positive'],
    'Simple Mastectomy': ['Checked', 'Unchecked'],
    'Type of Surgery': ['Mastectomy',  '2nd_Re-Excision', 'not_surgery', '1st_Re-Excision', 'Excisional_biopsy_(Lumpectomy)'],
    'Type of biopsy': ['Incisional_biopsy',  'Fine_needle_aspiration_(FNA)', 'No_breast_biopsy', 'Core_biopsy',  'Other', 'Needle_biopsy'],
    'Type of sampled LN (choice=ALND (Axillary LN Dissection))': ['Checked', 'Unchecked'],
    'Type of sampled LN (choice=None)': ['Checked', 'Unchecked'],
    'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': ['Checked', 'Unchecked']}


  JSONLabelDict = {
    'Checked':1,
    'Unchecked':0,
    'Yes': 1,
    'No':0,
    'Positive':1,
    'Negative': 0
  }

  JSONLabelNameDict = {
    'Her2 (Fish)': 'Her2',
    'Type of Surgery':'Type_of_Surgery',
    'Type of biopsy': 'Type_of_Biopsy',
    'Type of sampled LN (choice=ALND (Axillary LN Dissection))': 'Axillary_LN_Dissection',
    'Type of sampled LN (choice=None)': 'No_Sampled_LN',
    'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': 'Sentinel_LN_Biopsy',
    'ITC ': 'ITC'
  }
  labelsForEpisodes = ['ITC ', 'ER', 'Her2 (Fish)', 'PR']

  hueLabels = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', 
               u'IDC', u'LCIS', 
               u'ADH', u'LobularNeoplasia', u'FlatEpithelial', 
               u'BluntAdenosis', u'ALH']

      # Constants for genBoostexaFiles
  trainOutPath = "boostexer/breast/taghian/red.data"
  testOutPath = "boostexer/breast/taghian/red.test"
  devOutPath = "boostexer/breast/taghian/red.dev"


  allDataStem = "boostexer/breast/unlabled/red_all"

  if submode == "Analyze both":

    redLabels = diagnoses    

    for label in hueLabels:
      constantValidLabelDict[label] = {1, 0}

    diagnoses = redLabels + hueLabels


  metaData = hueLabels + metaData

  cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]

  outPath = "reportDB+new.p"
  episodePath = "episodeDB+new.p"
  JSONReportPath = "reportDB+red.json"
  JSONEpisodePath = "episodeDB+red.json"



  