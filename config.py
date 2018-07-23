import datetime
import oncotext.utils.parsing as parsing
import os
import pdb
import copy
import pickle

class Args(object):
    def __init__(self, config_dict):
        self.__dict__.update(config_dict)


class Config(object):
    PORT = 3000
    DEFAULT_USERNAME = 'default'
    DEFAULT_ORGAN = 'Meta'
    META_KEY = 'Meta'
    
    PICKLE_DIR = os.environ['PICKLE_DIR']
    SNAPSHOT_DIR = os.environ['SNAPSHOT_DIR']

    DB_TRAIN_PATH = os.path.join(PICKLE_DIR, "reportDBAPI_train.p")
    DB_BASE_PATH = os.path.join(PICKLE_DIR, "reportDB_base_train.p")
    DB_UNLABLED_PATH = os.path.join(PICKLE_DIR, "reportDBAPI_test.p")
    DB_NON_BREAST_PATH = os.path.join(PICKLE_DIR, "reportDBAPI_nonbreasts.p")
    EMBEDDING_PATH = os.path.join(PICKLE_DIR, "hash_embeddings.p")

    if not os.path.exists(PICKLE_DIR):
        os.makedirs(PICKLE_DIR)
    if not os.path.exists(DB_TRAIN_PATH):
        pickle.dump({}, open(DB_TRAIN_PATH, 'wb'))
    if not os.path.exists(DB_BASE_PATH):
        pickle.dump([], open(DB_BASE_PATH,'wb'))
    if not os.path.exists(DB_UNLABLED_PATH):
        pickle.dump({}, open(DB_UNLABLED_PATH, 'wb'))
    if not os.path.exists(DB_NON_BREAST_PATH):
        pickle.dump({}, open(DB_NON_BREAST_PATH, 'wb'))

    SIX_MONTHS = datetime.timedelta(365/2)

    RAW_REPORT_TEXT_KEY = "Report_Text"
    PREPROCESSED_REPORT_TEXT_KEY = "Report_Text_Segmented"
    REPORT_TIME_KEY = "Report_Date_Time"
    SIDE_KEY = "BreastSide"
    SEGMENT_ID_KEY = "SegmentID"
    SEGMENT_TYPE_KEY = "SegmentType"
    PATIENT_ID_KEY = "EMPI"
    PRUNE_KEY = "OrganBreast"
    PRUNE_AFTER_PREDICT = False

    COLUMN_KEYS = parsing.parse_XLS( os.environ['CONFIG_XLSX'])

    DIAGNOSES = {o: {} for o in COLUMN_KEYS.keys()}
    for organ in DIAGNOSES:
        DIAGNOSES[organ] = {k: v for k, v in COLUMN_KEYS[organ].items() if len(v) > 0}
    post_diagnoses = copy.deepcopy(DIAGNOSES)
    post_diagnoses['OrganBreast']['cancer'] = ['0', '1']
    post_diagnoses['OrganBreast']['atypia'] = ['0', '1']
    post_diagnoses['OrganBreast']['her2'] = ['0', '1', '9']
    post_diagnoses['OrganBreast']['ER_Intensity'] = ['0', '1', '2', '3', '9']
    post_diagnoses['OrganBreast']['PR_Intensity'] = ['0', '1', '2', '3', '9']
    POST_DIAGNOSES = post_diagnoses

    CANCERS = ['ILC', 'DCIS', 'IDC', 'TubularCancer', 'CancerInvasive', 'CancerInvNOS', 'CancerNotOfBreastOrigin']

    ATYPIAS = ['ALH', 'ADH', 'FlatEpithelial', 'LCIS', 'ADH_DCIS', 'LobularNeoplasia']

    MARKERS = ['ER', "ER_Intensity", 'PR', "PR_Intensity", "her2", 'Her2Fish', "Her2_IHC", 'PositiveLN', 'ECE', 'ITC', 'BVI', 'LVI']

    RATIONALE_NET_CONFIG = {
        'cuda': True,
        'num_workers': 8,
        'batch_size': 32,
        'class_balance': True,
        'dropout': 0,
        'init_lr': 0.0001,
        'weight_decay': 5e-5,
        'get_rationales': False,
        'selection_lambda': .01,
        'continuity_lambda': .01,
        'model_form': 'cnn',
        'hidden_dim': 100,
        'dataset': 'pathology_oncotext',
        'embedding': 'pathology',
        'num_layers': 1,
        'filters': [3,4,5],
        'filter_num': 100,
        'steps': 1500,
        'max_epochs': 75,
        'patience': 5,
        'snapshot': None,
        'objective':'cross_entropy',
        'num_gpus': 1,
        'save_dir': 'snapshot',
        'model_dir': SNAPSHOT_DIR+'/{}',
        'model_file': 'oncotext_{}.pt',
        'train_split': .80,
        'use_gumbel': True,
        'gumbel_temprature': 1,
        'gumbel_decay': 1e-5,
        'num_samples': 1,
        'debug_mode': False,
        'vocab_size': 1e6,
        'max_length': 720,
        'tag_lambda': 0.9,
        'tuning_metric': 'f1'
    }

    RATIONALE_NET_ARGS = Args(RATIONALE_NET_CONFIG)
