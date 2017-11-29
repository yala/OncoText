import datetime
import cPickle as p
from openpyxl import load_workbook
from collections import OrderedDict

MODE = "TAGHIAN"
baseline = False
submode=False

def replaceSpaces(label):
    return '_'.join(str(label).split())

def parseKeys(inp):
    wb = load_workbook(inp)
    sheet = wb.active
    data = OrderedDict()
    for row in sheet.rows:
        values = [str(cell.value) for cell in row if cell.value != None]
        if len(values) > 0:
            if len(values) > 1:
                data[values[0]] = values[1: ]
            else:
                data[values[0]] = []
    return data


HOMEDIR = '/home/nlp/'
PATHOLOGYDIR = HOMEDIR+'pathology/'
DROPBOXDIR = HOMEDIR+'Dropbox (Partners HealthCare)/NLP_Extraction/'
EVALDIR = DROPBOXDIR+'GoldSets/'
PARSINGDIR = DROPBOXDIR+'ForParsing/'
TRAININGDIR = DROPBOXDIR+'ForTraining/'
RESULTSDIR = DROPBOXDIR+'NLP_Results/'

metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'ReportID', 'Correct', 'Institution', 'DOBPlusX']

SIX_MONTHS = datetime.timedelta(365/2)
#SIX_MONTHS = 365/2

