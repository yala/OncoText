import datetime
import oncotext.utils.parsing as parsing
import os
import pdb
import copy

class Args(object):
    def __init__(self, config_dict):
        self.__dict__.update(config_dict)


class Config(object):
    DEBUG = True
    HOMEDIR = '/home/nlp/'
    PATHOLOGYDIR = os.path.join(HOMEDIR, 'pathology/')
    PICKLEDIR = os.path.join(PATHOLOGYDIR, "pickle_files")
    DROPBOXDIR = os.path.join(HOMEDIR,'Dropbox (Partners HealthCare)/NLP_Extraction/')
    EVALDIR = os.path.join(DROPBOXDIR,'GoldSets/')
    PARSINGDIR = os.path.join(DROPBOXDIR,'ForParsing/')
    TRAININGDIR = os.path.join(DROPBOXDIR,'ForTraining/')
    RESULTSDIR = os.path.join(DROPBOXDIR,'NLP_Results/')


    DB_TRAIN_PATH = os.path.join(PICKLEDIR, "reportDBAPI_train.p")
    DB_BASE_PATH = os.path.join(PICKLEDIR, "pickle_files/reportDB_base_train.p")
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

    columnKeys = parsing.parse_XLS( os.path.join(DROPBOXDIR,'SQL_KeysAndValues.xlsx'))

    diagnoses = {k: v for k, v in columnKeys.items() if len(v) > 0}
    post_diagnoses = copy.deepcopy(diagnoses)
    post_diagnoses['cancer'] = ['0', '1']
    post_diagnoses['atypia'] = ['0', '1']
    post_diagnoses['ER_Intensity'] = ['0', '1', '2', '3', '9']
    post_diagnoses['PR_Intensity'] = ['0', '1', '2', '3', '9']

    defaultLabelDict = {k: v[0] for k, v in post_diagnoses.items()}

    cancers = ['ILC', 'DCIS', 'IDC', 'TubularCancer', 'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin']

    atypias = ['ALH', 'ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia']

    markers = ['ER', "ER_Intensity", 'PR', "PR_Intensity", "Her2", 'Her2Fish', "Her2_IHC", 'Are there Positive LN?', 'ECE', 'ITC', 'BVI', 'LVI']

    ATYPIA_TABLES = [("allFEAsTable", cancers, ["FlatEpithelial"], False ),
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
        'embedding': 'pathology',
        'num_layers': 1,
        'filters': '3,4,5',
        'filter_num': 100,
        'epochs': 1,
        'patience': 5,
        'snapshot': None,
        'objective':'cross_entropy',
        'num_gpus ': 1,
        'results_path': 'snapshot/oncotext_{}.pt',
        'train_split': .80
    }


    rationale_net_args = Args(RATIONALE_NET_CONFIG)
