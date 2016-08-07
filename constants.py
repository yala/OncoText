import datetime
import pickle as p

MODE = "TAGHIAN"

#Shared constants for creating episodes
dataPath = "rawBreastPathReport.p"
outPath = "reportDB.p"
episodePath = "episodeDB.p"
goldDataPath = 'goldPathReports.p'
JSONReportPath = "reportDB.json"
JSONEpisodePath = "episodeDB.json"
allDataStem = "boostexer/pathology_all"

metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution', 'DOBPlusX']

SIX_MONTHS = datetime.timedelta(365/2)


if MODE == "Breast":
    #Outcomes constants
    diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
                 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
                 u'ADH', u'CancerInvInsituNOS',\
                 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']
    #Contants for creating episodes

    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"] 

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/pathology.data"
    testOutPath = "boostexer/pathology.test"
    devOutPath = "boostexer/pathology.dev"

elif MODE == "ALL_CANCER":
    print "MODE IS ALL CANCER"

elif MODE == "TAGHIAN":

    lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }
    filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
    'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'Max Tumor Size', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'ECE', 'Micro or Gross',
    'Number of LN with < =0.02 cm', 'Method size']
    # TODO Remove ECE and debug why bad class name    Micro or Gross   Number of LN with < =0.02 cm Method size

    diagnoses = [u'Are there positive LN?', u'Type of sampled LN (choice=None)', u'ITC ', u'PR',  
    u'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))', u'Radical Mastectomy', u'Type of Surgery', u'Simple Mastectomy', u'Type of biopsy', 
    u'Her2 (Fish)', u'ER',u'Nipple sparing Mastectomy', u'Type of sampled LN (choice=ALND (Axillary LN Dissection))', 'ECE']


    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]

elif MODE == "both":

    lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }
    filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
    'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'Max Tumor Size', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'ECE', 'Micro or Gross',
    'Number of LN with < =0.02 cm', 'Method size']
    # TODO Remove ECE and debug why bad class name    Micro or Gross   Number of LN with < =0.02 cm Method size

    redLabels = [u'Are there positive LN?', u'Type of sampled LN (choice=None)', u'ITC ', u'PR',  
    u'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))', u'Radical Mastectomy', u'Type of Surgery', u'Simple Mastectomy', u'Type of biopsy', 
    u'Her2 (Fish)', u'ER',u'Nipple sparing Mastectomy', u'Type of sampled LN (choice=ALND (Axillary LN Dissection))', 'ECE']
    

     diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
                 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
                 u'ADH', u'CancerInvInsituNOS',\
                 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']


    cols = diagnoses + redLabels + metaData + ['Report_Text', "Preprocessed_Report_Text"]
