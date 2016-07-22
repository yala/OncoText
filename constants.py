import datetime


MODE = "Breast"

if MODE == "Breast":
    #Outcomes constants
    diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
                 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
                 u'ADH', u'CancerInvInsituNOS',\
                 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']
    #Contants for creating episodes
    dataPath = "rawBreastPathReport.p"
    outPath = "reportDB.p"
    episodePath = "episodeDB.p"
    goldDataPath = 'goldPathReports.p'
    JSONReportPath = "reportDB.json"
    JSONEpisodePath = "episodeDB.json"
    allDataStem = "boostexer/pathology_all"


    metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution']

    SIX_MONTHS = datetime.timedelta(365/2)


    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/pathology.data"
    testOutPath = "boostexer/pathology.test"
    devOutPath = "boostexer/pathology.dev"
elif MODE == "ALL_CANCER":
    print "MODE IS ALL CANCER"