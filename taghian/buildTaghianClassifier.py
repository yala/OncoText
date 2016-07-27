import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
import datetime

random.seed(1)

if __name__ == "__main__":
    keys = ['Her2 (FISH)', 'Estrogen Receptor - qualitative', 'Progesterone receptor - qualitative']
    paths = ['her2DB.p', 'erDB.p', 'prDB.p']
    outStem = ["her2", "er", "pr"]

    for indx, path in enumerate(paths):
        db = p.load(open(path, 'rb'))
        key = keys[indx]
        stem = outStem[indx]
        dirPath = "../boostexer/breast/taghian/pathology_"
        print "Generating train/test for ", stem

        validLabels = ["Negative", "Positive"]
        filteredDB = [d for d in db if d[key] in validLabels]

        print "Len filiteredDB", len(filteredDB)
        random.shuffle(filteredDB)


        trainReports = [t['Preprocessed_Report_Text'] for t in filteredDB[:-400]]
        trainLabels  = [t[key] for t in filteredDB[:-400]]

        print "Num train samples", len(trainLabels)

        assert len(trainReports) == len(trainLabels)

        testReports = [t['Preprocessed_Report_Text'] for t in filteredDB[-400:]]
        testLabels  = [t[key] for t in filteredDB[-400:]]

        assert len(testReports) == len(testLabels)

        print "Num test samples", len(testLabels)


        with open(dirPath+stem+".name", 'wb') as f:
            labels = "Positive, Negative.\n"
            features = "pathReport: text.\n"
            f.write(labels)
            f.write(features)

        print "Saved namefile for", stem

        with open(dirPath+stem+".data", 'wb') as trF:
            for rep, label in zip(trainReports, trainLabels):
                trF.write(rep +", "+ label + ".\n")

        print "Saved trainfile for", stem

        with open(dirPath+stem+".test", 'wb') as tsF:
            for rep, label in zip(testReports, testLabels):
                tsF.write(rep +", "+ label + ".\n")

        print "Saved testfile for", stem
