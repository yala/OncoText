with open("classifier_results.txt", 'rb') as f:
   samples = f.readlines()

gold = []
guessed = []
for sample in samples:
    correctDCISLabel, correctNoLabel, dcisProb, noProb = \
    [float(f) for f in sample.split()]

    g = 'DCIS' if correctDCISLabel == 1 else 'no'
    p = "DCIS" if dcisProb > 0 else 'no'

    gold.append(g)
    guessed.append(p)

mistakeIds = [85, 102, 213, 273, 310]
yalaLabel = ['DCIS', 'no_DCIS', 'DCIS', 'DCIS',  'no_DCIS']

for i in range(len(mistakeIds)):
    idx = mistakeIds[i]
    yalaAnnotation = yalaLabel[i]

    gold[idx] = yalaAnnotation

truePos = sum([guessed[i] == "DCIS" and gold[i] == "DCIS" for i in range(len(gold))])
falsePos = sum([guessed[i] == "DCIS" and gold[i] == "no" for i in range(len(gold))])
trueNeg  = sum([guessed[i] == "no" and gold[i] == "no" for i in range(len(gold))])
falseNeg = sum([guessed[i] == "no" and gold[i] == "DCIS" for i in range(len(gold))])


percision = 1. * truePos / (truePos + falsePos)
recall    =  1. * truePos / (truePos + falseNeg)
f1        =  2. * (percision * recall)  / (percision + recall)

sensitivity = recall
specifcity = 1.* trueNeg / (trueNeg + falsePos)

print "percision, recall, f1:", percision, ',', recall, ',', f1
print "sensitivity, specifcity:", sensitivity, ',', specifcity


mistakes = [("gold, guessed", gold[i], guessed[i]) for i in range(len(gold)) if not gold[i] == guessed[i] ]

print "Mistakes are"
for mistake in mistakes:
    print mistake

print "number of people with DCIS" , sum([g == "DCIS" for g in gold])

idxMistakes = [ i for i in range(len(gold)) if \
            (not guessed[i] == gold[i]) ]

print 'idxMistakes', idxMistakes