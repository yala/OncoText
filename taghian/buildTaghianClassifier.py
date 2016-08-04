import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
import datetime

random.seed(0)

def replaceSpaces(label):
    return '_'.join(str(label).split())

if __name__ == "__main__":


    redmap = p.load(open('redmap.p', 'rb'))
    dB  = p.load(open('allExtractionDBs.p', 'rb'))
    types = set([redmap[m]['extraction feild'] for m in redmap if redmap[m]['event'] in lauraDictToIndx and not redmap[m]['extraction feild'] == None])

    modes = [ extraction for extraction in types if len(dB[extraction]) > 500 and extraction not in filtOutList]
    print 'All modess', modes
    raw_input()

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
        
        validLabelsUnfiltered = set([replaceSpaces(r[key]) for r in db if not r[key] == None])
        print "Length of valid labels unfilitered", len(validLabelsUnfiltered)
        print "validLabelsUnfiltered", validLabelsUnfiltered
        labelDist = {}
        for label in validLabelsUnfiltered:
            labelDist[label] = len([r for r in db if replaceSpaces(r[key]) == label])
        print "Distribution", labelDist
        validLabels = set([label for label in labelDist if labelDist[label] > 10 ])
        print "Valid Labels", validLabels
        filteredDB = [d for d in db if replaceSpaces(d[key]) in validLabels]

        print "Len filiteredDB", len(filteredDB)

        balanced = False
        # Reshuffle DB until there is some amount of each label on each side
        print "shuffle"
        random.shuffle(filteredDB)

        trainReports = [t['Preprocessed_Report_Text'] for t in filteredDB[:-testSetSize]]
        trainLabels  = [replaceSpaces(t[key])  for t in filteredDB[:-testSetSize]]

        print "Num train samples", len(trainLabels)
        print "-------- Train Label Dist,",key," ----------"
        for label in validLabels:
            count = sum([t == label for t in trainLabels]) 
            print "Label", label, count ,",", count * 1. / len(trainLabels)
            assert count > 0
        assert len(trainReports) == len(trainLabels)

        testReports = [t['Preprocessed_Report_Text'] for t in filteredDB[-testSetSize:]]
        testLabels  = [replaceSpaces(t[key]) for t in filteredDB[-testSetSize:]]

        ## Remove spaces from labels

        assert len(testReports) == len(testLabels)

        print "Num test samples", len(testLabels)
        print "-------- Test Label Dist -",key,"---------"
        for label in validLabels:
            count = sum([t == label for t in testLabels])
            print "Label", label, count, ',', count * 1. / len(testLabels)


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

        print "Saved testfile for", stem, 'at ', (dirPath+stem)
        print "************************************"
