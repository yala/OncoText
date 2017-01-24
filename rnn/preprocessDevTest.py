import cPickle as p
import word2vec
import random
import sys
sys.path.append("..")
from constants import *
import re
import numpy as np
sys.path.append('../preprocessDataset')
from aggregateDatasets import parseXLS




def preprocessText(text):
    cleanText = re.sub(r"\W", " ", text) 
    cleanText = ' '.join(cleanText.split('\n'))
    cleanText = re.sub(r"(----)+", "", cleanText)
    cleanText = re.sub(r"(====)+", "", cleanText)
    cleanText = cleanText.lower()
    return cleanText

def oneHot(diag, label):
    try:
        arr = np.zeros( (len(constantValidLabelDict[diag]), ))
        arr[ constantValidLabelDict[diag].index(label) ]  = 1
    except Exception, e:
        print diag, label
        return np.zeros( (len(constantValidLabelDict[diag]), ))
    return arr


diagDict = {}

load = True
if load:
    #TODO, load from EXCEL
    allReps =  p.load( open('goldSet.p', 'rb'))
    newReps = []
    for r in allReps:
        newR = {}
        for key in r:
            if key in conventionToDiagDict:
                targetKey = conventionToDiagDict[key]
                
            else:
                targetKey = key
            newR[targetKey] = r[key] if (targetKey not in diagnoses or r[key] in constantValidLabelDict[targetKey]) else defaultLabelDict[targetKey]
        for d in diagnoses:
            if not d in newR:
                print "D", d
                newR[d] = defaultLabelDict[d]                            
                print newR[d]
                
        newReps.append(newR)

    allReps = newReps

    j=0
    for diag in diagnoses:
        for i, r in enumerate(allReps):
            if diag in r:
                raw_Text = r["Report_Text_Segmented"].lower()
                pre_Text = preprocessText(r["Report_Text_Segmented"])
                r['Report_Text_Segmented'] = pre_Text
                r[diag] = oneHot(diag, r[diag])


    devReps = allReps[: len(allReps)/2]
    testReps = allReps[len(allReps)/2 :]


    # for i,s in enumerate(allSentences):
    #   allSentences[i] = preprocessText(s)
    
    model = word2vec.load('embeddings.bin')
    embeddings = model.vectors
    vocab      = model.vocab

    
    
    vocabIndxDict = p.load(open('vocabIndxDict.p','rb'))

    for name, reps in [('devReps',devReps), ('testReps',testReps)]:
        for j,r in enumerate(reps):
            sent = r['Report_Text_Segmented']    
            words = sent.split(" ")
            indices = [ vocabIndxDict[w] for w in words if w in vocabIndxDict]
            r['NN_Text'] = np.array(indices)
            
        p.dump(reps, open(name+'.p','wb'))







