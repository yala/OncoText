from operator import itemgetter
import pickle
from oncotext.utils.generic import hasCat
import datetime
import pdb

def prune_non_breast(reportDB, name, config, logger):
    logger.info("prune_non_breast - Loading non breast reports")
    if os.path.exists(config['DB_NON_BREAST_PATH']):
        non_breast_db = pickle.load(open(config['DB_NON_BREAST_PATH'],'rb'))
    else:
        non_breast_db = {name: []}
    logger.info("prune_non_breast - Loading db_unlabeled reports")
    db_unlabeled = pickle.load(open(config['DB_UNLABLED_PATH'],'rb'))

    id_to_report = { r['ID']: r for r in reportDB }
    prune_key = config['PRUNE_KEY']
    count = 0

    def prune(report):
        return report[prune_key] == '0'

    pruned_db_unlabeled = [r for r in db_unlabeled[name]
                if not prune(id_to_report[r['ID']])
            ]
    new_non_breast_db = [r for r in db_unlabeled[name]
                if prune(id_to_report[r['ID']])
            ]

    non_breast_db[name].extend(new_non_breast_db)

    logger.info(
            "prune_non_breast - Pruned db_unlabeled ({}) to breast {} and non {}. Total non breast {}".format(
                        len(db_unlabeled[name]),
                        len(pruned_db_unlabeled),
                        len(new_non_breast_db),
                        len(non_breast_db[name])
                        )
            )
    db_unlabeled[name] = pruned_db_unlabeled

    pickle.dump(db_unlabeled, open(config['DB_UNLABLED_PATH'],'wb'))
    pickle.dump(non_breast_db, open(config['DB_NON_BREAST_PATH'],'wb'))

    prune_report_db = [r for r in reportDB if not prune(r)]

    return prune_report_db

def apply_corrections(reportDB, trainDB, config, logger):
    text_key = config['PREPROCESSED_REPORT_TEXT_KEY']
    diagnoses = config['DIAGNOSES']
    corrections = 0
    num_match = 0
    textToLabel = {}

    for g in trainDB:
        textToLabel[g[text_key]] = g

    for t in reportDB:
        text = t[text_key]
        if text in textToLabel:
            t['train'] = "1"
            for d in textToLabel[text]:
                if d in diagnoses:
                    if d in t and t[d] != textToLabel[text][d]:
                        corrections += 1
                    t[d] = textToLabel[text][d]
                    num_match += 1
        else:
            t['train'] = "0"
    logger.info("apply corrections - num corrections: {} . num match: {}".format(corrections, num_match))

    return reportDB

# Runs enforces global constraints like ER/PR NA given no cancer
def generate_automatic_feilds(reportDB, organ, config):

    for r in reportDB:
        if "filename" not in r:
            r['filename'] = "Unknown"

    if organ == 'OrganBreast':
        for r in reportDB:
            if hasCat(r, config['CANCERS']):
                r['cancer'] = '1'
            else:
                r['cancer'] = '0'

            if hasCat(r, config['ATYPIAS']):
                r['atypia'] = '1'
            else:
                r['atypia'] = '0'

            if r['cancer'] == '0':
                for k in config['MARKERS']:
                    r[k] = '9'

            if 'Her2Fish' in r and r['Her2Fish'] != '9':
                r['her2'] = r['Her2Fish']
            else:
                if 'Her2_IHC' not in r or r['Her2_IHC'] == '9':
                    r['her2'] = '9'
                elif r['Her2_IHC'] == '3':
                    r['her2'] = '1'
                elif r['Her2_IHC'] in ['0', '1', '2']:
                    r['her2'] = '0'
                
            if 'DCIS' in r and r['DCIS'] == '0':
                r['GradeMaxDCIS'] = '9'

            if 'CancerInvasive' in r and r['CancerInvasive'] == '0':
                r['GradeMaxInvasive'] = '9'

    elif organ == "OrganProstate":
        for r in reportDB:
            if r['BiopsyType'] == 'Core':
                r['OrganProstateCore'] = '1'
                r['OrganProstateNonCore'] = '0'
            else:
                r['OrganProstateCore'] = '0'
                r['OrganProstateNonCore'] = '1'

            if r['ProstateCa'] == '0':
                numerical = [k for k in config['POST_DIAGNOSES']['OrganProstate'] if config['POST_DIAGNOSES']['OrganProstate'][k] == ["NUM"]]
                for k in numerical:
                    r[k] = '0'
                
    return reportDB


