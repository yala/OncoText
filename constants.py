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

def replaceSpaces(label):
    return '_'.join(str(label).split())

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
    trainOutPath = "boostexer/breast/labled/pathology.data"
    testOutPath = "boostexer/breast/labled/pathology.test"
    devOutPath = "boostexer/breast/labled/pathology.dev"

    allDataStem = "boostexer/breast/unlabled/pathology_all"


elif MODE == "ALL_CANCER":
    print "MODE IS ALL CANCER"

elif MODE == "TAGHIAN":

    lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }
    filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
    'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'Max Tumor Size', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'ECE', 'Micro or Gross',
    'Number of LN with < =0.02 cm', 'Method size', 'Radical Mastectomy']
    # TODO Remove ECE and debug why bad class name    Micro or Gross   Number of LN with < =0.02 cm Method size

    diagnoses = [u'Are there positive LN?', u'Type of sampled LN (choice=None)', u'ITC ', u'PR',  
    u'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))', u'Type of Surgery',  u'Type of biopsy', u'Simple Mastectomy',
    u'Her2 (Fish)', u'ER',u'Nipple sparing Mastectomy', u'Type of sampled LN (choice=ALND (Axillary LN Dissection))', 'ECE']

    redRawDBPath = 'reportDB+red+clean.p'

    defaultLabelDict = { 'Are there positive LN?': 'No', 'Type of sampled LN (choice=None)':'Unchecked', 'ITC ':'Not_Reported', 'PR':'Unknown',
        'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': 'Unchecked', 'Type of Surgery':'not_surgery', 'Type of biopsy':'No_breast_biopsy',
        'Simple Mastectomy':'Unchecked', 'Her2 (Fish)':'Unknown', 'ER': 'Unknown', 'Nipple sparing Mastectomy':'Unchecked',
        'Type of sampled LN (choice=ALND (Axillary LN Dissection))':'Unchecked', 'ECE':'Not_Reported'

    }

    constantValidLabelDict = {'Are there positive LN?': {'No', 'Yes'},
      'ECE': {'No','Not_Reported','Yes','Yes_(Macro)','Yes_(Micro)'},
      'ER': {'Negative', 'Positive', 'Unknown'},
      'Her2 (Fish)': {'Negative', 'Positive', 'Unknown'},
      'ITC ': {'No', 'Not_Reported', 'Yes'},
      'Nipple sparing Mastectomy': {'Checked', 'Unchecked'},
      'PR': {'Negative', 'Positive', 'Unknown'},
      'Simple Mastectomy': {'Checked', 'Unchecked'},
      'Type of Surgery': {'1st_Re-Excision', '2nd_Re-Excision', 'Excisional_biopsy_(Lumpectomy)','Mastectomy', 'not_surgery'},
      'Type of biopsy': {'Core_biopsy', 'Fine_needle_aspiration_(FNA)', 'Incisional_biopsy', 'Needle_biopsy','No_breast_biopsy', 'Other'},
      'Type of sampled LN (choice=ALND (Axillary LN Dissection))': {'Checked', 'Unchecked'},
      'Type of sampled LN (choice=None)': {'Checked', 'Unchecked'},
      'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))': {'Checked', 'Unchecked'}}

    cols = diagnoses + metaData + ['Report_Text', "Preprocessed_Report_Text"]

        # Constants for genBoostexaFiles
    trainOutPath = "boostexer/breast/taghian/red.data"
    testOutPath = "boostexer/breast/taghian/red.test"
    devOutPath = "boostexer/breast/taghian/red.dev"

    allDataStem = "boostexer/breast/unlabled/red_all"

elif MODE == "both":

    lauraDictToIndx = {'Biposy 1':0, 'Biopsy 2':1, 'Biopsy 3':2, 'Surgery 1':3, 'Surgery2':4, 'Surgery 3':5 }
    filtOutList = ['DCIS', 'LCIS', 'ILC', 'Mixed Inv Duct and Lob canc', 'IDC', 'ALH', 'hospital', 'Her2 (Fish)-val', \
    'IDC with lobular features', 'date', 'ADH', 'Her2 (immunochem)', 'Her2 (Fish)- val', 'Max Tumor Size', 'ALND (#sampled)', 'Number of LN with > 0.2 cm', 'ECE', 'Micro or Gross',
    'Number of LN with < =0.02 cm', 'Method size']
    # TODO Remove ECE and debug why bad class name    Micro or Gross   Number of LN with < =0.02 cm Method size

    redLabels = [u'Are there positive LN?', u'Type of sampled LN (choice=None)', u'ITC ', u'PR',  
    u'Type of sampled LN (choice=SLNB (Sentinel LN Biopsy))', u'Radical Mastectomy', u'Type of Surgery', u'Type of biopsy', u'Simple Mastectomy',
    u'Her2 (Fish)', u'ER',u'Nipple sparing Mastectomy', u'Type of sampled LN (choice=ALND (Axillary LN Dissection))', 'ECE']
    

    diagnoses = [ u'BreastSide', u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
                 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
                 u'ADH', u'CancerInvInsituNOS',\
                 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', u'FlatEpithelial', 
                 u'BluntAdenosis', u'Medullary', u'ALH', u'ADH_DCIS', u'Borderline']


    cols = diagnoses + redLabels + metaData + ['Report_Text', "Preprocessed_Report_Text"]
