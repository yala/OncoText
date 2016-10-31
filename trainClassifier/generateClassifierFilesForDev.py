import sys
sys.path.append("..")
import pickle as p
import re
import random
from constants import *
from generateClassifierFilesForProd import preprocessReports
import datetime

random.seed(0)

def replaceSpaces(label):
    return '_'.join(str(label).split())

if __name__ == "__main__":

    assert MODE == "TAGHIAN"

    buildLabelDictsBool = False

    redmap = p.load(open('../preprocessDataset/data/redmap.p', 'rb'))
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

    for mode in modes:
        print "mode", mode
        db = [d for d in dB if mode in d and not d[mode] == None]
        key = mode
        stem = '_'.join(mode.split())
        stem = '_'.join(stem.split('/'))

        dirPath = "../boostexer/breast/taghian/pathology_"
        print "************************************"
        print "Generating train/test for ", stem

        

        textKey = reportTextKey

        print "Size of db", len(db)
        testSetSize = min(int(len(db) * .15 ), 500)
            
        validLabels = validLabelDict[mode]
    
        filteredDB = [d for d in db if replaceSpaces(d[key]) in validLabels]

        print "Len filiteredDB", len(filteredDB)

        alignTest = True
        if not mode in MixedAnotations or not alignTest:

            # Reshuffle DB until there is some amount of each label on each side
            print "shuffle"
            random.shuffle(filteredDB)

            trainReports = [preprocessReports([t[textKey]])[0] for t in filteredDB[:-testSetSize]]
            trainLabels  = [replaceSpaces(t[key])  for t in filteredDB[:-testSetSize]]

            testReports = [preprocessReports([t[textKey]])[0] for t in filteredDB[-testSetSize:]]
            testLabels  = [replaceSpaces(t[key]) for t in filteredDB[-testSetSize:]]

            testSets[mode] = zip(testReports, testLabels)
        else:
            print "mixed annotation"
            hkey = "Report_Text_Segmented"
            print "aligning reports for ", mode, 'to test set for hughes dataset for row level scores'
            train = [(preprocessReports([t[hkey]])[0], replaceSpaces(t[key])) for t in filteredDB if not \
            t['Report_Text_Segmented'] in hughesTest ]
            trainReports, trainLabels = [t[0] for t in train], [t[1] for t in train]

            #this will be very slow O(n^2) and a temporary work around to make row level scores
            #enforce same order as hugheTest
            test = []
            for hReport in hughesTest:
                search = [ (preprocessReports([t[hkey]])[0], replaceSpaces(t[key]) )  for t \
                in filteredDB if t['Report_Text_Segmented'] == hReport ]
                assert len(search) > 0
                test.append( search[0] )

            assert len(test) == 500
            testReports, testLabels = [t[0] for t in test], [t[1] for t in test]

            if hkey == "Report_Text_Segmented":
                for rep in testReports + trainReports:
                    assert not ("right" in rep.lower() and "left" in rep.lower())
            print 'aligning done'

            testSets[mode] = zip(testReports, testLabels)

        print "Num train samples", len(trainLabels)
        print "-------- Train Label Dist,",key," ----------"
        for label in validLabels:
            count = sum([t == label for t in trainLabels]) 
            print "Label", label, count ,",", count * 1. / len(trainLabels)
            assert count > 0
        assert len(trainReports) == len(trainLabels)

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
    if buildLabelDictsBool:
        print "Dumping validLabel dict"
        p.dump(validLabelDict, open("../redLabelDict.p", 'wb'))
        p.dump(allLabelDict, open("../allRedLabelsAllDict.p", "wb"))

    p.dump(testSets, open('../buildTaghianClassifierTestSets.p', 'wb'))
    print "Fin"
