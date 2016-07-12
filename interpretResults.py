import genBoostexaFiles
import pickle
import sys

yalaAnnotations = { "FlatEpithelial": [14, 394], \
                    "DCIS": [36, 41, 365]}

diagToInt = {"ADH":8,\
             "ALH":16,\
             "DCIS":0}

skipList = [188] #This report says nothing, should have been filtered out

diagSamples = {}

catergoryVerbose= False
overallVerbose= False


if __name__ == "__main__":

    diagnoses = genBoostexaFiles.diagnoses
    stem = sys.argv[1]
    print "Calling interpret for ", stem
    for diag in diagnoses:
        with open(stem+diag+".txt", 'rb') as f:
           diagSamples[diag] = f.readlines()


    gold = {}
    guessed = {}
    for d in diagnoses:
        gold[d] = []
        guessed[d] = []
    c = 0

    numMistakes = 0

    for diag in diagnoses:
        samples = diagSamples[diag]
        for row, sample in enumerate(samples):

            skip = False

            if skip and row in skipList:
                continue


            goldsAndPredictions = [float(f) for f in sample.split()]

            assert len(goldsAndPredictions) % 2 == 0
            golds = []
            guesses = []

            goldsVec = goldsAndPredictions[:len(goldsAndPredictions)/2]
            guessedVec = [ 1 if p >= 0 else 0 for p in goldsAndPredictions[len(goldsAndPredictions)/2:]]
            assert len(goldsVec) == len(guessedVec)
            #if not goldsVec == guessedVec and (diag == "FlatEpithelial"):
            #     or diag == "BluntAdenosis" or diag == "ADH_DCIS"):
            #    print diag, ",",row
            #     numMistakes += 1
            
            # if diag in yalaAnnotations and row in yalaAnnotations[diag]:
            #     gold[diag].append(1)
            # else:
            #     gold[diag].append(goldsVec[0])

            gold[diag].append(goldsVec[0])

            prediction = 1 if guessedVec[0] > 0 else 0
            guessed[diag].append(prediction)


    overallGold = []
    overallGuessed = []
    mistakeIds = {}
    for diag in diagnoses:
        # if sum(gold[diag]) == 0:
        #     continue
        defualt = 1
        if catergoryVerbose:
            print "---------------------------"
            print diag
            print "Number of gold",  sum(gold[diag])
            print "Number guessed",  sum(guessed[diag])
            assert len(guessed[diag]) == len(gold[diag])
        overallGold.extend(gold[diag])
        overallGuessed.extend(guessed[diag])
        truePos = sum([guessed[diag][i] == 1 and gold[diag][i] == 1 for i in range(len(gold[diag]))])
        falsePos = sum([guessed[diag][i] == 1 and gold[diag][i] == 0 for i in range(len(gold[diag]))])
        trueNeg  = sum([guessed[diag][i] == 0 and gold[diag][i] == 0 for i in range(len(gold[diag]))])
        falseNeg = sum([guessed[diag][i] == 0 and gold[diag][i] == 1 for i in range(len(gold[diag]))])

        mistakeIds[diag] = [i for i in range(len(gold[diag])) if not guessed[diag][i] ==  gold[diag][i] ]


        percision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else defualt
        recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else defualt
        f1        =  2. * (percision * recall)  / (percision + recall) if (percision + recall) >0 else defualt

        sensitivity = recall
        specifcity = 1.* trueNeg / (trueNeg + falsePos) if (trueNeg + falsePos) >0 else defualt
        if catergoryVerbose:
            print "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
            print diag, "percision, recall, f1:", percision, ',', recall, ',', f1
            print diag, "sensitivity, specifcity:", sensitivity, ',', specifcity
            print "Diag", diag, ", Num Mistakes:", (falsePos + falseNeg), ", error rate", (falsePos + falseNeg)*1./len(gold[diag])

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

pickle.dump(mistakeIds, open("mistakes.p", "wb"))