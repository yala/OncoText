################ Helpers ######################
def pruneNonBreast(reportDB, name):
    print("Loading db_unlabeled...")
    # reportDB = p.load(open('/home/nlp/pathology/validateDB_'+name+'.p'))
    nonbreast_path = '/home/nlp/pathology/reportDBAPI_nonbreasts.p'
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
    print("Finding non-breast reports...")

    if os.path.exists(nonbreast_path):
        nonbreasts_unlabeled = p.load(open(nonbreast_path, 'rb'))
    else:
        nonbreasts_unlabeled = {name: []}

    count = 0
    for r in reportDB:
        if r['Organ'].lower() != '1':
            matchingReports = [i for i in range(len(db_unlabeled[name])) if db_unlabeled[name][i]['Report_Text_Segmented'] == r['Report_Text_Segmented']]
            # print(matchingReports, r['Organ'])
            count += len(matchingReports)
            for j in reversed(matchingReports):
                nonbreasts_unlabeled[name].append(db_unlabeled[name].pop(j))

    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
    p.dump(nonbreasts_unlabeled, open(nonbreast_path, 'wb'))
    print("Moved "+str(count)+" non-breast reports to "+nonbreast_path+"!")

def pruneEvals(name):
    print("Loading db_unlabeled...")
    db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
    print("Finding gold reports...")
    count = 0
    for r in reversed(db_unlabeled[name]):
        if 'filename' in r and r['filename'] in os.listdir(EVALDIR):
            db_unlabeled[name].remove(r)
            count += 1
    p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
    print("Deleted "+str(count)+" gold reports!")

def applyCorrections(test, gold):
    corrections = 0
    num_match = 0
    textToLabel = {}
    for g in gold:
        textToLabel[preprocessText(g['Report_Text_Segmented'])] = g
    for t in test:
        text = preprocessText(t['Report_Text_Segmented'])
        t['validated'] = text in textToLabel
        if text in textToLabel:
            t['train'] = 1
            for d in textToLabel[text]:
                if d in diagnoses:
                    if d in t and t[d] != textToLabel[text][d]:
                        corrections += 1
                    t[d] = textToLabel[text][d]
                    num_match += 1
    print("num corrected", corrections, num_match)

# Runs enforces global constraints like ER/PR NA given no cancer
def postProcessRules(db_train):
    print(db_train[0].keys())

    for r in db_train:
        if "filename" not in r:
            r['filename'] = "Unknown"

        if hasCat(r, const_cancers):
            r['cancer'] = '1'
        else:
            r['cancer'] = '0'
        if hasCat(r, const_atypias):
            r['atypia'] = '1'
        else:
            r['atypia'] = '0'

        if r['cancer'] == '0':
            for k in ['ER', 'PR', 'Her2Fish', 'ECE', 'LVI', 'BVI', 'PositiveLN', 'ITC']:
                r[k] = '9'

        for k in r.keys():
            if type(r[k]) is unicode:
                r[k] = str(r[k])

        if 'MRN_Type' in r:
            r['Institution'] = r['MRN_Type']


    return db_train


def aggregateEpisodes(data):
    data = preprocessRawDb.unicodeToDatetime(data)
    # label episode ids for data
    mrns = {}
    sideKey = "BreastSide"
    assert sideKey in data[0]
    for i in range(len(data)):
        if sideKey not in data[i]:
            print data[i]
            raw_input('sidekey is ' + sideKey)
        if 'MRN' not in data[i] and 'MRNPlusX' in data[i]:
            data[i]['MRN'] = data[i]['MRNPlusX']
        try:
            if not data[i]['MRN'] in mrns:
                mrns[data[i]['MRN']] = {}
            if not data[i][sideKey] in mrns[data[i]['MRN']]:
                mrns[data[i]['MRN']][data[i][sideKey]] = [data[i]]
            else:
                mrns[data[i]['MRN']][data[i][sideKey]].append(data[i])
        except Exception, e:
            continue
            # print "exception e", e, "with keys", data[i].keys()
            # print "data[i]", data[i]
    # Structure: List of Reports with Episode IDs
    reportsDB = []
    episodeDateDict = {}  # Use this to store Date -> episode Id for each MRN. use this to reorder episodes by date
    episodeRelabelDict = {}  # Use this to store episoideID to new Episode ID
    for mrn in mrns:
        patient = mrns[mrn]
        episodeId = -1
        episodeDateDict[mrn] = []
        for side in patient:
            for r in patient[side]:
                if r['Report_Date_TimePlusX'] == 0:
                    r['Report_Date_TimePlusX'] = datetime(1900, 1, 1)
            patient[side] = sorted(patient[side], key=itemgetter('Report_Date_TimePlusX'))
            for idx, rep in enumerate(patient[side]):

                if idx == 0:
                    episodeId += 1
                    rep['EpisodeID'] = 't'+str(episodeId)
                    episodeDateDict[mrn].append({'EpStartTime': rep['Report_Date_TimePlusX'], 'epID': 't'+str(episodeId)})
                else:
                    prevVisit = patient[side][idx - 1]
                    if rep['Report_Date_TimePlusX'] - prevVisit['Report_Date_TimePlusX'] < SIX_MONTHS:
                        rep['EpisodeID'] = prevVisit['EpisodeID']
                    else:
                        episodeId += 1
                        rep['EpisodeID'] = 't'+str(episodeId)
                        episodeDateDict[mrn].append({'EpStartTime': rep['Report_Date_TimePlusX'], 'epID': 't'+str(episodeId)})

                reportsDB.append(rep)


    # Relabel MRNs with chronological episode numbers (first was chronological per breast)
    for mrn in mrns:
        patient = mrns[mrn]
        episodeRelabelDict[mrn] = {}
        epDates = sorted(episodeDateDict[mrn], key=itemgetter('EpStartTime'))
        for indx, dateDict in enumerate(epDates):
            epID = dateDict['epID']
            episodeRelabelDict[mrn][epID] = indx

        assert len(episodeDateDict[mrn]) == len(epDates)
    assert len(episodeRelabelDict) == len(mrns)

    for rep in reportsDB:
        oldID = rep['EpisodeID']
        newID = episodeRelabelDict[rep['MRN']][oldID]
        rep['EpisodeID'] = newID
        assert isinstance(rep['EpisodeID'], int)

    return reportsDB