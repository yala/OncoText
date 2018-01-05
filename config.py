import datetime
import medtext_ie.utils.parsing as parsing
import os

class Args(object):
    def __init__(self, config_dict):
        self.__dict__.update(config_dict)


class Config(object):

    HOMEDIR = '/home/nlp/'
    PATHOLOGYDIR = os.path.join(HOMEDIR, 'pathology/')
    PICKLEDIR = os.path.join(PATHOLOGYDIR, "pickle_files")
    DROPBOXDIR = os.path.join(HOMEDIR,'Dropbox (Partners HealthCare)/NLP_Extraction/')
    EVALDIR = os.path.join(DROPBOXDIR,'GoldSets/')
    PARSINGDIR = os.path.join(DROPBOXDIR,'ForParsing/')
    TRAININGDIR = os.path.join(DROPBOXDIR,'ForTraining/')
    RESULTSDIR = os.path.join(DROPBOXDIR,'NLP_Results/')


    DB_TRAIN_PATH = os.path.join(PICKLEDIR, "reportDBAPI_train.p")
    DB_BASE_PATH = os.path.join(PICKLEDIR, "reportDBAPI_train.p")
    DB_UNLABLED_PATH = os.path.join(PICKLEDIR, "reportDBAPI_test.p")
    DB_NON_BREAST_PATH = os.path.join(PICKLEDIR, "reportDBAPI_nonbreasts.p")

    HOST = "nlp.partners.org"
    FROM =  "nlp@nlp.partners.org"
    SUBJECT = "Pathology Parser Update!"
    EMAIL_LIST =  ["cyli@mgh.harvard.edu", "ayala@mgh.harvard.edu", "KSHUGHES@PARTNERS.ORG"]

    SQL_HOST = 'localhost'
    SQL_USER = 'root'
    SQL_PASSWD = 'nlpdb'
    SQL_DB = 'reports'
    BREAST_REPORT_TABLE = "reports"
    NOBREAST_REPORT_TABLE = "nonbreastReports"

    SIX_MONTHS = datetime.timedelta(365/2)

    RAW_REPORT_TEXT_KEY = "Report_Text"
    PREPROCESSED_REPORT_TEXT_KEY = "Report_Text_Segmented"
    REPORT_TIME_KEY = "Report_Date_Time"
    SIDE_KEY = "BreastSide"
    PATIENT_ID_KEY = "MRN"
    PRUNE_KEY = "Organ"


    columnKeys = parsing.parse_XLS(DROPBOXDIR + 'SQL_KeysAndValues.xlsx')

    diagnoses = {k: columnKeys[k] for k in columnKeys if len(columnKeys[k]) > 0}

    post_diagnoses = {k: diagnoses[k] for k in diagnoses}
    post_diagnoses['cancer'] = ['0', '1']
    post_diagnoses['atypia'] = ['0', '1']
    post_diagnoses['ER_Intensity'] = ['0', '1', '2', '3', '9']
    post_diagnoses['PR_Intensity'] = ['0', '1', '2', '3', '9']

    defaultLabelDict = {k: post_diagnoses[k][0] for k in post_diagnoses}

    cancers = ['ILC', 'DCIS', 'IDC', 'TubularCancer', 'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin']

    atypias = ['ALH', 'ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia']

    markers = ['ER', "ER_Intensity", 'PR', "PR_Intensity", "Her2", 'Her2Fish', "Her2_IHC", 'Are there Positive LN?', 'ECE', 'ITC', 'BVI', 'LVI']

    groupings = {
        'atypias': [k for k in ['Report_Text_Segmented', 'BreastSide', 'LCIS', 'LobularNeoplasia', 'ALH', 'ADH_DCIS', 'ADH', 'FlatEpithelial'] if k in columnKeys],
        'cancersSansMarkers': [k for k in ['Report_Text_Segmented', 'BreastSide', 'CancerSuspicious', 'InvasiveSuspicious', 'CancerInvInsituNOS', 'InsituNOS', 'InvasiveNOS', 'IDC', 'ILC', 'TubularCancer', 'DCIS'] if k in columnKeys],
        'phyllodesAndPapil': [k for k in ['Report_Text_Segmented', 'BreastSide', 'Phyllodes', 'SuspiciousForPhyllodes', 'Papill'] if k in columnKeys],
        'allNN': ['Report_Text_Segmented'] + [k for k in nn_diagnoses],
        'allNNSansMarkers': ['Report_Text_Segmented'] + [k for k in nn_diagnoses if k not in markers],
    }

    ATYPIA_TABLES = [("allFEAsTable", cancers, ["FlatEpithelial"], False )
                     ("allADHsTable", cancers, ['ADH'], False),
                     ("allAtypiaTable", cancers, atypias, False),
                     ("allAtypia2010Table", cancers, atypias, True),
                     ("allCancersTable", [], cancers, False)]

    RATIONALE_NET_CONFIG = {
        'cuda': False,
        'dropout': .1,
        'init_lr': 0.0001,
        'model_form': 'cnn',
        'hidden_dim': 100,
        'dataset': 'pathology_oncotext',
        'num_layers': 1,
        'filters': '3,4,5',
        'filter_num': 100,,
        'epochs': 1,
        'patience': 5,
        'snapshot': None,
        'objective':'cross_entropy',
        'num_gpus ': 1,
        'results_path': 'snapshot/oncotext_{}.pt',
    }

    rationale_net_args = Args(RATIONALE_NET_CONFIG)
