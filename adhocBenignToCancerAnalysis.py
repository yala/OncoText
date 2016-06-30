import pickle as p
from operator import itemgetter
import datetime
import random

random.seed(1)


dbPath = 'episodicDB.p'
epsDBPath = 'episodeDbByEp.p'
mrnDBPath = 'mrnDB.p'
benignPath = 'benignDB.p'
reportPairsPath = 'reportPairs.p'


typesOfCarcinoma = ["DCIS", "ILC", "IDC", "LCIS", "TubularCancer", \
                            "CancerNOS", "InsituNOS", "CancerInvInsituNOS",\
                            "ClingingCarcinoma", "Medullary", "ADH_DCIS"] 

typesOfAtypia    = ["ADH", "ALH", "FlatEpithelial", "Phylodes", "LobularNeoplasia", "BluntAdenosis" ]

# Build episode linked DB and patient linked DB
def buildDBs(db):

    eps = {}
    mrns = {}
    for report in db:
        ## Stuff for episodic DB
        if report['EpisodeID'] in eps:
            eps[report['EpisodeID']].append(report)
        else:
            eps[report['EpisodeID']] = [report]

        ## Stuff for Patient DB
        if not report['MRNPlusX'] in mrns:
            mrns[report['MRNPlusX']] = {}

        if report['BreastSide'] in mrns[report['MRNPlusX']]:
            mrns[report['MRNPlusX']][report['BreastSide']].append(report)
        else:
            mrns[report['MRNPlusX']][report['BreastSide']]= [report]

    p.dump(eps, open(epsDBPath, 'wb'))
    p.dump(mrns, open(mrnDBPath, 'wb'))
 
    return eps, mrns

def isBenign(report):
    debug = False
    cancer = bool( sum([report[c] == c  or str(report[c]) == '1'  for c in typesOfCarcinoma]))
    if debug:
        print report
        print cancer
        raw_input()
    return not cancer

#Count number of patients that start benign and have more that one report in that breast.
# Of those, count number that lator develop cancer
def getSeedSet(db):
    startBenign = {}
    for mrn in db:
        breasts = db[mrn]
        for side in breasts:
            reports = sorted( breasts[side], key=itemgetter('Report_Date_TimePlusX') )

            if isBenign(reports[0]) and len(reports) > 1:
                startBenign[mrn] = {}
                startBenign[mrn][side] = reports
                break

    p.dump(startBenign, open(benignPath, 'wb'))
    return startBenign


def devsCancer(reports):
    for report in reports:
        if not isBenign(report):
            return True
    return False


def doBasicStats(db):
    
    numReports = 0
    numBreasts = 0
    numCancer = 0
    reportNumsByPatient = {}
    cancerReportCountHisto = {}
    for mrn in db:
        patientNum = 0
        for side in db[mrn]:
            numBreasts += 1
            numReports += len(db[mrn][side])
            patientNum += len(db[mrn][side])

            if devsCancer(db[mrn][side]):
                numCancer += 1

        if patientNum in reportNumsByPatient:
            reportNumsByPatient[patientNum] += 1
        else:
            reportNumsByPatient[patientNum] = 1

        side = db[mrn].keys()[0]
        if devsCancer(db[mrn][side]):
            if patientNum in cancerReportCountHisto:
                cancerReportCountHisto[patientNum] += 1
            else:
                cancerReportCountHisto[patientNum] = 1

    print  "Number of patients that start benign", len(db)

    print  "Number of reports total", numReports

    print "num reports per patient", reportNumsByPatient

    print "num breasts", numBreasts
    print "num breasts that later develop Cancer", numCancer, "ratio", numCancer *1. / numBreasts

    print "num reports histogram for people that dev cancer", cancerReportCountHisto


