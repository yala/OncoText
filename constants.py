import datetime
from openpyxl import load_workbook
from collections import OrderedDict

MODE = "TAGHIAN"
baseline = False
submode = False


def replaceSpaces(label):
    return '_'.join(str(label).split())


def parseKeys(inp):
    wb = load_workbook(inp)
    sheet = wb.active
    data = OrderedDict()
    for row in sheet.rows:
        values = [str(cell.value) for cell in row if cell.value is not None]
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

hueLabels = []
if MODE == "TAGHIAN":
    reportTextKey = "Report_Text_Segmented"

    columnKeys = parseKeys(DROPBOXDIR + 'SQL_KeysAndValues.xlsx')

    diagnoses = {k: columnKeys[k] for k in columnKeys if len(columnKeys[k]) > 0}

    post_diagnoses = {k: diagnoses[k] for k in diagnoses}
    post_diagnoses['cancer'] = ['0', '1']
    post_diagnoses['atypia'] = ['0', '1']
    post_diagnoses['ER_Intensity'] = ['0', '1', '2', '3', '9']
    post_diagnoses['PR_Intensity'] = ['0', '1', '2', '3', '9']

    defaultLabelDict = {k: post_diagnoses[k][0] for k in post_diagnoses}

    boostexer_diagnoses = ["CancerInvInsituNOS", "CancerNOS", "BiopsyType", "Her2", "Her2_IHC", "ITC", "PR", "Her2Fish", "ER", "ECE", "LVI", "BVI", "PathologyType", "Organ", "CancerInvasive", "CancerInvNOS", "NodeTissue", "CancerNotOfBreastOrigin", "BluntAdenosis", "PositiveLN"]
    boostexer_diagnoses = [d for d in boostexer_diagnoses if d in diagnoses]
    nn_diagnoses = [d for d in diagnoses if d not in boostexer_diagnoses]

    const_cancers = ['ILC', 'DCIS', 'IDC', 'TubularCancer', 'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin']

    const_atypias = ['ALH', 'ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia']

    markers = ['ER', "ER_Intensity", 'PR', "PR_Intensity", "Her2", 'Her2Fish', "Her2_IHC", 'Are there Positive LN?', 'ECE', 'ITC', 'BVI', 'LVI']
    groupings = {
        'atypias': [k for k in ['Report_Text_Segmented', 'BreastSide', 'LCIS', 'LobularNeoplasia', 'ALH', 'ADH_DCIS', 'ADH', 'FlatEpithelial'] if k in columnKeys],
        'cancersSansMarkers': [k for k in ['Report_Text_Segmented', 'BreastSide', 'CancerSuspicious', 'InvasiveSuspicious', 'CancerInvInsituNOS', 'InsituNOS', 'InvasiveNOS', 'IDC', 'ILC', 'TubularCancer', 'DCIS'] if k in columnKeys],
        'phyllodesAndPapil': [k for k in ['Report_Text_Segmented', 'BreastSide', 'Phyllodes', 'SuspiciousForPhyllodes', 'Papill'] if k in columnKeys],
        'allNN': ['Report_Text_Segmented'] + [k for k in nn_diagnoses],
        'allNNSansMarkers': ['Report_Text_Segmented'] + [k for k in nn_diagnoses if k not in markers],
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
