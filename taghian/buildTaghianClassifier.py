import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
import datetime

random.seed(1)

def replaceSpaces(label):
    return '_'.join(str(label).split())

if __name__ == "__main__":


    redmap = p.load(open('redmap.p', 'rb'))
    dB  = p.load(open('allExtractionDBs.p', 'rb'))
    types = set([redmap[m]['extraction feild'] for m in redmap if redmap[m]['event'] in lauraDictToIndx and not redmap[m]['extraction feild'] == None])

    modes = [ extraction for extraction in types if len(dB[extraction]) > 500 and extraction not in filtOutList]

    for mode in modes:
        db = dB[mode]
        key = mode
        stem = '_'.join(mode.split())
        stem = '_'.join(stem.split('/'))

        dirPath = "../boostexer/breast/taghian/pathology_"
        print "************************************"
        print "Generating train/test for ", stem

        print "Size of db", len(db)
        testSetSize = len(db)/5
        
        validLabels = set([replaceSpaces(r[key]) for r in db if not r[key] == None])
        print "Length of valid labels", len(validLabels)
        print "validLabels", validLabels
        filteredDB = [d for d in db if replaceSpaces(d[key]) in validLabels]

        print "Len filiteredDB", len(filteredDB)
        random.shuffle(filteredDB)


        trainReports = [t['Preprocessed_Report_Text'] for t in filteredDB[:-testSetSize]]
        trainLabels  = [t[key] for t in filteredDB[:-testSetSize]]

        print "Num train samples", len(trainLabels)
        print "-------- Train Label Dist,",key," ----------"
        print sum([t == list(validLabels)[0] for t in trainLabels]) * 1. / len(trainLabels)

        assert len(trainReports) == len(trainLabels)

        testReports = [t['Preprocessed_Report_Text'] for t in filteredDB[-testSetSize:]]
        testLabels  = [replaceSpaces(t[key]) for t in filteredDB[-testSetSize:]]

        ## Remove spaces from labels

        assert len(testReports) == len(testLabels)

        print "Num test samples", len(testLabels)
        print "-------- Test Label Dist -",key,"---------"
        print sum([t == list(validLabels)[0] for t in testLabels]) * 1. / len(testLabels)

        with open(dirPath+stem+".names", 'wb') as f:
            labels = ", ".join(validLabels) + ".\n"
            features = "pathReport: text.\n"
            f.write(labels)
            f.write(features)

        print "Saved namefile for", stem

        with open(dirPath+stem+".data", 'wb') as trF:
            for rep, label in zip(trainReports, trainLabels):
                trF.write(rep +", "+ str(label) + ".\n")

        print "Saved trainfile for", stem

        with open(dirPath+stem+".test", 'wb') as tsF:
            for rep, label in zip(testReports, testLabels):
                tsF.write(rep +", "+ str(label) + ".\n")

        print "Saved testfile for", stem
        print "************************************"
