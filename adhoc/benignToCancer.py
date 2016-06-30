import pickle as p
from operator import itemgetter


dbPath = '../episodicDB.p'
epsDBPath = '../episodeDbByEp.p'
mrnDBPath = '../mrnDBPath'
benignPath = '../benignDBPath'


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
    cancer = bool( sum( [report[c] == 1 for c in typesOfCarcinoma]))
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
                reportNumsByPatient[patientNum] += 1
            else:
                reportNumsByPatient[patientNum] = 1

    print  "Number of patients that start benign", len(db)

    print  "Number of reports total", numReports

    print "num reports per patient", reportNumsByPatient

    print "num breasts", numBreasts
    print "num breasts that later develop Cancer", numCancer, "ratio", numCancer *1. / numBreasts

    print "num reports histogram for people that dev cancer", cancerReportCountHisto



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

    basicStatsBool = True
    if basicStatsBool:
        doBasicStats(seedSet)





    
