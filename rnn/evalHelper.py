from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import cPickle as p
import pprint
import re
import sys
sys.path.append("..")
from constants import *


NN_DIAGS = p.load(open('/home/nlp/pathology/rnn/diagDictTrain_mghMar.p'))
NN_DIAGS = [k for k in NN_DIAGS if len(NN_DIAGS[k][0]) > 0]

vocab = p.load(open('vocab.p', 'rb'))
vocabIndxDict = p.load(open('vocabIndxDict.p', 'rb'))


def diagName(d):
    diag = "_".join(d.split())
    diag = re.sub(r'\W', '', diag)
    return diag


def evaluate(preds, golds, inputs=None):
    predHist = {}
    for key in preds[0]:
        predHist[key] = {}
        for pr in preds:
            sample = pr[key][0]
            if sample not in predHist[key]:
                predHist[key][sample] = 0
            predHist[key][sample] += 1

    accuracy = {}
    for d in NN_DIAGS:
        diag = diagName(d)
        accuracy[diag] = sum([preds[i][diag] == golds[i][diag] for i in range(len(preds))]) / len(preds)

    numExamples = 0
    rowAccuracy = {}
    for i in range(len(preds)):

        for groupKey in groupings:
            groupWrong = False
            for member in groupings[groupKey]:
                if not groupWrong:
                    if member in NN_DIAGS:
                        diag = diagName(member)
                        if groupKey not in rowAccuracy:
                            rowAccuracy[groupKey] = 0
                        if not preds[i][diag] == golds[i][diag]:
                            groupWrong = True
                            rowAccuracy[groupKey] += 1
                            # if numExamples < 10 and not inputs == None:
                            # print(diag, "Guessed", preds[i][diag], "Gold, ", golds[i][diag])
                            # print(" ".join([vocab[vocabIndxDict[k]] for k in inputs[i]]))
                            break
    
    for key in rowAccuracy:
        rowAccuracy[key] = 1-rowAccuracy[key]/len(preds)

    averageAccuracy = sum([accuracy[diagName(d)] for d in NN_DIAGS])/len(NN_DIAGS)

    pprint.pprint("Group level Accuracies")
    pprint.pprint(rowAccuracy)
    pprint.pprint("category wide accuracies")
    pprint.pprint(accuracy)
    pprint.pprint("Average accuracy")
    pprint.pprint(averageAccuracy)

    print("-----------------------------")
    
    return averageAccuracy[0]
