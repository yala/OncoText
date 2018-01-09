import os, shutil
from os.path import dirname, realpath
import sys
sys.path.append(dirname(dirname(realpath(__file__))))
from config import Config
import pickle
import oncotext.utils.preprocess as preprocess
import oncotext.logger as logger
import oncotext.utils.parsing as parsing
import argparse


parser = argparse.ArgumentParser(description='Reproduce Db from invariants')

parser.add_argument('--train_db_outpath',  type=str, default='pickle_files/reportDBAPI_train.p.new', help="Place where reports are stored ")

parser.add_argument('--train_db_outpath_intermediate',  type=str, default='pickle_files/reportDBAPI_train.p.intermediate', help="Place where reports are stored ")


parser.add_argument('--source_db_path',  type=str, default='pickle_files/reportDB+red+clean.p', help="Place where original kevin+taghian reports annotations were collected")
parser.add_argument('--source_addit_db_path',  type=str, default='pickle_files/additionalTrainRepsMar10.p', help="Place where first pickle file of addit annotations was stored")

parser.add_argument('--extra_annotation_dir',  type=str, default='/home/nlp/Dropbox/NLP_Extraction/ForTraining/PastTraining', help="Dir of addition xlsx and xmls")


SUCCES_STR = "Reproduced train db!"
LOGPATH = 'LOGS'
LOGNAME = 'oncotext'
logger = logger.get_logger(LOGNAME, LOGPATH)

args = parser.parse_args()

def parse_annotation_file(path):
    '''
    Parse XML/XLSX files and return the contents.
    '''
    if path.endswith('xml'):
        return parsing.parse_XML(path)
    elif path.endswith('xlsx'):
        return parsing.parse_XLS(path)
    else:
        raise Exception("{} not an xml or xlsx!".format(path))

if __name__ == "__main__":
    '''
        recreate train db from the original cohort Taghian and Hughes provided.
    '''

    ## Load dbs

    ## Run preprocess on each db

    db_base = pickle.load(open(args.source_db_path, 'rb'), encoding='bytes')
    db_base += pickle.load(open(args.source_addit_db_path, 'rb'), encoding='bytes')

    ## 1.  Delete keys not in old convention
    conved_keys= ['CancerSuspicious',
                'ALH',
                'InvasiveSuspicious',
                'FlatEpithelial',
                'CancerNOS',
                'ADH',
                'ADH_DCIS',
                'ILC',
                'BreastSide',
                'IDC',
                'Phylodes',
                'LobularNeoplasia',
                'BluntAdenosis',
                'CancerInvInsituNOS',
                'TubularCancer',
                'DCIS',
                'LCIS',
                'InsituNOS']

    ## 1.5 Make all keys strs
    for report in db_base:
        keys = report.keys()
        for key in keys:
            val = report[key]
            if isinstance(val, bytes):
                report[key] = val.decode()
            if isinstance(key, bytes):
                report[key.decode()] = report[key]
                del report[key]

    # 1.9 Del keys in new convention that need be overwritten
    for report in db_base:
        for key in conved_keys:
            if not key in report:
                continue
            del report[key]

    ## 2. Map all keys in old convention to new convention, and del old
    for report in db_base:
        for key in conved_keys:
            old_conv_key = "Red {}".format(key)
            if not old_conv_key in report:
                continue
            report[key] = report[old_conv_key]
            del report[old_conv_key]

    ## 4. Change all labels to new convention

    LABEL_TO_NEW_LABEL_MAP = {
                     'Absent': '0',
                     'Other': '9',
                     'NA' :'9',
                     'LEFT': 'l',
                     'Negative': '0',
                     'No': '0',
                     'Positive': '1',
                     'Present': '1',
                     'RIGHT': 'r',
                     'Yes': '1',
                     'breast': '1',
                     'non-breast': '0'
                     }

    transformed_keys = []
    for report in db_base:
        for key in report:
            val = report[key]
            if val in LABEL_TO_NEW_LABEL_MAP:
                transformed_keys.append(key)
                report[key] = LABEL_TO_NEW_LABEL_MAP[val]

    transformed_keys = set(transformed_keys)
    ## 5. Save as intermediate
    pickle.dump(db_base, open(args.train_db_outpath_intermediate,'wb'))

    ## 6. Go through XMLs and update to naming / label convention
    files = os.listdir(args.extra_annotation_dir)
    addit_annotations = []
    for file in files:
        path = os.path.join(args.extra_annotation_dir, file)
        annotation = parse_annotation_file(path)
        addit_annotations += annotation

    ## 7. Concat all dbs and call preprocessing script

    db_base = preprocess.apply_rules(db_base,
                                     Config.RAW_REPORT_TEXT_KEY,
                                     Config.PREPROCESSED_REPORT_TEXT_KEY,
                                     Config.REPORT_TIME_KEY,
                                     Config.SIDE_KEY,
                                     logger)

    ## 8. put in a dict under default.
    train_db = {Config.DEFAULT_USERNAME: db_base}

    ## 9. dump to out path
    pickle.dump(train_db, open(Config.train_db_outpath, 'wb'))
    logger.info(SUCCES_STR)
