import pickle as p
from createEpisodes import preprocessReports
from genBoostexaFiles import genTrainTestFiles

trainData = p.load(open('adams_training_set.p', 'rb'))
testData = p.load(open('adams_test_set.p', 'rb'))

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

    testReports = preprocessReports([tr[0] for tr in testData])
    testLabels = ['M' if tr[1] == 'M' else 'no_M' for tr in testData]

    writeBoostFiles(trainReports, trainLabels, stem+"data")
    writeBoostFiles(testReports, testLabels, stem+"test")