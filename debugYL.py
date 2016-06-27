import pickle as p
import xmltodict
from createEpisodes import preprocessReports
from genBoostexaFiles import genTrainTestFiles
import random
from pandas import *

random.seed(1)

# trainData = p.load(open('adams_training_set.p', 'rb'))
# testData = p.load(open('adams_test_set.p', 'rb'))

# data = trainData + testData
data = []
allData = []
xls = ExcelFile("pathreports.xlsx")
df = xls.parse(xls.sheet_names[0])
allData = df.to_dict()


for ind in range(436):
    label = allData['SXRESULT'][ind].strip()
    text  = allData['BXPATHREP'][ind].strip()
    
    data.append( (text, label) )

random.shuffle(data)

trainData = data[:326]
testData  = data[326:]

stem = "boostexer/predictM."


def writeNameFile():
    with open(stem+"names", 'wb') as f:
        f.write("M, no_M.\n")
        f.write("pathReport : text.\n")

def writeBoostFiles(reports, labels, path):
    with open(path, 'wb') as f:
        for r in range(len(reports)):
            report = reports[r]
            label = labels[r]
            f.write(report + ", " + label + ".\n")
    print "Saved", path


if __name__ == "__main__":    
    writeNameFile()


    trainReports = preprocessReports([tr[0] for tr in trainData])
    trainLabels = ['M' if tr[1] == 'M' else 'no_M' for tr in trainData]

    print "Train stats", sum([l == "M" for l in trainLabels])*1./len(trainLabels), len(trainLabels)

    testReports = preprocessReports([tr[0] for tr in testData])
    testLabels = ['M' if tr[1] == 'M' else 'no_M' for tr in testData]

    print "Test stats", sum([l == "M" for l in testLabels])*1./len(testLabels), len(testLabels)

    writeBoostFiles(trainReports, trainLabels, stem+"data")
    writeBoostFiles(testReports, testLabels, stem+"test")