hueLabels = []
if MODE == "TAGHIAN":
  reportTextKey = "Report_Text_Segmented"

  columnKeys = parseKeys(DROPBOXDIR+'SQL_KeysAndValues.xlsx')
  # columnKeys = {
  #     'Report_Text_Segmented': [],
  #     'Report_Text': [],
  #     'Report_Date_Time': [],
  #     'Owner': [],
  #     'Institution': [],
  #     'MRN': [],
  #     'EMPI': [],
  #     'ReportID': [],
  #     'Organ': ['0', '1'],
  #     'PathologyType': ['Anatomic', 'Cytology'],
  #     'BiopsyType': ['Core', 'Excision', 'Other', '9'],
  #     'BreastSide': ['l', 'r'],
  #     'CancerSuspicious': ['0', '1'],
  #     'InvasiveSuspicious': ['0', '1'],
  #     'CancerInvInsituNOS': ['0', '1'],
  #     'InsituNOS': ['0', '1'],
  #     'IDC': ['0', '1'],
  #     'ILC': ['0', '1'],
  #     'TubularCancer': ['0', '1'],
  #     'CancerInvasive': ['0', '1'],
  #     'CancerInvNOS': ['0', '1'],
  #     'CancerNotOfBreastOrigin': ['0', '1'], 
  #     'CancerNOS': ['0', '1'],
  #     'DCIS': ['0', '1'],
  #     'ER': ['0', '1', '9'],
  #     'PR': ['0', '1', '9'],
  #     'Her2': ['0', '1', '9', '999'],
  #     'Her2Fish': ['0', '1', '9'],
  #     'Her2_IHC': ['0', '1+', '2+', '3+', '4+', '9'],
  #     'PositiveLN': ['0', '1'],
  #     'ECE': ['0', '1', '9'],
  #     'ITC': ['0', '1'], 
  #     'BVI': ['0', '1', '9'],
  #     'LVI': ['0', '1', '9'],
  #     'LCIS': ['0', '1'],
  #     'LobularNeoplasia': ['0', '1'],
  #     'ALH': ['0', '1'],
  #     'ADH_DCIS': ['0', '1'],
  #     'ADH': ['0', '1'],
  #     'FlatEpithelial': ['0', '1'],
  #     'Phyllodes': ['0', '1'],
  #     'SuspiciousForPhyllodes': ['0', '1'],
  #     'Papill': ['0', '1'],
  #     'BluntAdenosis': ['0', '1'],
  #     'NodeTissue': ['0', '1'],
  #     'filename': [],
  #     'batchID': [],
  #     'train': [],
  #     'validated': [],
  #   }

  diagnoses = {k:columnKeys[k] for k in columnKeys if len(columnKeys[k]) > 0}

  post_diagnoses = {k:diagnoses[k] for k in diagnoses}
  post_diagnoses['cancer'] = ['0', '1']
  post_diagnoses['atypia'] = ['0', '1']
  post_diagnoses['ER_Intensity'] = ['0', '1', '2', '3', '9']
  post_diagnoses['PR_Intensity'] = ['0', '1', '2', '3', '9']

  defaultLabelDict = {k:post_diagnoses[k][0] for k in post_diagnoses}
  # defaultLabelDict = { 'PositiveLN': '0', 'Type of sampled LN (choice=None)':'Unchecked', 'ITC':'0', 'PR':'9',
  #     'BiopsyType':'9', 'Her2Fish':'9', 'ER': '9', 'ECE':'0',
  #     'LVI': '9', 'BVI': '9', 'TumorGrade': '9', 'DCIS':'0', 'LCIS':'0', 'IDC':'0', 'ILC':'0',
  #     'ALH':'0', 'ADH':'0', 'BreastSide':'r', 'FlatEpithelial':'0','BluntAdenosis':'0', 'LobularNeoplasia': '0',
  #     'cancer':'0', 'atypia':'0',
  #     'Oncotype score':'Low_risk',
  #     'ADH_DCIS':'0', 'Phyllodes':'0', 'CancerNOS':'0', 'InvasiveSuspicious':'0', 'InsituNOS':'0', 'CancerInvInsituNOS':'0',
  #     'SuspiciousForPhyllodes':'0', 'CancerSuspicious':'0', 'TubularCancer':'0',
  #     'Papill':'0',
  #     'CancerInvasive':'0',
  #     'CancerInvNOS':'0',
  #     'NodeTissue':'0', #'Node_x0020_tissue'
  #     'CancerNotOfBreastOrigin':'0', #CancerNotOfBreastOrigin
  #     'PathologyType':'Anatomic',
  #     "Organ":"0",
  #     "ER_Intensity":"9", "PR_Intensity":"9", "Her2":"9", "Her2_IHC":"9"
  #     }

  boostexer_diagnoses = ["CancerInvInsituNOS", "CancerNOS", "BiopsyType", "Her2", "Her2_IHC", "ITC", "PR", "Her2Fish", "ER", "ECE", "LVI", "BVI", "PathologyType", "Organ", "CancerInvasive", "CancerInvNOS", "NodeTissue", "CancerNotOfBreastOrigin", "BluntAdenosis", "PositiveLN"]
  boostexer_diagnoses = [d for d in boostexer_diagnoses if d in diagnoses]
  nn_diagnoses = [d for d in diagnoses if d not in boostexer_diagnoses]

  const_cancers = [
    'ILC','DCIS', 'IDC',
    'TubularCancer',
    'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin'
    ]

  const_atypias = [
  'ALH','ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia'
  ]

  markers = [ 'ER', "ER_Intensity", 'PR',"PR_Intensity", "Her2", 'Her2Fish',  "Her2_IHC",  'Are there Positive LN?','ECE','ITC' ,'BVI', 'LVI']
  groupings = {
      'atypias': [k for k in ['Report_Text_Segmented', 'BreastSide', 'LCIS', 'LobularNeoplasia','ALH', 'ADH_DCIS', 'ADH' ,'FlatEpithelial'] if k in columnKeys],
      'cancersSansMarkers': [k for k in ['Report_Text_Segmented', 'BreastSide' ,'CancerSuspicious' ,'InvasiveSuspicious', 'CancerInvInsituNOS','InsituNOS','InvasiveNOS','IDC','ILC','TubularCancer', 'DCIS'] if k in columnKeys],
      'phyllodesAndPapil':[k for k in ['Report_Text_Segmented', 'BreastSide', 'Phyllodes', 'SuspiciousForPhyllodes','Papill'] if k in columnKeys],
      'allNN': ['Report_Text_Segmented']+[k for k in nn_diagnoses],
      'allNNSansMarkers': ['Report_Text_Segmented']+[k for k in nn_diagnoses if k not in markers],
  }

  redRawDBPath = '../reportDB+red+clean.p'

  reportsTableName = "reports"
  reportsNoBreastTableName = "nonbreastReports"
  backupTableName = "backup"
  backupNoBreastTableName = "nonbreastBackup"

  trainOutPath = "../boostexer/breast/taghian/red.data"
  testOutPath = "../boostexer/breast/taghian/red.test"
  devOutPath = "../boostexer/breast/taghian/red.dev"


  allDataStem = "../boostexer/breast/unlabled/red_all"


  cols = boostexer_diagnoses + metaData + ['Report_Text_Segmented', 'Report_Text']

  outPath = "../reportDB+new.p"
  dataPath = "../rawBreastPathReport.p"

  episodePath = "../episodeDB+new.p"
  JSONReportPath = "../reportDB+red.json"
  JSONEpisodePath = "../episodeDB+red.json"
