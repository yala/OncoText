import datetime
import cPickle as p

MODE = "TAGHIAN"
baseline = False
submode=False

def replaceSpaces(label):
    return '_'.join(str(label).split())

metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'ReportID', 'Correct', 'Institution', 'DOBPlusX']

SIX_MONTHS = datetime.timedelta(365/2)

hueLabels = []
if MODE == "TAGHIAN":
  reportTextKey = "Report_Text_Segmented"

  # diagnoses = [
  #   'PositiveLN','ITC', 'PR',  'Her2Fish', 'ER', 'ECE', 'LVI', 'BVI',
  #   'ILC', 'ALH','DCIS', 'LCIS', 'IDC',
  #   'ADH', 'BreastSide', 'FlatEpithelial', 'BluntAdenosis',
  #   'LobularNeoplasia','BiopsyType',
  #   'ADH_DCIS', 'Phyllodes',
  #   'CancerNOS',
  #   'InvasiveSuspicious',
  #   'InsituNOS',
  #   'CancerInvInsituNOS',
  #   'SuspiciousForPhyllodes',
  #   'CancerSuspicious', 'TubularCancer', 'Papill',
  #   'CancerInvasive', 'CancerInvNOS', 'NodeTissue', 'CancerNotOfBreastOrigin', 'PathologyType',
  #   "Organ", "Her2", "Her2_IHC" ]

  keys = {
      'Report_Text_Segmented': [],
      'Report_Text': [],
      'Report_Date_Time': [],
      'Owner': [],
      'Institution': [],
      'MRN': [],
      'EMPI': [],
      'ReportID': [],
      'Organ': ['0', '1'],
      'PathologyType': ['Anatomic', 'Cytology'],
      'BiopsyType': ['Core', 'Excision', 'Other', '9'],
      'BreastSide': ['l', 'r'],
      'CancerSuspicious': ['0', '1'],
      'InvasiveSuspicious': ['0', '1'],
      'CancerInvInsituNOS': ['0', '1'],
      'InsituNOS': ['0', '1'],
      'IDC': ['0', '1'],
      'ILC': ['0', '1'],
      'TubularCancer': ['0', '1'],
      'CancerInvasive': ['0', '1'],
      'CancerInvNOS': ['0', '1'],
      'CancerNotOfBreastOrigin': ['0', '1'], 
      'CancerNOS': ['0', '1'],
      'DCIS': ['0', '1'],
      'ER': ['0', '1', '9'],
      'PR': ['0', '1', '9'],
      'Her2': ['0', '1', '9', '999'],
      'Her2Fish': ['0', '1', '9'],
      'Her2_IHC': ['0', '1+', '2+', '3+', '4+', '9'],
      'PositiveLN': ['0', '1'],
      'ECE': ['0', '1', '9'],
      'ITC': ['0', '1'], 
      'BVI': ['0', '1', '9'],
      'LVI': ['0', '1', '9'],
      'LCIS': ['0', '1'],
      'LobularNeoplasia': ['0', '1'],
      'ALH': ['0', '1'],
      'ADH_DCIS': ['0', '1'],
      'ADH': ['0', '1'],
      'FlatEpithelial': ['0', '1'],
      'Phyllodes': ['0', '1'],
      'SuspiciousForPhyllodes': ['0', '1'],
      'Papill': ['0', '1'],
      'BluntAdenosis': ['0', '1'],
      'NodeTissue': ['0', '1'],
      'filename': [],
      'batchID': [],
      'train': [],
      'validated': [],
    }

  diagnoses = {k:keys[k] for k in keys if len(keys[k]) > 0}

  post_diagnoses = {k:diagnoses[k] for k in diagnoses}
  post_diagnoses['cancer'] = ['0', '1']
  post_diagnoses['atypia'] = ['0', '1']
  post_diagnoses['ER_Intensity'] = ['0', '1', '2', '3', '9']
  post_diagnoses['PR_Intensity'] = ['0', '1', '2', '3', '9']

  defaultLabelDict = {k:post_diagnoses[k][0] for k in post_diagnoses}

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

  # key_order = ['Report_Text_Segmented' , 'Report_Text', "Organ", "PathologyType",'BreastSide' ,'CancerSuspicious' ,'InvasiveSuspicious',
  # 'CancerInvInsituNOS','InsituNOS','IDC','ILC','TubularCancer', 'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin', 
  # 'DCIS', 'cancer', 'ER', "ER_Intensity", 'PR',"PR_Intensity", "Her2", 'Her2Fish',  "Her2_IHC", 'PositiveLN','ECE','ITC' ,'BVI', 'LVI'  ,'LCIS',
  # 'LobularNeoplasia','ALH', 'ADH_DCIS', 'ADH' ,'FlatEpithelial' ,'Phyllodes',
  # 'SuspiciousForPhyllodes', 'Papill']

  markers = [ 'ER', "ER_Intensity", 'PR',"PR_Intensity", "Her2", 'Her2Fish',  "Her2_IHC",  'Are there Positive LN?','ECE','ITC' ,'BVI', 'LVI']
  groupings = {
      'atypias': [k for k in ['Report_Text_Segmented', 'BreastSide', 'LCIS', 'LobularNeoplasia','ALH', 'ADH_DCIS', 'ADH' ,'FlatEpithelial'] if k in keys],
      'cancersSansMarkers': [k for k in ['Report_Text_Segmented', 'BreastSide' ,'CancerSuspicious' ,'InvasiveSuspicious', 'CancerInvInsituNOS','InsituNOS','InvasiveNOS','IDC','ILC','TubularCancer', 'DCIS'] if k in keys],
      'phyllodesAndPapil':[k for k in ['Report_Text_Segmented', 'BreastSide', 'Phyllodes', 'SuspiciousForPhyllodes','Papill'] if k in keys],
      'allNN': ['Report_Text_Segmented']+[k for k in nn_diagnoses],
      'allNNSansMarkers': ['Report_Text_Segmented']+[k for k in nn_diagnoses if k not in markers],
  }

  # diagToConventionDict = {
  #   'PositiveLN': 'PositiveLN' ,
  #   'ITC':'ITC',
  #   'Her2':'Her2',
  #   'Her2Fish':'Her2Fish',
  #   'Her2_IHC':'Her2_IHC',
  #   'ILC':'ILC',
  #   'ALH':'ALH',
  #   'DCIS':'DCIS',
  #   'LCIS':'LCIS',
  #   'IDC':'IDC',
  #   'ADH' :'ADH',
  #   'BreastSide':'BreastSide',
  #   'FlatEpithelial':'FlatEpithelial',
  #   'BluntAdenosis':'BluntAdenosis',
  #   'LobularNeoplasia':'LobularNeoplasia',
  #   'ADH_DCIS': 'ADH_DCIS',
  #   'Phyllodes':'Phyllodes',
  #   'CancerNOS':'CancerNOS',
  #   'InvasiveSuspicious': 'InvasiveSuspicious',
  #   'InsituNOS':'InsituNOS',
  #   'CancerInvInsituNOS': 'CancerInvInsituNOS',
  #   'SuspiciousForPhyllodes':'SuspiciousForPhyllodes',
  #   'CancerSuspicious':'CancerSuspicious',
  #   'TubularCancer':'TubularCancer',
  #   'Papill':'Papill',
  #   'CancerInvasive':'CancerInvasive',
  #   'CancerInvNOS':'CancerInvNOS',
  #   'CancerNotOfBreastOrigin':'CancerNotOfBreastOrigin',
  #   "Organ":"Organ",
  #   "Cytology":"Cytology"
  # }
  # for diag in diagnoses:
  #   if not diag in diagToConventionDict:
  #     diagToConventionDict[diag] = diag

  # conventionToDiagDict = {}
  # for diag in diagnoses:
  #   if diag in diagToConventionDict:
  #     conventionToDiagDict[ diagToConventionDict[diag] ] = diag
  #   else:
  #     conventionToDiagDict[ diag ] = diag

  # key_order_convention = [ diagToConventionDict[k] if k in diagToConventionDict else k for k in key_order]

  # if baseline:
  #   diagnoses = [
  #   'ILC', 'ALH','DCIS', 'LCIS', 'IDC',
  #   'ADH', 'BreastSide', 'FlatEpithelial','BluntAdenosis',
  #   'LobularNeoplasia']


  redRawDBPath = '../reportDB+red+clean.p'

  # defaultLabelDict = { 'PositiveLN': '0', 'Type of sampled LN (choice=None)':'Unchecked', 'ITC':'0', 'PR':'9',
  #     'BiopsyType':'9', 'Her2Fish':'9', 'ER': '9', 'ECE':'0',
  #     'LVI': '9', 'BVI': '9', 'TumorGrade': '9', 'DCIS':'0', 'LCIS':'0', 'IDC':'0', 'ILC':'0',
  #     'ALH':'0', 'ADH':'0', 'BreastSide':'r', 'FlatEpithelial':'0','BluntAdenosis':'0', 'LobularNeoplasia': '0',
  #     'cancer':'0', 'atypia':'0',
  #     'OncotypeScore':'Low_risk',
  #     'ADH_DCIS':'0', 'Phyllodes':'0', 'CancerNOS':'0', 'InvasiveSuspicious':'0', 'InsituNOS':'0', 'CancerInvInsituNOS':'0',
  #     'SuspiciousForPhyllodes':'0', 'CancerSuspicious':'0', 'TubularCancer':'0',
  #     'Papill':'0',
  #     'CancerInvasive':'0',
  #     'CancerInvNOS':'0',
  #     'NodeTissue':'0', #'Node_x0020_tissue'
  #     'CancerNotOfBreastOrigin':'0', #CancerNotOfBreastOrigin
  #     'PathologyType':'1',
  #     "Organ":'0',
  #     "ER_Intensity":'9', "PR_Intensity":'9', "Her2":'9', "Her2_IHC":'9'
  #     }


  # constantValidLabelDict = {'PositiveLN': ['1', '0'],
  #   'ER': ['1','0','9'],
  #   'Her2Fish': ['1', '0','9'],
  #   'ITC': ['1', '0'],
  #   'PR': ['9', '0', '1'],
  #   "ER_Intensity":['9', '0', '1', '2','3'], 
  #   "PR_Intensity":['9', '0', '1', '2','3'], 
  #   "Her2":['9','0','1','999'], 
  #   "Her2_IHC":['9','0','1','2','3','4'],
  #   'BiopsyType': ['Core', 'Excision', '9', 'Other'],
  #   'ECE': ['1', '0', '9'],
  #   'LVI': ['1', '0', '9'],
  #   'BVI': ['1', '0', '9'],
  #   'TumorGrade': ['Well_differentiated_(grade_I)', 'Moderate_(grade_II)', 'Poor_(grade_III)_Undifferentiated', '9'],
  #   'DCIS':  ['1','0'],
  #   'LCIS': ['1','0'],
  #   'IDC': ['1','0'],
  #   'ILC': ['1','0'],
  #   'ALH': ['1','0'],
  #   'ADH': ['1','0'],
  #   'Papill': ['1','0'],
  #   'FlatEpithelial':['1','0'],
  #   'BluntAdenosis':['1','0'],
  #   'LobularNeoplasia':['1','0'],
  #   'cancer': ['1','0'],
  #   'atypia': ['1','0'],
  #   'BreastSide': ['r', 'l'],
  #   'OncotypeScore': ['Low_risk', 'High_risk'],
  #   'ADH_DCIS': ['1','0'],
  #   'Phyllodes': ['1','0'],
  #   'CancerNOS': ['1','0'],
  #   'InvasiveSuspicious': ['1','0'],
  #   'InsituNOS': ['1','0'],
  #   'CancerInvInsituNOS': ['1','0'],
  #   'SuspiciousForPhyllodes': ['1','0'],
  #   'CancerSuspicious':['1','0'],
  #   'TubularCancer':['1','0'],
  #   'CancerInvasive':['1','0'],
  #   'CancerInvNOS':['1','0'],
  #   'NodeTissue':['1','0'], #'Node_x0020_tissue'
  #   'CancerNotOfBreastOrigin':['1','0'], #CancerNotOfBreastOrigin
  #   'PathologyType':['1','0'],  #'Pathology_x0020_type'
  #   "Organ":['0','1']
  # }

  # sqlToLabelDict = {'PositiveLN': {'1':'1','0':'0'},
  #   'ER': {'1':'1','0':'0','9':'9'},
  #   'Her2Fish': {'1':'1','0':'0','9':'9'},
  #   'ITC': {'1':'1','0':'0'},
  #   'PR': {'9':'9','0':'0','1':'1'},
  #   'ECE': {'1':'1','0':'0','9':'9'},
  #   'LVI': {'1':'1','0':'0','9':'9'},
  #   'BVI': {'1':'1','0':'0','9':'9'},
  #   "ER_Intensity":{'9':'9','0':'0','1':'1','2':'2','3':'3'}, 
  #   "PR_Intensity":{'9':'9','0':'0','1':'1','2':'2','3':'3'}, 
  #   "Her2":{'9':'9','0':'0','1':'1','999':'999'}, 
  #   "Her2_IHC":{'9':'9','0':'0','1':'1','2':'2','3':'3','4':'4'},
  #   'DCIS':  {'1':'1','0':'0'},
  #   'LCIS': {'1':'1','0':'0'},
  #   'IDC': {'1':'1','0':'0'},
  #   'ILC': {'1':'1','0':'0'},
  #   'ALH': {'1':'1','0':'0'},
  #   'ADH': {'1':'1','0':'0'},
  #   'Papill': {'1':'1','0':'0'},
  #   'FlatEpithelial':{'1':'1','0':'0'},
  #   'BluntAdenosis':{'1':'1','0':'0'},
  #   'LobularNeoplasia':{'1':'1','0':'0'},
  #   'cancer': {'1':'1','0':'0'},
  #   'atypia': {'1':'1','0':'0'},
  #   'BreastSide': {'r':'r', 'l':'l'},
  #   'ADH_DCIS': {'1':'1','0':'0'},
  #   'Phyllodes': {'1':'1','0':'0'},
  #   'CancerNOS': {'1':'1','0':'0'},
  #   'InvasiveSuspicious': {'1':'1','0':'0'},
  #   'InsituNOS': {'1':'1','0':'0'},
  #   'CancerInvInsituNOS': {'1':'1','0':'0'},
  #   'SuspiciousForPhyllodes': {'1':'1','0':'0'},
  #   'CancerSuspicious':{'1':'1','0':'0'},
  #   'TubularCancer':{'1':'1','0':'0'},
  #   'CancerInvasive':{'1':'1','0':'0'},
  #   'CancerInvNOS':{'1':'1','0':'0'},
  #   'NodeTissue':{'1':'1','0':'0'}, #'Node_x0020_tissue'
  #   'CancerNotOfBreastOrigin':{'1':'1','0':'0'}, #CancerNotOfBreastOrigin
  #   'PathologyType':{'1':'1','0':'0'},  #'Pathology_x0020_type'
  #   "Organ":{'0':'0','1':'1'}
  # }


  # gregToAccessDbDict = {
  #   'Report_Date_Time':'Report_Date_Time',
  #   'PositiveLN':'PositiveLN',
  #   'ITC':'ITC',
  #   'Her2':'Her2',
  #   'Her2_IHC':'Her2_IHC',
  #   'Her2Fish':'Her2Fish',
  #   'ILC':'ILC',
  #   'ALH':'ALH',
  #   'DCIS':'DCIS',
  #   'LCIS':'LCIS',
  #   'IDC':'IDC',
  #   'ADH':'ADH',
  #   'BreastSide':'BreastSide',
  #   'FlatEpithelial':'FlatEpithelial',
  #   'BluntAdenosis':'BluntAdenosis',
  #   'LobularNeoplasia':'LobularNeoplasia',
  #   'ADH_DCIS':'ADH_DCIS',
  #   'Phyllodes':'Phyllodes',
  #   'CancerNOS':'CancerNOS',
  #   'InvasiveSuspicious':'InvasiveSuspicious',
  #   'InsituNOS':'InsituNOS',
  #   'CancerInvInsituNOS':'CancerInvInsituNOS',
  #   'SuspiciousForPhyllodes':'SuspiciousForPhyllodes',
  #   'CancerSuspicious':'CancerSuspicious',
  #   'TubularCancer':'TubularCancer',
  #   'Papill':'Papill',
  #   'CancerInvasive':'CancerInvasive',
  #   'CancerInvNOS':'CancerInvNOS',
  #   'CancerNotOfBreastOrigin':'CancerNotOfBreastOrigin',
  #   'filename':'filename',
  #   'PR':'PR',
  #   'ECE':'ECE',
  #   'validated':'validated',
  #   'Report_Text':'Report_Text',
  #   'Institution':'Institution',
  #   'BiopsyType':'BiopsyType',
  #   'Organ':'Organ',
  #   'batchID':'batchID',
  #   'MRN':'MRN',
  #   'ReportID':'ReportID',
  #   'ER':'ER',
  #   'Owner':'Owner',
  #   'BVI':'BVI',
  #   'NodeTissue':'NodeTissue',
  #   'cancer':'cancer',
  #   'PathologyType':'PathologyType',
  #   'Report_Text_Segmented':'Report_Text_Segmented',
  #   'LVI':'LVI',
  #   'EMPI':'EMPI',
  #   "ER_Intensity":"ER_Intensity",
  #   "PR_Intensity":"PR_Intensity",
  #   "Her2":"Her2",
  #   "Her2_IHC":"Her2_IHC",
  #   "train": "train"
  #   }

  # AccessDbToGregDict = {v: k for k, v in gregToAccessDbDict.items()}
  # accessDbKeys = AccessDbToGregDict.keys()
  reportsTableName = "reports"
  reportsNoBreastTableName = "nonbreastReports"
  backupTableName = "backup"
  backupNoBreastTableName = "nonbreastBackup"



  # gregToMongoDict = {       
  #               'PositiveLN':'PositiveLN',
  #               'Her2':'Her2',
  #               'Her2Fish':'Her2Fish',
  #               'Her2_IHC':'Her2_IHC',
  #               'ITC':'ITC',
  #               'ILC':'ILC',
  #               'ALH':'ALH',
  #               'DCIS':'DCIS',
  #               'LCIS':'LCIS',
  #               'IDC':'IDC',
  #               'ADH':'ADH',
  #               'BreastSide':'BreastSide',
  #               'FlatEpithelial':'FlatEpithelial',
  #               'BluntAdenosis':'BluntAdenosis',
  #               'LobularNeoplasia':'LobularNeoplasia',
  #               'ADH_DCIS':'ADH_DCIS',
  #               'Phyllodes':'Phyllodes',
  #               'CancerNOS':'CancerNOS',
  #               'InvasiveSuspicious':'InvasiveSuspicious',
  #               'InsituNOS':'InsituNOS',
  #               'CancerInvInsituNOS':'CancerInvInsituNOS',
  #               'SuspiciousForPhyllodes':'SuspiciousForPhyllodes',
  #               'CancerSuspicious':'CancerSuspicious',
  #               'TubularCancer':'TubularCancer',
  #               'Papill':'Papill',
  #               'CancerInvasive':'CancerInvasive',
  #               'CancerInvNOS':'CancerInvNOS',
  #               'OncotypeScore':'OncotypeScore'  }


 # JSONLabelNameDict = diagToConventionDict




#  labelsForEpisodes = diagnoses



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
