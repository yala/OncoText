from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np
import re
import sys
sys.path.append("..")
from constants import *
import pprint

def diagName(d):
    diag = "_".join(d.split())
    diag = re.sub(r'\W','',diag)
    return diag

def evaluate(preds, golds):

    predHist = {}
    for key in preds[0]:
        predHist[key] = {}
        for p in preds:
            sample = p[key][0]
            if sample not in predHist[key]:
                predHist[key][sample] = 0
            predHist[key][sample] +=1
    print("------------------------")
    print("Predicition Histogram")
    pprint.pprint(predHist)




    accuracy = {}
    for d in nn_diagnoses:
        diag = diagName(d)
        accuracy[diag] = sum([preds[i][diag] == golds[i][diag] for i in range(len(preds))]) / len(preds)



    rowAccuracy = {}
    for i in range(len(preds)):
        for groupKey in groupings:
            for member in groupings[groupKey]:
                if member in nn_diagnoses:
                    if not member in rowAccuracy[member]:
                        rowAccuracy[member] = 0
                    diag = diagName(member)
                    if not preds[i][diag] == golds[i][diag]:
                        rowAccuracy[member] +=1
                        break
    
    for key in rowAccuracy:
        rowAccuracy[key] = 1 -  rowAccuracy[key]/len(preds)

    averageAccuracy = sum([ accuracy[ diagName(d) ] for d in nn_diagnoses ]) / len(nn_diagnoses)

    pprint.pprint("Group level Accuracies", rowAccuracy)
    pprint.pprint("category wide accuracies", accuracy)
    pprint.pprint("Average accuracy",averageAccuracy)

