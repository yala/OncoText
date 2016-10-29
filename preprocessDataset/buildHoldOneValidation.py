import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
from createEpisodes import preprocessReports
import datetime

random.seed(0)

def replaceSpaces(label):
    return '_'.join(str(label).split())

if __name__ == "__main__":

    assert MODE == "TAGHIAN"

    buildLabelDictsBool = False

    redmap = p.load(open('redmap.p', 'rb'))
    dB  = p.load(open('../reportDB+red+clean.p', 'rb'))
    if buildLabelDictsBool:
        allLabelDict = {}    
        validLabelDict = {}
    else:
        validLabelDict = constantValidLabelDict

    modes = diagnoses    
    print 'All modess', modes

    hughesTest = p.load(open('../analysis/genBoostexaTestReportDump.p', 'rb'))
    
    testSets = {}

    for mode in ['Oncotype score']:
        print "mode", mode
        db = [d for d in dB if mode in d and not d[mode] == None]
        key = mode
        stem = '_'.join(mode.split())
        stem = '_'.join(stem.split('/'))

        dirPath = "../boostexer/breast/crossval/pathology_"
        print "************************************"
        print "Generating train/test for ", stem

        

        textKey = reportTextKey

        print "Size of db", len(db)
        testSetSize = min(int(len(db) * .15 ), 500)
            
        validLabels = validLabelDict[mode]
    
        filteredDB = [d for d in db if replaceSpaces(d[key]) in validLabels]

        print "Len filiteredDB", len(filteredDB)

        print "-------- Overall Label Dist ----------"
        for label in validLabels:
            count = sum([replaceSpaces(t[key]) == label for t in filteredDB])
            print "Label", label, count, ',', count * 1. / len(filteredDB)
        raw_input()
        balanced = False
        
        for i in range(len(filteredDB)):
            # Reshuffle DB until there is some amount of each label on each side
            print i
            trainReports = [preprocessReports([t[textKey]])[0] for t in filteredDB[0:i]+filteredDB[i+1:]]
            trainLabels  = [replaceSpaces(t[key])  for t in filteredDB[0:i]+filteredDB[i+1:]]

            print "Num train samples", len(trainLabels)
            print "-------- Train Label Dist,",key," ----------"
            for label in validLabels:
                count = sum([t == label for t in trainLabels]) 
                print "Label", label, count ,",", count * 1. / len(trainLabels)
                assert count > 0
            assert len(trainReports) == len(trainLabels)

            testReports = [preprocessReports([t[textKey]])[0] for t in [filteredDB[i]]]
            testLabels  = [replaceSpaces(t[key]) for t in [filteredDB[i]]]

            testSets[mode] = [d['Report_Text_Segmented'] for f in filteredDB[-testSetSize:] ]
            
            ## Remove spaces from labels

            assert len(testReports) == len(testLabels)

            print "Num test samples", len(testLabels)
            print "-------- Test Label Dist -",key,"---------"
            for label in validLabels:
                count = sum([t == label for t in testLabels])
                print "Label", label, count, ',', count * 1. / len(testLabels)

            print "Num OVERALL samples", len(testLabels)
            print "-------- OVERALL Label Dist -",key,"---------"
            print "LEN", len(trainLabels + testLabels)
            for label in validLabels:
                count = sum([t == label for t in trainLabels+testLabels])
                print "Label", label, count, ',', count * 1. / len(trainLabels+testLabels) * 100


            with open(dirPath+stem+"_"+str(i)+".names", 'wb') as f:
                labels = ", ".join(validLabels) + ".\n"
                features = "pathReport: text.\n"
                f.write(labels)
                f.write(features)

            print "Saved namefile for", stem

            with open(dirPath+stem+"_"+str(i)+".data", 'wb') as trF:
                for rep, label in zip(trainReports, trainLabels):
                    trF.write(rep +", "+ str(label) + ".\n")

            print "Saved trainfile for", stem

            with open(dirPath+stem+"_"+str(i)+".test", 'wb') as tsF:
                for rep, label in zip(testReports, testLabels):
                    tsF.write(rep +", "+ str(label) + ".\n")

            print "Saved testfile for", stem, 'at ', (dirPath+stem)
            print "************************************"


    print "Fin"
