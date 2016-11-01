import pickle as p
import re
import random
import datetime
import pprint
from operator import itemgetter
import sys
sys.path.append("..")
from constants import *

random.seed(1)
labelDict = constantValidLabelDict


def genTrainTestFiles(trainReports, trainLabels, testReports, testLabels, stem):
    writeNameFiles(stem)

    trainSuf = 'data'
    testSuf = 'test'
    for indx, diag in enumerate(diagnoses):
        trainStem = stem
        with open(trainStem+"_"+replaceSpaces(diag)+"."+trainSuf, "wb") as f: 
            for a in range(len(trainReports)):                
                if trainLabels[a][indx] in labelDict[diag]:
                    label = trainLabels[a][indx]
                else:
                    continue

                report = trainReports[a]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", trainStem+"_"+replaceSpaces(diag)+"."+trainSuf

        testStem = stem
        with open(testStem+"_"+replaceSpaces(diag)+"."+testSuf, "wb") as f: 
            for b in range(len(testReports)):   
                if testLabels[b][indx] in labelDict[diag]:
                    label = testLabels[b][indx]
                else:
                    label = defaultLabelDict[diag]

                report = testReports[b]

                assert not "\n" in report
                f.write(report + ", " + label + '.\n')

        print "Saved", testStem+"_"+replaceSpaces(diag)+"."+testSuf

def writeNameFiles(stem):
    for diag in diagnoses:
        with open(stem+"_"+replaceSpaces(diag)+".names", "wb") as f:
            if MODE == "Breast":
                if diag == u'BreastSide':
                    labels = "RIGHT, LEFT.\n"
                else:
                    labels = diag + ", " + "no_"+diag+".\n"
            elif MODE == "TAGHIAN":
                labels = ", ".join(labelDict[diag])+".\n"
            features = "pathReport : text.\n"
            f.write(labels)
            f.write(features)

# Set write to true to generate train and test files for classification. 
# Set write to false to collace files for export
def binarizeFilesForClassification(allData, stem, write = True):
    

    #valid input db isn't corrupted

    def isGold(r):
        isTaghian = 'TaghianGold' in r and r['TaghianGold'] == 1
        isHughes = 'Correct' in r and r['Correct'] == 'Y'
        return isTaghian or isHughes
    
    trainData = [d for d in allData if isGold(d)]
        

    # For taghian, because TaghianGold has a different number of things annotated per diagnosis in gold
    # Using gold labels by themselves would be a pain, so we will re-annotate the whole thing.
    # Since the training error is ~0, this wont hurt us.
    
    remainData = allData
    
    export = not write
    ## gen train data

    trainReports, trainLabels = getLabelsAndReports(trainData)
    restReports,  restLabels =  getLabelsAndReports(remainData)
    assert len(restReports) == len(remainData)

    genTrainTestFiles(trainReports, trainLabels, restReports, restLabels, stem)



def preprocessReports(reports):
    cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
    cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
    cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
    cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]
    cleanReports = [ d.lower() for d in cleanReports]
    return cleanReports

# Function takes [ reports ] and returns a tuple or reports, labels
# If export is true, returns only diagnoses, if false, also returns metaData
def getLabelsAndReports(data):
    reports = [d[reportTextKey] for d in data]
    cleanReports = preprocessReports(reports)

    labels = []

    for i in range(len(data)):
        diags = []
        sample = data[i]

        for diag in diagnoses:    
            if diag in sample and not sample[diag] == None and sample[diag] in labelDict[diag]:
                diags.append(sample[diag])

                assert replaceSpaces(sample[diag]) in labelDict[diag]

            else:
                diags.append('PLACEHOLDER')

        labels.append(diags)

    return cleanReports, labels


def say(s):
    pprint.pprint(s)




## Flex (for flexible) flag means we runs asserts on a label only if it is present in the sample
## We don't enforce that all labels are present. this is useful for pre-complete dbs
def validateRepsDB(reps, flex = False, dirty = False):
    for r in reps:
        checks = diagnoses + hueLabels if MODE == "TAGHIAN" else diagnoses
    
        for c in checks:
            assert flex or c in r

            if MODE == "TAGHIAN":
                if c in diagnoses:
                    if flex:
                        if c in r and not( replaceSpaces(r[c]) in labelDict[c] or dirty):
                            print 'r[c]',  r[c]
                            print 'c', c
                            print labelDict[c]
                        assert not (c in r) or replaceSpaces(r[c]) in labelDict[c] or dirty
                    else:
                        assert c in r and (replaceSpaces(r[c]) in labelDict[c] or dirty)
                else:
                    assert c in hueLabels
                    if c in r and not (r[c] in [0,1,'RIGHT','LEFT', '0', '1']):
                        print "C", c
                        print "r[c]", r[c]
                        assert False







if __name__ == "__main__": 
    allDataPath = redRawDBPath
    allData = p.load(open(allDataPath, 'rb'))
    binarizeFilesForClassification()




