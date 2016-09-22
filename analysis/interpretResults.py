import pickle as p
import sys
sys.path.append("..")
from constants import *
from csv import DictWriter


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
    print "diagnoses", diagnoses
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
        gold[d]['overall'] = []
        guessed[d]['overall'] = []


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
                gold[diag]['overall'].append(goldsVec[labelIndx])
    
                predictionIndx = guessedVec.index(max(guessedVec))
                if labelIndx == predictionIndx:
                    prediction = 1
                else:
                    prediction = 0

                guessed[diag][label].append(prediction)
                guessed[diag]['overall'].append(prediction)


    results = []
    overallGold = []
    overallGuessed = []
    for diag in diagnoses:
        if MODE == "TAGHIAN":
            labels = diagLabelDict[diag]
        for label in labels +['overall'] if True else ['overall']:
            if len(labels) == 2 and label == labels[-1] and False: 
                continue
            if submode == "Analyze both" and diag in hueLabels and label == 0 and False:
                continue
            resultDict = {}
            resultDict['Name'] = diag + " " + str(label)
            defualt = 1
            if catergoryVerbose:
                print "---------------------------"
                print diag, label
                print "Number of gold",  sum(gold[diag][label])
                print "Number guessed",  sum(guessed[diag][label])
                assert len(guessed[diag][label]) == len(gold[diag][label])
                resultDict['num gold'] =  sum(gold[diag][label])
                resultDict['num geussed'] = sum(guessed[diag][label])

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

            numMistakes = (falsePos + falseNeg)
            errorRate = (falsePos + falseNeg)*1./ (len(gold[diag][label]) if len(gold[diag][label]) > 0 else defualt)

            resultDict['percision'] = percision
            resultDict['recall'] = recall
            resultDict['f1'] = f1
            resultDict['sensitivity'] = sensitivity
            resultDict['specifcity'] = specifcity
            resultDict['numMistakes'] = numMistakes
            resultDict['errorRate']   = errorRate

            results.append(resultDict)

            if catergoryVerbose:
                print diag, label, "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
                print diag, label, "percision, recall, f1:", percision, ',', recall, ',', f1
                print diag, label, "sensitivity, specifcity:", sensitivity, ',', specifcity
                print "Diag", diag, label, ", Num Mistakes:", numMistakes, ", error rate", errorRate
    oResultDict = {}
    oResultDict['Name'] = 'Overall'
    if overallVerbose:
        print "---------------------------"
        print "Overall"
        print "Number of gold",  sum(overallGold)
        print "Number guessed",  sum(overallGuessed)
        assert len(overallGold) == len(overallGuessed)

        oResultDict['num gold'] = sum(overallGold)
        oResultDict['num geussed'] = sum(overallGuessed)

    truePos = sum([overallGold[i] == 1 and overallGuessed[i] == 1 for i in range(len(overallGold))])
    falsePos = sum([overallGold[i] == 0 and overallGuessed[i] == 1 for i in range(len(overallGold))])
    trueNeg  = sum([overallGold[i] == 0 and overallGuessed[i] == 0 for i in range(len(overallGold))])
    falseNeg = sum([overallGold[i] == 1 and overallGuessed[i] == 0 for i in range(len(overallGold))])


    percision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else defualt
    recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else defualt
    f1        =  2. * (percision * recall)  / (percision + recall) if (percision + recall) >0 else defualt

    avgF1 = sum([r['f1'] for r in results])/ len(results)


    sensitivity = recall
    specifcity = 1.* trueNeg / (trueNeg + falsePos) if (trueNeg + falsePos) >0 else defualt

    numMistakes = (falsePos + falseNeg)
    errorRate = (falsePos + falseNeg)*1./(truePos+falsePos+falseNeg+trueNeg)

    oResultDict['percision'] = percision
    oResultDict['recall'] = recall
    oResultDict['f1'] = f1
    oResultDict['sensitivity'] = sensitivity
    oResultDict['specifcity'] = specifcity
    oResultDict['numMistakes'] = numMistakes
    oResultDict['errorRate']   = errorRate

    results.append(oResultDict)
    if overallVerbose:
        print "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
    print stem, "Overall", "percision, recall, f1:", percision, ',', recall, ',', f1
    if overallVerbose:
        print stem, "Overall", "sensitivity, specifcity:", sensitivity, ',', specifcity
    print stem, "Overall", "Num Mistakes:", (falsePos + falseNeg), ", error rate", (falsePos + falseNeg)*1./(truePos+falsePos+falseNeg+trueNeg)
    print "Average F1 vs aggregated one:", avgF1, f1

    rowLevelDict = {}
    diagNames = []

    if MODE == "TAGHAIN":
        if submode == "Analyze both":
            diagNames = MixedAnotations
    if MODE == "Breast":
        diagNames = diagnoses


    numRowMistakes = 0
    numRows = len(gold[diagNames[0]][gold[diagNames[0]].keys()[0]] )
    offenders = {}
    offenderRows = {}
    #This is my correcting hand annotations
    corrections = [('Red_DCIS', 67), ('FlatEpithelial', 7), ('Red_ILC', 467), ('Red_ALH', 434)]

    for i in range(numRows):
        incorrect = False
        for d in diagNames:
            for l in gold[d]:
                if not l in analysisLabelDict[d]:
                    continue
                if (d,i) in corrections:
                    print "Noom"
                if not guessed[d][l][i] == gold[d][l][i] and not incorrect and not (d,i) in corrections:
                    if not d in offenders:
                        offenders[d] = 0
                        offenderRows[d] = []
                    mistake = {}
                    mistake['row'] = i
                    mistake['gold']=  gold[d][l][i]
                    mistake['pred']=  guessed[d][l][i]
                    offenderRows[d].append(mistake)
                    offenders[d] += 1
                    numRowMistakes +=1
                    incorrect = True

    print "Rowz level", numRowMistakes, numRows, numRowMistakes *1. / numRows, 1- numRowMistakes *1. / numRows
    print offenders
    p.dump(offenderRows, open('mistake.p', 'wb'))

    print "writing to a file"
    keys = ['Name', 'num gold', 'num geussed', 'percision', 'recall', 'f1', 'sensitivity','specifcity', 'numMistakes', 'errorRate']
    with open("allResults.csv", "wb") as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(results)
    
