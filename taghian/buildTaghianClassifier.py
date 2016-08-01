import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
import datetime

random.seed(1)

def replaceSpaces(label):
    return '_'.join(label.split())

if __name__ == "__main__":
    paths = ['her2DB.p', 'erDB.p', 'prDB.p']
    mode = ["her2", "er", "pr"]
    testSetSize = 500

    for indx, path in enumerate(paths):
        db = p.load(open(path, 'rb'))
        key = mode[indx]
        stem = mode[indx]
        dirPath = "../boostexer/breast/taghian/pathology_"
        print "Generating train/test for ", stem

        validLabels = set([replaceSpaces(r[key]) for r in db if not r[key] == None])
        filteredDB = [d for d in db if d[key] in validLabels]

        print "Len filiteredDB", len(filteredDB)
        random.shuffle(filteredDB)


        trainReports = [t['Preprocessed_Report_Text'] for t in filteredDB[:-testSetSize]]
        trainLabels  = [t[key] for t in filteredDB[:-testSetSize]]

        print "Num train samples", len(trainLabels)
        print "-------- Train Label Dist,",key," ----------"
        print sum([t == "Positive" for t in trainLabels]) * 1. / len(trainLabels)

        assert len(trainReports) == len(trainLabels)

        testReports = [t['Preprocessed_Report_Text'] for t in filteredDB[-testSetSize:]]
        testLabels  = [replaceSpaces(t[key]) for t in filteredDB[-testSetSize:]]

        ## Remove spaces from labels

        assert len(testReports) == len(testLabels)

        print "Num test samples", len(testLabels)
        print "-------- Test Label Dist -",key,"---------"
        print sum([t == "Positive" for t in testLabels]) * 1. / len(testLabels)

        with open(dirPath+stem+".names", 'wb') as f:
            labels = ", ".join(validLabels) + ".\n"
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
