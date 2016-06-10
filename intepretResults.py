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

assert sum([not gold[i] == guessed[i] for i in range(len(gold))]) == 9



truePos = sum([guessed[i] == "DCIS" and gold[i] == "DCIS" for i in range(len(gold))])
falsePos = sum([guessed[i] == "DCIS" and gold[i] == "no" for i in range(len(gold))])
trueNeg  = sum([guessed[i] == "no" and gold[i] == "no" for i in range(len(gold))])
falseNeg = sum([guessed[i] == "no" and gold[i] == "DCIS" for i in range(len(gold))])


percision = 1. * truePos / (truePos + falsePos)
recall    =  1. * truePos / (truePos + falseNeg)
f1        =  2. * (percision * recall)  / (percision + recall)

print "percision, recall, f1", percision, recall, f1

mistakes = [("gold, guessed", gold[i], guessed[i]) for i in range(len(gold)) if not gold[i] == guessed[i] ]
assert len(mistakes) == 9

print "Mistakes are"
for mistake in mistakes:
    print mistake

print "number of people with DCIS" , sum([g == "DCIS" for g in gold])

idxMistakes = [ i for i in range(len(gold)) if \
            guessed[i] == "DCIS" and gold[i] == "no"  or \
            guessed[i] == "no" and gold[i] == "DCIS" ]

print "ID of mistakes", idxMistakes