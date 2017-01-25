from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import numpy as np

import sys
sys.path.append("..")
from constants import *

def evaluate(preds, golds):
    print("Call evaluate")
    accuracy = {}
    for d in nn_diagnoses:
        diag = diagName(d)
        accuracy[diag] = sum([preds[i][diag] == golds[i][diag] for i in range(len(preds))]) / len(preds)



    rowAccuracy = {}
    for i in range(len(preds)):

        for group in groupings:
            for member in group:
                if member in nn_diagnoses:
                    if not member in rowAccuracy[member]:
                        rowAccuracy[member] = 0
                    diag = diagName(member)
                    if not preds[i][diag] == golds[i][diag]:
                        rowAccuracy[member] +=1
                        break
    
    for key in rowAccuracy:
        rowAccuracy[key] = 1 -  rowAccuracy[key]/len(preds)

    averageAccuracy = sum([ accuracy[diag] for diag in nn_diagnoses ]) / len(nn_diagnoses)

    print("Group level Accuracies", rowAccuracy)
    print("category wide accuracies", accuracy)
    print("Average accuracy",averageAccuracy)

def diagName(d):
    diag = "_".join(d.split())
    diag = re.sub(r'\W','',diag)
    return diag