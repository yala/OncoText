import cPickle as p
import sys
sys.path.append("..")
import numpy as np
from constants import *


name = "mghMar"
def main(mode='eval') :

    if mode == 'eval':
        db = p.load(open('/home/nlp/pathology/evalDB_'+name+'.p','rb'))
        testSet = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))
    elif mode == 'pakistani':
        db = p.load(open('/home/nlp/pathology/pakistaniDB_'+name+'.p','rb'))
        testSet = p.load(open('/home/nlp/pathology/externalDataSources/pakistani_data.p','rb'))


    text_to_gold = {}
    for d in testSet:
        if mode == 'eval':
            for k in diagToConventionDict:
                if not k in d:
                    continue 
                ##Convert label from diag format to clean conv
                d[diagToConventionDict[k]] = d[k]
                ## convert frome onehot to str label
                label_ind = np.argmax(d[k])
                d[diagToConventionDict[k]] = constantValidLabelDict[k][label_ind]

        text_to_gold[ d['Report_Text_Segmented']] = d

    text_to_pred = {}
    for d in db:
        if d["Report_Text_Segmented"] in text_to_gold:
            text_to_pred[d['Report_Text_Segmented']] = d

    results = []
    for d in conventionToDiagDict:
        res = {'name':d}
        texts = [t for t in text_to_pred]       
        pred, gold = [text_to_pred[t][d] for t in texts if d in text_to_pred[t]],  [text_to_gold[t][d] for t in texts if d in text_to_pred[t]]
        if len(pred) == 0:
            continue
        res['accuracy'] = sum([ pred[i] == gold[i] for i in range(len(pred))] )*100./ len(pred)
        
        truePos =  sum([gold[i] in ['Present', 'Yes'] and pred[i] == ['Present', 'Yes'] for i in range(len(pred))])
        falsePos = sum([gold[i] == ['Absent', 'No'] and pred[i] == ['Present', 'Yes'] for i in range(len(pred))])
        trueNeg  = sum([gold[i] == ['Absent', 'No'] and pred[i] == ['Absent', 'No'] for i in range(len(pred))])
        falseNeg = sum([gold[i] == ['Present', 'Yes'] and pred[i] == ['Absent', 'No'] for i in range(len(pred))])


        percision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else 0
        recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else 0
        f1        =  2. * (percision * recall)  / (percision + recall) if (percision + recall) >0 else 0

        res['precision'] = precision
        res['recall'] = recall
        res['f1'] = f1


        results.append(res)
    
    overallRes = {'name':'average'}
    overallRes['accuracy'] = sum([r['accuracy'] for r in results]) / len(results)
    overallRes['precision'] = sum([r['precision'] for r in results]) / len(results)
    overallRes['recall'] = sum([r['recall'] for r in results]) / len(results)
    overallRes['f1'] = sum([r['f1'] for r in results]) / len(results)

    results.append(overallRes)

    print results
    return results



if __name__ == "__main__":
    main()
