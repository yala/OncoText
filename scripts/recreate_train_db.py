import os, shutil
from os.path import dirname, realpath
import sys
sys.path.append(dirname(dirname(realpath(__file__))))
from config import Config
import pickle
import oncotext.utils.preprocess as preprocess
import oncotext.logger as logger
import oncotext.utils.parsing as parsing
import oncotext.utils.generic as generic
import argparse


parser = argparse.ArgumentParser(description='Reproduce Db from invariants')

parser.add_argument('--train_db_outpath',  type=str, default=Config.PICKLE_DIR+'reportDBAPI_train.p', help="Place where reports are stored ")
parser.add_argument('--base_db_outpath',  type=str, default=Config.PICKLE_DIR+'reportDB_base_train.p', help="Place where reports are stored ")
parser.add_argument('--train_db_outpath_intermediate',  type=str, default=Config.PICKLE_DIR+'reportDBAPI_train.p.intermediate', help="Place where reports are stored ")


parser.add_argument('--source_db_path',  type=str, default=Config.PICKLE_DIR+'reportDB+red+clean.p', help="Place where original kevin+taghian reports annotations were collected")
parser.add_argument('--source_addit_db_path',  type=str, default=Config.PICKLE_DIR+'additionalTrainRepsMar10.p', help="Place where first pickle file of addit annotations was stored")

parser.add_argument('--extra_annotation_dir',  type=str, default='/Mounts/Isilon/Dropbox/NLP_Extraction/ForTraining/PastTraining', help="Dir of addition xlsx and xmls")
parser.add_argument('--keys_and_values_file',  type=str, default='/Mounts/Isilon/Dropbox/NLP_Extraction/SQL_KeysAndValues_Multiorgan.xlsx', help="File with keys and values for each organ")


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
        return parsing.parse_XLS_reports(path)
    else:
        return []

if __name__ == "__main__":
    '''
        recreate train db from the original cohort Taghian and Hughes provided.
    '''

    db_base = pickle.load(open(args.source_db_path, 'rb'), encoding='bytes')
    db_base += pickle.load(open(args.source_addit_db_path, 'rb'), encoding='bytes')
    
    ## Get previous annotation files
    files = os.listdir(args.extra_annotation_dir)
    addit_annotations = []
    for file in files:
        path = os.path.join(args.extra_annotation_dir, file)
        annotation = parse_annotation_file(path)
        addit_annotations.extend(annotation)

    filt_annotations = []
    for report in addit_annotations:
        try:
            report = dict(report)
            filt_annotations.append(report)
        except Exception as e:
            # Corrupt row, usaully just a note or just an ID for eyeballing it
            continue

    ## Normalize key names
    for report in filt_annotations:
        keys = report.keys()
        for key in keys:
            val = report[key]
            if isinstance(val, bytes):
                report[key] = val.decode()
            if isinstance(key, bytes):
                report[key.decode()] = report[key]
                del report[key]
                key = key.decode()
            if "_x0020_" in key:
                new_key = key.replace("_x0020_","_")
                report[new_key] = report[key]
                del report[key]

        if 'Her2 (Fish)' in report:
            report['Her2Fish'] = report['Her2 (Fish)']
            del report['Her2 (Fish)']

        if 'Are there positive LN?' in report:
            report['PositiveLN'] = report['Are there positive LN?']
            del report['Are there positive LN?']

        if 'Node_tissue' in report:
            report['NodeTissue'] = report['Node_tissue']
            del report['Node_tissue']

        # re-segment all reports
        if Config.PREPROCESSED_REPORT_TEXT_KEY in report:
            del report[Config.PREPROCESSED_REPORT_TEXT_KEY]


    ## Noramlize label values
    LABEL_TO_NEW_LABEL_MAP = {
        'Absent': '0',
        'Other': '9',
        'NA' :'9',
        'na': '9', 
        'LEFT': 'l',
        'L': 'l',
        'R': 'r',
        'Negative': '0',
        'No': '0',
        'NO': '0',
        'Positive': '1',
        'Present': '1',
        'present': '1',
        'RIGHT': 'r',
        'Yes': '1',
        'breast': '1',
        'non-breast': '0',
        'unknown': '9'
    }

    transformed_keys = []
    for report in filt_annotations:
        for key in report:
            val = report[key]
            if val in LABEL_TO_NEW_LABEL_MAP:
                transformed_keys.append(key)
                report[key] = LABEL_TO_NEW_LABEL_MAP[val]

    print("{} were transformed in relabel".format( set(transformed_keys)))

    
    db_default = {}
    for organ in Config.COLUMN_KEYS:
        db_concat_all = []
        if organ == "OrganBreast":
            ## 1.  Keys not in old convention
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
                        key = key.decode()

                    if "_x0020_" in key:
                        new_key = key.replace("_x0020_","_")
                        report[new_key] = report[key]
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

                ## Do this adhoc for Her2Fish
                if 'Her2 (Fish)' in report:
                    report['Her2Fish'] = report['Her2 (Fish)']
                    del report['Her2 (Fish)']
                        
                if 'Are there positive LN?' in report:
                    report['PositiveLN'] = report['Are there positive LN?']
                    del report['Are there positive LN?']

                if 'Node_tissue' in report:
                    report['NodeTissue'] = report['Node_tissue']
                    del report['Node_tissue']

                if 'Phylodes' in report:
                    report['Phyllodes'] = report['Phylodes']
                    del report['Phylodes']

                if 'Organ' in report and 'OrganBreast' not in report:
                    report['OrganBreast'] = report['Organ']

                    
            ## 3. Change all labels to new convention

            transformed_keys = []
            for report in db_base:
                for key in report:
                    val = report[key]
                    if val in LABEL_TO_NEW_LABEL_MAP:
                        transformed_keys.append(key)
                        report[key] = LABEL_TO_NEW_LABEL_MAP[val]
            print("{} were transformed in relabel".format( set(transformed_keys)))

            db_concat_all.extend(db_base)

        ## 7. Concat all dbs
        for r in filt_annotations:
            if len(r.keys() & Config.COLUMN_KEYS[organ].keys()) > 0:
                db_concat_all.append(r)


        # for report in db_concat_all:
        #     for key in Config.DIAGNOSES:
        #         if key in report and not report[key] in Config.DIAGNOSES[key]:
        #             del report[key]


        ##7.5 Filter for only those that contain an annotation
        db_concat = []
        for report in db_concat_all:
            if generic.hasCat(report, list(Config.DIAGNOSES.keys()), loose = True):
                db_concat.append(report)

        print("{} num annotations in end for {}".format(len(db_concat, organ)))

        
        ##7.9 Call preprocesing script
        db_concat = preprocess.apply_rules(db_concat,
                                           Config.RAW_REPORT_TEXT_KEY,
                                           Config.PREPROCESSED_REPORT_TEXT_KEY,
                                           Config.REPORT_TIME_KEY,
                                           Config.SIDE_KEY,
                                           logger)

        db_default[organ] = db_concat

        ## 8. put in a dict under default.
        train_db = {Config.DEFAULT_USERNAME: db_concat}
        filename = args.train_db_outpath.split(".")[0]+"_"+organ+".p"
        pickle.dump(train_db, open(filename, 'wb'))
    
    ## 9. dump to out path
    pickle.dump(db_concat, open(args.base_db_outpath, 'wb'))

    logger.info(SUCCES_STR)
