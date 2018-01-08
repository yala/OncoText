from datetime import datetime as date
import sys, os
import numpy as np
from csv import DictWriter
import pdb
import smtplib
import string
import sklearn
import oncotext.utils.parsing as parsing
import oncotext.utils.preprocess as preprocess
import sklearn.metrics

def score_on_test_set(reports, test_set, config, logger):

    gold_reports = preprocess.apply_rules(test_set)
    preprocessed_text_key = config['PREPROCESSED_REPORT_TEXT_KEY']
    diagnoses = config['POST_DIAGNOSES']

    text_to_gold = {}
    for r in gold_reports:
        text = r[preprocessed_text_key]
        text_to_gold[ text ] = r

    logger.info("evaluation - test set has {} unique preprocessed texts".format(len(text_to_gold)))

    text_to_pred = {}
    for r in reports:
        text = r[preprocessed_text_key]
        text_to_pred[text] = r
    logger.info("evaluation - filename filtered report set has {} unique preprocessed texts".format(len(text_to_pred)))

    results = []
    keys = ['NAME', 'PERCENTPOS', 'ACCURACY', 'PRECISION', 'RECALL', 'F1']
    for d in diagnoses:
        res = {'NAME':d}
        texts = [t for t in text_to_pred]

        preds = [text_to_pred[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]]
        golds =  [text_to_gold[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]]

        if len(preds) == 0 or len(golds) == 0:
            logger.warnings("evaluation [{}] - skipping because num preds {}, num golds {}".format(d, len(preds), len(golds)))
            continue

        res['ACCURACY'] = sklearn.metrics.accuracy_score(preds, golds)
        res['PERCENTPOS'] = sum([g in ['1'] for g in gold])*100. / len(gold)

        res['PRECISION'] = sklearn.metrics.precision_score(preds, golds)
        res['RECALL'] = sklearn.metrics.recall_score(preds, golds)
        res['F1'] = sklearn.metrics.f1_score(preds, golds)

        results.append(res)

    overallRes = {'NAME':'AVERAGE'}
    overallRes['ACCURACY'] = np.mean([r['ACCURACY'] for r in results])
    overallRes['PRECISION'] = np.mean([r['PRECISION'] for r in results])
    overallRes['RECALL'] = np.mean([r['RECALL'] for r in results])
    overallRes['F1'] = np.mean([r['F1'] for r in results])

    results.append(overallRes)

    return results, keys


def evaluate(reportDB, config, logger):
    test_set_paths = os.listdir( config['EVALDIR'])
    results_dir = config['RESULTSDIR']
    test_file_names = [p for p in test_set_paths if p.endswith('.xlsx')]

    today = date.now().strftime("%m-%d-%Y")
    result_paths = []

    for file_name in test_file_names:
        test_path = os.path.join(config['EVALDIR'], file_name)
        relevant_reports = [r for r in reportDB if r['filename'] == file_name]
        logger.info("Scoring reportDB against test_set {}".format(test_path))
        test_set = parsing.parse_XLS(test_path)
        logger.info("Scoring reportDB has {} records matching  test_set {} records".format(len(relevant_reports), len(test_set)))
        results, result_keys = score_on_test_set(relevant_reports, test_set,
                                                 config, logger)

        out_name = "{}_{}.csv".format(file_name.split('.')[0], today)
        out_path = os.path.join(results_dir, out_name)

        logger.info("Saving results for {} to {}".format(file_name, out_path))

        result_paths.append(out_path)

        with open(out_path,'w') as out_csv:
            writer = DictWriter(out_csv, result_keys)
            writer.writeheader()
            writer.writerows(results)
        message = "Retraining completed for {} \n Avg accuracy was {}.\n  Full results stored at {}".format(file_name, results[-1]['ACCURACY'], out_path)
        logger.info("Sending email")
        send_mail(message)


    return result_paths
