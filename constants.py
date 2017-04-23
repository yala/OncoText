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

  lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5}
  maxedOutDictToIndx = {'Oncotype score':-1, 'Oncotype date':-1}
  maxedOutList = ['Oncotype score', 'Oncotype date']
  externalList = ['TumorGrade', 'Red SuspiciousForPhyllodes', 'Red Phylodes']


  diagnoses = [
    'Are there positive LN?','ITC ', 'PR',  'Her2 (Fish)', 'ER', 'ECE', 'LVI', 'BVI',
    'Red ILC', 'Red ALH','Red DCIS', 'Red LCIS', 'Red IDC',
    'Red ADH', 'Red BreastSide', 'Red FlatEpithelial', 'Red BluntAdenosis',
    'Red LobularNeoplasia','BiopsyType',
    'Red ADH_DCIS', 'Red Phylodes',
    'Red CancerNOS',
    'Red InvasiveSuspicious',
    'Red InsituNOS',
    'Red CancerInvInsituNOS',
    'Red SuspiciousForPhyllodes',
    'Red CancerSuspicious', 'Red TubularCancer', 'Red Papill',
    'Red CancerInvasive', 'Red CancerInvNOS', 'NodeTissue', 'CancerNotOfBreastOrigin', 'PathologyType',
    "Organ"  ]

  boostexer_diagnoses = ['ITC ', 'Red CancerNOS', 'BiopsyType', 'Red BluntAdenosis',
  'Red CancerInvInsituNOS', 'Are there positive LN?', 'PR', 'Her2 (Fish)', 'ER', 'ECE', 'LVI', 'BVI',
  'Red CancerInvasive', 'Red CancerInvNOS', 'NodeTissue', 'CancerNotOfBreastOrigin', 'PathologyType',
  "Organ",
  ]

  feb_new_diagnoses = ['Red CancerInvasive', 'Red CancerInvNOS', 'NodeTissue', 'CancerNotOfBreastOrigin', 'PathologyType', "Organ"
  ]

  nn_diagnoses = [d for d in diagnoses if not d in boostexer_diagnoses]

  const_cancers = [
  'Red ILC','Red DCIS', 'Red IDC',
  'Red CancerNOS', 'Red InsituNOS', 'Red CancerInvInsituNOS', 'Red TubularCancer',
  'Red CancerInvasive', 'Red CancerInvNOS', 'CancerNotOfBreastOrigin'
  ]

  const_cancers_mod = [
    'ILC','DCIS', 'IDC',
    'CancerNOS', 'InsituNOS', 'CancerInvInsituNOS', 'TubularCancer',
    'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin'
    ]

  const_atypias = [
  'Red ALH','Red ADH', 'Red FlatEpithelial', 'Red LCIS', 'Red ADH_DCIS', 'Red LobularNeoplasia'
  ]

  const_atypias_mod = [
  'ALH','ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia'
  ]

  key_order = ['Report_Text_Segmented' , "Organ", "PathologyType",'Red BreastSide' ,'Red CancerSuspicious' ,'Red InvasiveSuspicious',
  'Red CancerInvInsituNOS','Red InsituNOS','Red IDC','Red ILC','Red TubularCancer', 'Red CancerInvasive', 'Red CancerInvNOS', 'CancerNotOfBreastOrigin'
  'Red DCIS', 'ER', 'PR', 'Her2 (Fish)', 'Are there positive LN?','ECE','ITC ' ,'BVI', 'LVI'  ,'Red LCIS',
  'Red LobularNeoplasia','Red ALH', 'Red ADH_DCIS', 'Red ADH' ,'Red FlatEpithelial' ,'Red Phylodes',
  'Red SuspiciousForPhyllodes', 'Red Papill']

  markers = [ 'ER', 'PR', 'Her2 (Fish)',  'Are there Positive LN?','ECE','ITC' ,'BVI', 'LVI']
  groupings = {
    "atypias": [ 'Report_Text_Segmented', 'Red BreastSide', 'Red LCIS',
        'Red LobularNeoplasia','Red ALH', 'Red ADH_DCIS', 'Red ADH' ,'Red FlatEpithelial'],
    # 'cancers': ['Report_Text_Segmented' ,'Red BreastSide' ,'Red CancerSuspicious' ,'Red InvasiveSuspicious',
    #     'Red CancerInvInsituNOS','Red InsituNOS','Red InvasiveNOS','Red IDC','Red ILC','Red TubularCancer',
    #     'Red DCIS', 'ER', 'PR', 'Her2 (Fish)',  'Are there Positive LN?','ECE','ITC' ,'BVI', 'LVI'],
    #'markers': markers,
    'cancersSansMarkers': ['Report_Text_Segmented' ,'Red BreastSide' ,'Red CancerSuspicious' ,'Red InvasiveSuspicious',
        'Red CancerInvInsituNOS','Red InsituNOS','Red InvasiveNOS','Red IDC','Red ILC','Red TubularCancer',
        'Red DCIS'],
    'phyllodesAndPapil':[ 'Report_Text_Segmented' ,'Red BreastSide', 'Red Phylodes', 'Red SuspiciousForPhyllodes',
       'Red Papill'],
     'allNN': [k for k in key_order if k in diagnoses and not k in boostexer_diagnoses],
     'allNNSansMarkers': [k for k in key_order if not k in markers and k in diagnoses and not k in boostexer_diagnoses],
  }

  diagToConventionDict = {
    "Red DCIS": 'DCIS',
    'Are there positive LN?': 'Are there positive LN?' ,
    'ITC ':'ITC',
    'Her2 (Fish)':'Her2',
    'Red ILC':'ILC',
    'Red ALH':'ALH',
    'Red DCIS':'DCIS',
    'Red LCIS':'LCIS',
    'Red IDC':'IDC',
    'Red ADH' :'ADH',
    'Red BreastSide':'BreastSide',
    'Red FlatEpithelial':'FlatEpithelial',
    'Red BluntAdenosis':'BluntAdenosis',
    'Red LobularNeoplasia':'LobularNeoplasia',
    'Red ADH_DCIS': 'ADH_DCIS',
    'Red Phylodes':'Phylodes',
    'Red CancerNOS':'CancerNOS',
    'Red InvasiveSuspicious': 'InvasiveSuspicious',
    'Red InsituNOS':'InsituNOS',
    'Red CancerInvInsituNOS': 'CancerInvInsituNOS',
    'Red SuspiciousForPhyllodes':'SuspiciousForPhyllodes',
    'Red CancerSuspicious':'CancerSuspicious',
    'Red TubularCancer':'TubularCancer',
    'Red Papill':'Papill',
    'Red CancerInvasive':'CancerInvasive',
    'Red CancerInvNOS':'CancerInvNOS',
    'CancerNotOfBreastOrigin':'CancerNotOfBreastOrigin',
    "Organ":"Organ",
    "Cytology":"Cytology"
  }
  for diag in diagnoses:
    if not diag in diagToConventionDict:
      diagToConventionDict[diag] = diag

  conventionToDiagDict = {}
  for diag in diagnoses:
    if diag in diagToConventionDict:
      conventionToDiagDict[ diagToConventionDict[diag] ] = diag
    else:
      conventionToDiagDict[ diag ] = diag

  key_order_convention = [ diagToConventionDict[k] if k in diagToConventionDict else k for k in key_order]

  if baseline:
    diagnoses = [
    'Red ILC', 'Red ALH','Red DCIS', 'Red LCIS', 'Red IDC',
    'Red ADH', 'Red BreastSide', 'Red FlatEpithelial','Red BluntAdenosis',
    'Red LobularNeoplasia']



  HueAnotationSource= ['DCIS', 'LCIS', 'IDC', 'ILC', 'ALH', 'ADH', 'BreastSide', 'FlatEpithelial', 'BluntAdenosis', 'LobularNeoplasia',
  'ADH_DCIS', 'Phylodes', 'CancerNOS', 'InvasiveSuspicious', 'InsituNOS', 'CancerInvInsituNOS','CancerSuspicious',
  'TubularCancer' ]
  diagSkip = ['ALH', 'ILC']
  BiopAnotationSource= [a + " Biop" for a in HueAnotationSource  if not a in diagSkip]
  SurgAnotationSource= [a + " Surg" for a in HueAnotationSource  if not a in diagSkip]


  MixedAnotations= ["Red "+d for d in HueAnotationSource]


  redRawDBPath = '../reportDB+red+clean.p'

  defaultLabelDict = { 'Are there positive LN?': 'No', 'Type of sampled LN (choice=None)':'Unchecked', 'ITC ':'No', 'PR':'NA',
      'BiopsyType':'NA', 'Her2 (Fish)':'NA', 'ER': 'NA', 'ECE':'No',
      'LVI': 'NA', 'BVI': 'NA', 'TumorGrade': 'NA', 'Red DCIS':'Absent', 'Red LCIS':'Absent', 'Red IDC':'Absent', 'Red ILC':'Absent',
      'Red ALH':'Absent', 'Red ADH':'Absent', 'Red BreastSide':'RIGHT', 'Red FlatEpithelial':'Absent','Red BluntAdenosis':'Absent', 'Red LobularNeoplasia': 'Absent',
      'cancer':'Absent', 'atypia':'Absent',
      'Oncotype score':'Low_risk',
      'Red ADH_DCIS':'Absent', 'Red Phylodes':'Absent', 'Red CancerNOS':'Absent', 'Red InvasiveSuspicious':'Absent', 'Red InsituNOS':'Absent', 'Red CancerInvInsituNOS':'Absent',
      'Red SuspiciousForPhyllodes':'Absent', 'Red CancerSuspicious':'Absent', 'Red TubularCancer':'Absent',
      'Red Papill':'Absent',
      'Red CancerInvasive':'Absent',
      'Red CancerInvNOS':'Absent',
      'NodeTissue':'Absent', #'Node_x0020_tissue'
      'CancerNotOfBreastOrigin':'Absent', #CancerNotOfBreastOrigin
      'PathologyType':'Anatomic',
      "Organ":"non-breast"
      }


  extractions = [u'Max Tumor Size', 'Non Sentinel LN (# Malignant)', 'Sentinel LN (# Sampled)']



  constantValidLabelDict = {'Are there positive LN?': ['Yes', 'No'],
    'ER': ['Positive','Negative','NA'],
    'Her2 (Fish)': ['Positive', 'Negative','NA'],
    'ITC ': ['Yes', 'No'],
    'PR': ['NA', 'Negative', 'Positive'],
    'BiopsyType': ['Core', 'Excision', 'NA', 'Other'],
    'ECE': ['Yes', 'No', 'NA'],
    'LVI': ['Yes', 'No', 'NA'],
    'BVI': ['Yes', 'No', 'NA'],
    'TumorGrade': ['Well_differentiated_(grade_I)', 'Moderate_(grade_II)', 'Poor_(grade_III)_Undifferentiated', 'NA'],
    'Red DCIS':  ['Present','Absent'],
    'Red LCIS': ['Present','Absent'],
    'Red IDC': ['Present','Absent'],
    'Red ILC': ['Present','Absent'],
    'Red ALH': ['Present','Absent'],
    'Red ADH': ['Present','Absent'],
    'Red Papill': ['Present','Absent'],
    'Red FlatEpithelial':['Present','Absent'],
    'Red BluntAdenosis':['Present','Absent'],
    'Red LobularNeoplasia':['Present','Absent'],
    'cancer': ['Present','Absent'],
    'atypia': ['Present','Absent'],
    'Red BreastSide': ['RIGHT', 'LEFT'],
    'Oncotype score': ['Low_risk', 'High_risk'],
    'Red ADH_DCIS': ['Present','Absent'],
    'Red Phylodes': ['Present','Absent'],
    'Red CancerNOS': ['Present','Absent'],
    'Red InvasiveSuspicious': ['Present','Absent'],
    'Red InsituNOS': ['Present','Absent'],
    'Red CancerInvInsituNOS': ['Present','Absent'],
    'Red SuspiciousForPhyllodes': ['Present','Absent'],
    'Red CancerSuspicious':['Present','Absent'],
    'Red TubularCancer':['Present','Absent'],

    'Red CancerInvasive':['Present','Absent'],
    'Red CancerInvNOS':['Present','Absent'],
    'NodeTissue':['Present','Absent'], #'Node_x0020_tissue'
    'CancerNotOfBreastOrigin':['Present','Absent'], #CancerNotOfBreastOrigin
    'PathologyType':['Anatomic','Cytology'],  #'Pathology_x0020_type'
    "Organ":["non-breast","breast"]
  }

  analysisLabelDict = {'Are there positive LN?': ['Yes', 'No'],
    'ER': ['NA', 'Negative', 'Positive'],
    'Her2 (Fish)': ['NA', 'Negative', 'Positive'],
    'ITC ': ['Yes', 'No'],
    'PR': ['NA', 'Negative', 'Positive'],
    'ECE': ['Yes', 'No'],
    'LVI': ['Yes', 'No', 'NA'],
    'BVI': ['Yes', 'No', 'NA'],
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
    'Red Papill': ['Present','Absent'],
    'Red BreastSide': ['RIGHT', 'LEFT'],
    'cancer': ['cancer','no_cancer'],
    'atypia': ['atypia','no_atypia'],
    'BiopsyType': ['Core', 'Excision', 'Other'],
    'Oncotype score': ['Low_risk', 'High_risk'],
    'Red ADH_DCIS': ['Present','Absent'],
    'Red Phylodes': ['Present','Absent'],
    'Red CancerNOS': ['Present','Absent'],
    'Red InvasiveSuspicious': ['Present','Absent'],
    'Red InsituNOS': ['Present','Absent'],
    'Red CancerInvInsituNOS': ['Present','Absent'],
    'Red SuspiciousForPhyllodes': ['Present', 'Absent'],
    'Red CancerSuspicious':['Present','Absent'],
    'Red TubularCancer':['Present','Absent'],
    "Organ":["non-breast","breast"]
    }




  gregToAccessDbDict = {
    'Report_Date_Time':'Report_Date_Time',
    'Are there positive LN?':'PositiveLN',
    'ITC':'ITC',
    'Her2':'Her2Fish',
    'ILC':'ILC',
    'ALH':'ALH',
    'DCIS':'DCIS',
    'LCIS':'LCIS',
    'IDC':'IDC',
    'ADH':'ADH',
    'BreastSide':'BreastSide',
    'FlatEpithelial':'FlatEpithelial',
    'BluntAdenosis':'BluntAdenosis',
    'LobularNeoplasia':'LobularNeoplasia',
    'ADH_DCIS':'ADH_DCIS',
    'Phylodes':'Phylodes',
    'CancerNOS':'CancerNOS',
    'InvasiveSuspicious':'InvasiveSuspicious',
    'InsituNOS':'InsituNOS',
    'CancerInvInsituNOS':'CancerInvInsituNOS',
    'SuspiciousForPhyllodes':'SuspiciousForPhyllodes',
    'CancerSuspicious':'CancerSuspicious',
    'TubularCancer':'TubularCancer',
    'Papill':'Papill',
    'CancerInvasive':'CancerInvasive',
    'CancerInvNOS':'CancerInvNOS',
    'CancerNotOfBreastOrigin':'CancerNotOfBreastOrigin',
    'filename':'filename',
    'PR':'PR',
    'ECE':'ECE',
    'validated':'validated',
    'Report_Text':'Report_Text',
    'Institution':'Institution',
    'BiopsyType':'BiopsyType',
    'Organ':'Organ',
    'batchID':'batchID',
    'MRN':'MRN',
    'ReportID':'ReportID',
    'ER':'ER',
    'Owner':'Owner',
    'BVI':'BVI',
    'NodeTissue':'NodeTissue',
    'cancer':'cancer',
    'PathologyType':'PathologyType',
    'Report_Text_Segmented':'Report_Text_Segmented',
    'LVI':'LVI',
    'EMPI':'EMPI'
    }

  AccessDbToGregDict = {v: k for k, v in gregToAccessDbDict.items()}
  accessDbKeys = AccessDbToGregDict.keys()
  reportsTableName = "reports"
  backupTableName = "backup"








  JSONLabelNameDict = diagToConventionDict




  labelsForEpisodes = diagnoses



  trainOutPath = "../boostexer/breast/taghian/red.data"
  testOutPath = "../boostexer/breast/taghian/red.test"
  devOutPath = "../boostexer/breast/taghian/red.dev"


  allDataStem = "../boostexer/breast/unlabled/red_all"


  cols = diagnoses + metaData + ['Report_Text_Segmented', 'Report_Text']

  outPath = "../reportDB+new.p"
  dataPath = "../rawBreastPathReport.p"

  episodePath = "../episodeDB+new.p"
  JSONReportPath = "../reportDB+red.json"
  JSONEpisodePath = "../episodeDB+red.json"