def makeReportPairs(db):
    pairs = []
    labelDist = {0:0, 1:0}

    maxTimeGap = 365
    for mrn in db:
        for side in db[mrn]:
            reports = db[mrn][side]
            for i, report in enumerate(reports):
                if i == 0:
                    assert isBenign(report)
                    continue
                if isBenign(reports[i-1]):
                    reportPair = (reports[i-1], report)
                    staysB = isBenign(report)
                    label  = 0 if staysB else 1
                    labelDist[label] +=1
                    pairs.append( (reportPair, label) )
    print "label distribution", labelDist, "Percent dev cancer", labelDist[1]*1/len(pairs)
    print "Num pairs", len(pairs)
    p.dump(pairs, open(reportPairsPath, 'wb'))
    return pairs

def buildDataForClassifier(pairs, textBased):
    data = []
    dev = True
    for pair, label in pairs:
        orig = pair[0]
        if textBased:
            features = orig['Preprocessed_Report_Text']
        else:
            features = {}
            for a in typesOfAtypia:
                features[a] = orig[a]

        data.append( (features, label))

    random.shuffle(data)

    if dev:
        trainCut = int(len(data) * .7)
        testCut = int(len(data) * .8)
        
    else:
        trainCut = int(len(data) * .8)
        testCut  = len(data)

    trainReports = [d[0] for d in data[:trainCut]]
    trainLabels = [d[1] for d in data[:trainCut]]

    assert len(trainReports) == len(trainLabels)

    testReports = [d[0] for d in data[trainCut:testCut]]
    testLabels = [d[1] for d in data[trainCut:testCut]]

    assert len(testReports) == len(testLabels)

    print '================================='
    print "Datset stats"
    print "Num train", len(trainReports)
    print "train fraction ones", sum(trainLabels)*1./len(trainReports)

    print "Num test", len(testReports)
    print "test fraction ones", sum(testLabels)*1./len(testReports)

    writeFiles(trainReports, trainLabels, testReports, testLabels, "boostexer/adhoc_benignStart", textBased)


def writeFiles(trainReports, trainLabels, testReports, testLabels, stem, textBased):
    with open(stem+'.names','wb') as f:
        labels = '1, 0.\n'
        if textBased:
            features = "pathReport: text.\n"
        else:
            features = ""
            for a in typesOfAtypia:
                features += a+": 1, 0.\n"
        f.write(labels)
        f.write(features)

    print "Saved "+ stem+'.names'

    with open(stem+'.data','wb') as f:
        for r,l in zip(trainReports, trainLabels):
            if textBased:
                features = r
            else:
                features = ""
                for a in typesOfAtypia:
                    feature = r[a]
                    feature = "1" if r[a] == a or str(r[a]) == "1" else "0"
                    features += feature+", "
            f.write(features + str(l) + ".\n")
    
    print "Saved "+ stem+'.data'

    with open(stem+'.test','wb') as f:
        for r,l in zip(testReports, testLabels):
            if textBased:
                features = r
            else:
                features = ""
                for a in typesOfAtypia:
                    feature = r[a]
                    feature = "1" if r[a] == a or str(r[a]) == "1" else "0"
                    features += feature+", "

            f.write(features + str(l) + ".\n")
    
    print "Saved "+ stem+'.test'


if __name__ == "__main__":

    getEpisodesBool = False
    getSeedSetBool = False

    if getEpisodesBool:
        db = p.load(open(dbPath, 'rb'))
        eps, mrns = buildDBs(db)
    elif getSeedSetBool:
        eps = p.load(open(epsDBPath, 'rb'))
        mrns = p.load(open(mrnDBPath, 'rb'))
        seedSet = getSeedSet(mrns)
    else:
        seedSet = p.load(open(benignPath, 'rb'))

    basicStatsBool = False
    if basicStatsBool:
        doBasicStats(seedSet)

    makeReportPairsBool = False
    if makeReportPairsBool:
        pairs = makeReportPairs(seedSet)
    else:
        pairs = p.load(open(reportPairsPath, 'rb'))

    buildDataForClassifierBool = True
    textBased = False
    if buildDataForClassifierBool:
        buildDataForClassifier(pairs, textBased)

