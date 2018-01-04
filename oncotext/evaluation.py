import cPickle as p
from datetime import datetime as date
import sys, os
import numpy as np
from constants import *
from csv import DictWriter
import pdb
import smtplib
import string
import sklearn
import oncotext.utils.parsing as parsing
import oncotext.utils.preprocess as preprocess



def score_on_test_set(reports, test_set, config, logger):

    gold_reports = preprocess.apply_rules(test_set)
    preprocessed_text_key = config['PREPROCESSED_REPORT_TEXT_KEY']
    diagnoses = config['post_diagnoses']

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
    for d in diagnoses:
        res = {'NAME':d}
        texts = [t for t in text_to_pred]

        pred, gold = [text_to_pred[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]],  [text_to_gold[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]]

        if len(pred) == 0:
            continue
        res['ACCURACY'] = sum([pred[i] == gold[i] for i in range(len(pred))])*100. / len(pred)
        res['PERCENTPOS'] = sum([g in ['1'] for g in gold])*100. / len(gold)

        truePos = sum([gold[i] == '1' and pred[i] == '1' for i in range(len(pred))])
        falsePos = sum([gold[i] == '0' and pred[i] == '1' for i in range(len(pred))])
        trueNeg = sum([gold[i] == '0' and pred[i] == '0' for i in range(len(pred))])
        falseNeg = sum([gold[i] == '1' and pred[i] == '0' for i in range(len(pred))])

        #print d
        #print "truePos", truePos
        #print "falsePos", falsePos
        #print "falseNeg", falseNeg
        precision = 1.*truePos / (truePos+falsePos) if (truePos+falsePos) > 0 else 0
        recall = 1.*truePos / (truePos+falseNeg) if (truePos+falseNeg) > 0 else 0
        f1 = 2.*(precision*recall)/(precision+recall) if (precision+recall) >0 else 0

        res['PRECISION'] = precision
        res['RECALL'] = recall
        res['F1'] = f1

        results.append(res)

    overallRes = {'NAME':'AVERAGE'}
    overallRes['ACCURACY'] = sum([r['ACCURACY'] for r in results]) / len(results)
    overallRes['PRECISION'] = sum([r['PRECISION'] for r in results]) / len(results)
    overallRes['RECALL'] = sum([r['RECALL'] for r in results]) / len(results)
    overallRes['F1'] = sum([r['F1'] for r in results]) / len(results)
    overallRes['PERCENTPOS'] = 'NA'

    results.append(overallRes)

    print results

    today = date.now().strftime("%Y-%d-%m")
    #dateStr = "-".join([str(s) for s in today])
    setName = inFile.split('.')[0]
    path = outPath+setName+'_'+today+'.csv'
    keys = ['NAME', 'PERCENTPOS', 'ACCURACY', 'PRECISION', 'RECALL', 'F1']
    print "Saving results to", path
    with open(path,'w') as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(results)

    return results, path


def evaluate(reportDB, config, logger):
    test_set_paths = os.listdir( config['EVALDIR'])
    test_file_names = [p for p in test_set_paths if p.endswith('.xlsx')]

    for file_name in test_file_names:
        test_path = os.path.join(config['EVALDIR'], file_name)
        relevant_reports = [r for r in reportDB if r['filename'] == file_name]
        logger.info("Scoring reportDB against test_set {}".format(test_path))
        test_set = parsing.parse_XLS(test_path)
        logger.info("Scoring reportDB has {} records matching  test_set {} records".format(len(relevant_reports), len(test_set)))
        results, result_path = score_on_test_set(relevant_reports, test_set,
                                                 config, logger)

    return None

def main(sendText=True):
    message = ""
    for goldset in os.listdir(EVALDIR):
        if goldset.endswith('.xlsx'):
            results, path = calcScores(goldset)
            message += "\nRetraining completed today for "+str(goldset)+"!\nAverage accuracy was "+str(results[-1]['ACCURACY'])+". Full results are stored at "+path+".\n"

    if sendText:
        print "Sending email update..."
        send_mail(message)
    return results

if __name__ == "__main__":
    main(sendText=True)
