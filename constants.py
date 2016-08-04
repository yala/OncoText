import datetime
import pickle as p

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

    lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }
    filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
    'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'Max Tumor Size', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'ECE']
    # TODO Remove ECE and debug why bad class name    

    diagnoses = [u'Are there positive LN?', u'Type of sampled LN (choice=None)', u'Pagets', u'Lymphovascular invasion', u'Number of LN with 0.02- 0.2 cm', 
    u'EIC', u'ITC ', u'Focality', u'Sentinel LN (# Sampled)', u'PR', u'Comedonercrosis', u'Purpose of surgey', u'SLN staining (if positive) (choice=Frozen Section)', 
    u'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))', u'Micro or Gross', u'Other Cancr', u'Radical Mastectomy', u'Type of Surgery', u'Simple Mastectomy', u'Type of biopsy', u'No malignancy', 
    u'Solid/Cribiform', u'Number of LN with < =0.02 cm', u'Method size', u'Her2 (Fish)', u'SLN staining (if positive) (choice=Keratin)', u'Mastectomy incision', u'LVI', u'ER', u'Micopapillary', u'Skin sparing Mastectomy', u'Invasive', 
    u'SLN staining (if positive) (choice=H & E)', u'Type of sampled LN (choice=Non SLN (Non Sentinel LN))', u'Sentinel LN (# Malignant)', u'Nipple sparing Mastectomy', u'Type of sampled LN (choice=ALND (Axillary LN Dissection))', u'Skin', u'ALND (#malignant)', u'BVI',
     u'Modified radical Mastectomy', u'Type of sampled LN (choice=Intraparynchemal)', u'NOS']

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

    metaData = ['Report_Date_TimePlusX', 'MRNPlusX', 'Correct', 'Institution']

    SIX_MONTHS = datetime.timedelta(365/2)


    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]

    # Constants for genBoostexaFiles
    trainOutPath = "boostexer/pathology.data"
    testOutPath = "boostexer/pathology.test"
    devOutPath = "boostexer/pathology.dev"