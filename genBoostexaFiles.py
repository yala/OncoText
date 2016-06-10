import pickle as p
from clean import outPath as dataPath
import re
import random

random.seed(1)
goldDataPath = 'goldPathReports.p'
trainOutPath = "boostexer/pathology.data"
testOutPath = "boostexer/pathology.test"

dumpGold = True

if dumpGold:
    allData = p.load(open(dataPath, 'rb'))
    goldData = [d for d in allData if 'Correct' in d]
    p.dump(goldData, open(goldDataPath, 'wb'))
else:
    goldData = p.load(open(goldDataPath, 'rb'))

labels = [d['DCIS'] for d in goldData]
reports = [d['Report_Text'] for d in goldData]

cleanReports = [ re.sub(r"\W", " ", d) for d in reports]

debug = False
if debug:
    for i in range(len(reports)):
        print "___________________________________"
        print reports[1]
        print cleanReports[1]
        raw_input()

test_Size = 500

idx = range(len(reports))
random.shuffle(idx)

trainReports = [reports[i] for i in idx[:-500]]
trainLabels = [labels[i] for i in idx[:-500]]

testReports = [reports[i] for i in idx[-500:]]
testLabels = [labels[i] for i in idx[-500:]]

with open(trainOutPath, "wb") as f: 
    for i in range(len(trainReports)):
        label = trainLabels[i]
        report = trainReports[i]
        f.write(report + ", " + label + '.\n')

with open(testOutPath, "wb") as f: 
    for i in range(len(testReports)):
        label = testLabels[i]
        report = testReports[i]
        f.write(report + ", " + label + '.\n')