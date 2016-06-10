import pickle as p
from clean import outPath as dataPath
import re
import random

random.seed(1)
goldDataPath = 'goldPathReports.p'
trainOutPath = "boostexer/pathology.data"
testOutPath = "boostexer/pathology.test"

dumpGold = False

if dumpGold:
    allData = p.load(open(dataPath, 'rb'))
    goldData = [d for d in allData if 'Correct' in d]
    p.dump(goldData, open(goldDataPath, 'wb'))
else:
    goldData = p.load(open(goldDataPath, 'rb'))

print "Report keys:", goldData[0].keys()
labels = ['DCIS' if d['DCIS'] == '1' else "no_DCIS" for d in goldData]
reports = [d['Report_Text'] for d in goldData]

cleanReports = [ re.sub(r"\W", " ", d) for d in reports]
cleanReports = [ ' '.join(d.split('\n')) for d in cleanReports]
cleanReports = [ re.sub(r"(----)+", "", d) for d in cleanReports]
cleanReports = [ re.sub(r"(====)+", "", d) for d in cleanReports]


dups= {}
dupLabels= {}
for i,report in enumerate(set(cleanReports)):
    count = 0
    dupLabels[report] = set([labels[i]])
    for j,r2 in enumerate(cleanReports):
        if r2 == report:
            count +=1
            dupLabels[report].add(labels[j])
        if count > 1:
            dups[report] = count

nonSepDups = []
for dup in dupLabels:
    if len(dupLabels[dup]) >1:
        nonSepDups.append(dup)

print 'len(nonSepDups)', len(nonSepDups)

filteredReport = []
filteredLabel  = []
for i in range(len(cleanReports)):
    if not cleanReports[i] in dups:
        filteredReport.append(cleanReports[i].lower())
        filteredLabel.append(labels[i])
assert len(filteredReport) < len(cleanReports)
cleanReports = filteredReport
labels = filteredLabel


assert len(cleanReports) == len(set(cleanReports))


assert len(cleanReports) == len(labels)
debug = False
if debug:
    for i in range(len(reports)):
        print "___________________________________"
        print reports[1]
        print cleanReports[1]
        raw_input()

test_Size = 500

idx = range(len(cleanReports))
random.shuffle(idx)

trainReports = [cleanReports[i] for i in idx[:-500]]
trainLabels = [labels[i] for i in idx[:-500]]
print "Label dist for train", sum([l == 'DCIS' for l in trainLabels])
print len(trainLabels)

testReports = [cleanReports[i] for i in idx[-500:]]
testLabels = [labels[i] for i in idx[-500:]]
print "Label dist for test",  sum([l == 'DCIS' for l in testLabels])
print len(testLabels)


mistakeIds = [102, 273, 310]
goldLabels = [testLabels[idx] for idx in mistakeIds]
yalaLabel = ['DCIS', 'no_DCIS', 'DCIS', 'DCIS',  'no_DCIS']

print 'goldLabels', goldLabels


for idx in mistakeIds:
    print "************************"
    print "MISTAKE ", idx
    print "gold", testLabels[idx]
    print testReports[idx]
    raw_input()

write = True
if write:

    with open(trainOutPath, "wb") as f: 
        for i in range(len(trainReports)):
            label = trainLabels[i]
            report = trainReports[i]
            assert not "\n" in report
            f.write(report + ", " + label + '.\n')
    print "Saved", trainOutPath

    with open(testOutPath, "wb") as f: 
        for i in range(len(testReports)):
            label = testLabels[i]
            report = testReports[i]
            assert not "\n" in report
            f.write(report + ", " + label + '.\n')
    print "Saved", testOutPath