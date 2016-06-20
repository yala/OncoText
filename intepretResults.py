import genBoostexaFiles
import pickle


yalaAnnotations = { "ADH": [392, 444, 369, 72, 107, 211, 226, 255, 452], \
                    "ALH": [477, 85],\
                    "DCIS": [101]}

diagToInt = {"ADH":8,\
             "ALH":16,\
             "DCIS":0}

skipList = [188] #This report says nothing, should have been filtered out


if __name__ == "__main__":
    with open("classifier_results_all_classes.txt", 'rb') as f:
       samples = f.readlines()
    diagnoses = genBoostexaFiles.diagnoses + ["no"]

    assert diagnoses == ["DCIS", "ILC", "Phylodes", \
    "CancerSuspicious", "CancerNOS", "TubularCancer", "IDC", "LCIS", \
    "ADH", "CancerInvInsituNOS", "ClingingCarcinoma", "InvasiveSuspicious", \
    "LobularNeoplasia", "FlatEpithelial", "BluntAdenosis", "Medullary", "ALH", \
    "ADH_DCIS", "no"]
    gold = {}
    guessed = {}
    for d in diagnoses:
        gold[d] = []
        guessed[d] = []
    c = 0
    for row, sample in enumerate(samples):
        # if row in skipList:
        #     continue

        goldsAndPredictions = [float(f) for f in sample.split()]

        assert len(goldsAndPredictions) % 2 == 0
        golds = []
        guesses = []
        numMistakes = 0
        for j in range(len(goldsAndPredictions)/2):
    
            # if diagnoses[j] in yalaAnnotations and row in yalaAnnotations[diagnoses[j]]:
            #     goldsAndPredictions[j] = 1
            #     c += 1
            if not goldsAndPredictions[:len(goldsAndPredictions)/2] == [ 1 if p < 0 else 0 for p in goldsAndPredictions[len(goldsAndPredictions)/2:]]:
                numMistakes += 1
            gold[diagnoses[j]].append(goldsAndPredictions[j])
            prediction = 1 if goldsAndPredictions[len(goldsAndPredictions)/2 + j] > 0 else 0
            guessed[diagnoses[j]].append(prediction)
            assert len(gold[diagnoses[j]]) == len(guessed[diagnoses[j]])

           
    print "Num Mistakes", numMistakes

    overallGold = []
    overallGuessed = []
    mistakeIds = {}
    for diag in diagnoses:
        if sum(gold[diag]) == 0:
            continue
        defualt = 1
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
        print "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
        print diag, "percision, recall, f1:", percision, ',', recall, ',', f1
        print diag, "sensitivity, specifcity:", sensitivity, ',', specifcity

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
    print "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
    print diag, "percision, recall, f1:", percision, ',', recall, ',', f1
    print diag, "sensitivity, specifcity:", sensitivity, ',', specifcity

    pickle.dump(mistakeIds, open("mistakes.p", "wb"))