def aggregate_episodes_breast(reports, config):

    patientDict = {}
    sideKey = config['SIDE_KEY']
    patientIDkey = config['PATIENT_ID_KEY']
    dateKey = config['REPORT_TIME_KEY']
    episode_span = config['SIX_MONTHS']
   
    for r in reports:
        if isinstance(r[dateKey], str):
            r[dateKey] = datetime.datetime.strptime(r[dateKey], '%Y-%m-%dT%H:%M:%S')

    ## Group reports by patient
    for i,r  in enumerate(reports):
        patientID = r[patientIDkey]
        side = r[sideKey]

        if not patientID in patientDict:
            patientDict[patientID] = {}

        if not side in patientDict[patientID]:
            patientDict[patientID][side] = []

        patientDict[patientID][side].append(r)

    # Structure: List of Reports with Episode IDs
    reportsDB = []
    episodeDateDict = {}  # Use this to store Date -> episode Id for each MRN. use this to reorder episodes by date
    episodeRelabelDict = {}  # Use this to store episoideID to new Episode ID
    for patientID in patientDict:
        patient = patientDict[patientID]
        episodeId = -1
        episodeDateDict[patientID] = []
        for side in patient:
            patient[side] = sorted(patient[side], key=itemgetter(dateKey))
            for idx, rep in enumerate(patient[side]):

                if idx == 0:
                    episodeId += 1
                    rep['EpisodeID'] = 't'+str(episodeId)
                    episodeDateDict[patientID].append(
                                            {'EpStartTime': rep[dateKey],
                                            'epID': 't'+str(episodeId)})
                else:
                    prevVisit = patient[side][idx - 1]
                    if rep[dateKey] - prevVisit[dateKey] < episode_span:
                        rep['EpisodeID'] = prevVisit['EpisodeID']
                    else:
                        episodeId += 1
                        rep['EpisodeID'] = 't'+str(episodeId)
                        episodeDateDict[patientID].append(
                                    {'EpStartTime': rep[dateKey],
                                    'epID': 't'+str(episodeId)})

                reportsDB.append(rep)

    # Relabel MRNs with chronological episode numbers (first was chronological per breast)
    for patientID in patientDict:
        patient = patientDict[patientID]
        episodeRelabelDict[patientID] = {}
        epDates = sorted(episodeDateDict[patientID], key=itemgetter('EpStartTime'))
        for indx, dateDict in enumerate(epDates):
            epID = dateDict['epID']
            episodeRelabelDict[patientID][epID] = indx
        assert len(episodeDateDict[patientID]) == len(epDates)

    for rep in reportsDB:
        oldID = rep['EpisodeID']
        newID = episodeRelabelDict[rep[patientIDkey]][oldID]
        rep['EpisodeID'] = newID

    return reportsDB


def aggregate_episodes(reports, organ, config, logger):
    if organ == 'OrganBreast':
        reportsDB = aggregate_episodes_breast(reports, config)
        return reportsDB
    else:
        logger.warn("postprocess - aggregate episodes is not a defined for {}. Returned original report list instead".format(organ))
        return reports
    
    
def apply_rules(reportDB, trainDB, organ, config, logger):
    '''
        - Match up predicted labels with train ones, and correct errors
        - Procedurally create labels for things like cancer/atypia
        - Aggregate into episodes
    '''
    logger.info("postprocess - apply corrections")
    reportDB = apply_corrections(reportDB, trainDB, config, logger)
    # logger.info("postprocess - generate automatic fields")
    # reportDB = generate_automatic_feilds(reportDB, organ, config)
    # logger.info("postprocess - aggregate episodes")
    # reportDB = aggregate_episodes(reportDB, organ, config, logger)

    return reportDB
