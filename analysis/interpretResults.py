import pickle as p
import sys
sys.path.append("..")
from constants import *


diagSamples = {}

catergoryVerbose= True
overallVerbose= True


if __name__ == "__main__":

    stem = sys.argv[1]

    labels = ['Positive']

    if MODE == "TAGHIAN":
        redmap = p.load(open('../taghian/redmap.p', 'rb'))
        dB  = p.load(open('../taghian/allExtractionDBs.p', 'rb'))
        diagLabelDict = constantValidLabelDict

    print "Calling interpret for ", stem
    for diag in diagnoses:
        diagFile = '_'.join(diag.split())
        diagFile = '_'.join(diagFile.split('/'))
        with open(stem+diagFile+".txt", 'rb') as f:
           diagSamples[diag] = f.readlines()


    gold = {}
    guessed = {}
    for d in diagnoses:
        if MODE == "TAGHIAN":
            labels = diagLabelDict[d]
        gold[d] = {}
        guessed[d] = {}
        for l in labels:
            gold[d][l] = []
            guessed[d][l] = []


    for diag in diagnoses:
        samples = diagSamples[diag]
        if MODE == "TAGHIAN":
            labels = diagLabelDict[diag]

        for row, sample in enumerate(samples):
            for labelIndx, label in enumerate(labels):

                goldsAndPredictions = [float(f) for f in sample.split()]

                assert len(goldsAndPredictions) % 2 == 0
                golds = []
                guesses = []

                goldsVec = goldsAndPredictions[:len(goldsAndPredictions)/2]
                
                guessedVec = goldsAndPredictions[len(goldsAndPredictions)/2:]

                assert len(goldsVec) == len(guessedVec)
               

                gold[diag][label].append(goldsVec[labelIndx])

                predictionIndx = guessedVec.index(max(guessedVec))
                if labelIndx == predictionIndx:
                    prediction = 1
                else:
                    prediction = 0

                guessed[diag][label].append(prediction)


    overallGold = []
    overallGuessed = []
    for diag in diagnoses:
        if MODE == "TAGHIAN":
            labels = diagLabelDict[diag]
        for label in labels:
            defualt = 1
            if catergoryVerbose:
                print "---------------------------"
                print diag, label
                print "Number of gold",  sum(gold[diag][label])
                print "Number guessed",  sum(guessed[diag][label])
                assert len(guessed[diag][label]) == len(gold[diag][label])
            overallGold.extend(gold[diag][label])
            overallGuessed.extend(guessed[diag][label])
            truePos = sum([guessed[diag][label][i] == 1 and gold[diag][label][i] == 1 for i in range(len(gold[diag][label]))])
            falsePos = sum([guessed[diag][label][i] == 1 and gold[diag][label][i] == 0 for i in range(len(gold[diag][label]))])
            trueNeg  = sum([guessed[diag][label][i] == 0 and gold[diag][label][i] == 0 for i in range(len(gold[diag][label]))])
            falseNeg = sum([guessed[diag][label][i] == 0 and gold[diag][label][i] == 1 for i in range(len(gold[diag][label]))])


            percision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else defualt
            recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else defualt
            f1        =  2. * (percision * recall)  / (percision + recall) if (percision + recall) >0 else defualt

            sensitivity = recall
            specifcity = 1.* trueNeg / (trueNeg + falsePos) if (trueNeg + falsePos) >0 else defualt

            if catergoryVerbose:
                print diag, label, "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
                print diag, label, "percision, recall, f1:", percision, ',', recall, ',', f1
                print diag, label, "sensitivity, specifcity:", sensitivity, ',', specifcity
                print "Diag", diag, label, ", Num Mistakes:", (falsePos + falseNeg), ", error rate", (falsePos + falseNeg)*1./len(gold[diag][label])

if overallVerbose:
    print "---------------------------"
    print "Overall"
    print "Number of gold",  sum(overallGold)
    print "Number guessed",  sum(overallGuessed)
    assert len(overallGold) == len(overallGuessed)

truePos = sum([overallGold[i] == 1 and overallGuessed[i] == 1 for i in range(len(overallGold))])
falsePos = sum([overallGold[i] == 0 and overallGuessed[i] == 1 for i in range(len(overallGold))])
trueNeg  = sum([overallGold[i] == 0 and overallGuessed[i] == 0 for i in range(len(overallGold))])
falseNeg = sum([overallGold[i] == 1 and overallGuessed[i] == 0 for i in range(len(overallGold))])


percision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else defualt
recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else defualt
f1        =  2. * (percision * recall)  / (percision + recall) if (percision + recall) >0 else defualt

sensitivity = recall
specifcity = 1.* trueNeg / (trueNeg + falsePos) if (trueNeg + falsePos) >0 else defualt
if overallVerbose:
    print "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
print stem, "Overall", "percision, recall, f1:", percision, ',', recall, ',', f1
if overallVerbose:
    print stem, "Overall", "sensitivity, specifcity:", sensitivity, ',', specifcity
print stem, "Overall", "Num Mistakes:", (falsePos + falseNeg), ", error rate", (falsePos + falseNeg)*1./(truePos+falsePos+falseNeg+trueNeg)

