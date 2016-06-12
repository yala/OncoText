import genBoostexaFiles

with open("classifier_results_all_classes.txt", 'rb') as f:
   samples = f.readlines()
diagnoses = genBoostexaFiles.diagnoses + ["no"]

gold = {}
guessed = {}
for d in diagnoses:
    gold[d] = []
    guessed[d] = []
for sample in samples:
    goldsAndPredictions = [float(f) for f in sample.split()]

    assert len(goldsAndPredictions) % 2 == 0
    golds = []
    guesses = []
    for j in range(len(goldsAndPredictions)/2):
        gold[diagnoses[j]].append(goldsAndPredictions[j])
        prediction = 1 if goldsAndPredictions[2*j] > 0 else 0
        guessed[diagnoses[j]].append(prediction)
        assert len(gold[diagnoses[j]]) == len(guessed[diagnoses[j]])


mistakeIds = [85, 102, 213, 273, 310]
yalaLabel  = [1, 0, 1, 1, 0]

for k in range(len(mistakeIds)):
    idx = mistakeIds[k]
    yalaAnnotation = yalaLabel[k]
    gold['DCIS'][idx] = yalaAnnotation

for diag in diagnoses:

    if sum(gold[diag]) == 0:
        continue

    defualt = 0

    print "---------------------------"
    print diag
    print "Number of gold",  sum(gold[diag])
    print "Number guessed",  sum(guessed[diag])
    assert len(guessed[diag]) == len(gold[diag])
    truePos = sum([guessed[diag][i] == 1 and gold[diag][i] == 1 for i in range(len(gold[diag]))])
    falsePos = sum([guessed[diag][i] == 1 and gold[diag][i] == 0 for i in range(len(gold[diag]))])
    trueNeg  = sum([guessed[diag][i] == 0 and gold[diag][i] == 0 for i in range(len(gold[diag]))])
    falseNeg = sum([guessed[diag][i] == 0 and gold[diag][i] == 1 for i in range(len(gold[diag]))])


    percision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else defualt
    recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else defualt
    f1        =  2. * (percision * recall)  / (percision + recall) if (percision + recall) >0 else defualt

    sensitivity = recall
    specifcity = 1.* trueNeg / (trueNeg + falsePos) if (trueNeg + falsePos) >0 else defualt
    print "truePos, falsePos, trueNeg, falseNeg:", truePos, falsePos, trueNeg, falseNeg
    print diag, "percision, recall, f1:", percision, ',', recall, ',', f1
    print diag, "sensitivity, specifcity:", sensitivity, ',', specifcity

    raw_input()
# mistakes = [("gold, guessed", gold[i], guessed[i]) for i in range(len(gold)) if not gold[i] == guessed[i] ]

# print "Mistakes are"
# for mistake in mistakes:
#     print mistake

# print "number of people with DCIS" , sum([g == "DCIS" for g in gold])

# idxMistakes = [ i for i in range(len(gold)) if \
#             (not guessed[i] == gold[i]) ]

# print 'idxMistakes', idxMistakes