import datetime


MODE = "TAGHIAN"

if MODE == "Breast":
    #Outcomes constants
    diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
                 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
                 u'ADH', u'CancerInvInsituNOS',\
                 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']
    #Contants for creating episodes
    #Contants for creating episodes
    dataPath = "rawBreastPathReport.p"
    outPath = "reportDB.p"
    episodePath = "episodeDB.p"
    goldDataPath = 'goldPathReports.p'
    JSONReportPath = "reportDB.json"
    JSONEpisodePath = "episodeDB.json"
    allDataStem = "boostexer/pathology_all"


    metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution', 'DOBPlusX']

    SIX_MONTHS = datetime.timedelta(365/2)


    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"] 

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/pathology.data"
    testOutPath = "boostexer/pathology.test"
    devOutPath = "boostexer/pathology.dev"
elif MODE == "ALL_CANCER":
    print "MODE IS ALL CANCER"

elif MODE == "TAGHIAN":
    redmap = p.load(open('redmap.p', 'rb'))
    types = set([redmap[m]['extraction feild'] for m in redmap if redmap[m]['event'] in lauraDictToIndx and not redmap[m]['extraction feild'] == None])
    diagnoses = [ extraction for extraction in types if len(dB[extraction]) > 500 and extraction not in filtOutList]
    diagLabelDict = {}
    for diag in diagnoses:
        validLabels = set(['_'.join(str(r[key]).split()) for r in db if not r[key] == None])
        diagLabelDict[diag] = validLabels
    #Outcomes constants
    #Contants for creating episodes
    #Contants for creating episodes
    dataPath = "rawBreastPathReport.p"
    outPath = "reportDB.p"
    episodePath = "episodeDB.p"
    goldDataPath = 'goldPathReports.p'
    JSONReportPath = "reportDB.json"
    JSONEpisodePath = "episodeDB.json"
    allDataStem = "boostexer/pathology_all"
    lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }


    filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
    'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val']

    metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution']

    SIX_MONTHS = datetime.timedelta(365/2)


    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/pathology.data"
    testOutPath = "boostexer/pathology.test"
    devOutPath = "boostexer/pathology.dev"