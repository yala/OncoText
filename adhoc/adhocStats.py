import pickle as p
from operator import itemgetter
from csv import DictWriter
import sys
sys.path.append("..")
from constants import *
import matplotlib.pyplot as plt

trumpOrderAtyp = ['Red ADH_DCIS','Red ADH', "Red LCIS",'Red ALH', 'Red FlatEpithelial', 'Red Phylodes']
# trumpOrderAtyp = ['Red ADH', "Red LCIS", 'Red ALH', 'Red FlatEpithelial', 'Red LobularNeoplasia', 'Red Phylodes']



def getIncis(reps):
    results = []
    mrnToReps = {} 
    for r in reps:
        mrn = r['MRNPlusX']
        if not mrn in  mrnToReps:
            mrnToReps[mrn] = []
        mrnToReps[mrn].append(r)

    for mrn in mrnToReps:
        if len(mrnToReps[mrn]) < 0:
            continue
        reps = sorted( mrnToReps[mrn],key=itemgetter('Report_Date_TimePlusX') )

        if True:
            for i,r in enumerate(reps):
                if r['BiopsyType'] == 'Incision' and r['Institution'] == 'MGH': 
                    results.append(r)
        else:
            results.append(reps[0])

    return results


def getAtypIncis(reps):
    resultDict = {}
    mrnToReps = {} 
    for r in reps:
        mrn = r['MRNPlusX']
        if not mrn in  mrnToReps:
            mrnToReps[mrn] = []
        mrnToReps[mrn].append(r)

    for mrn in mrnToReps:
        if len(mrnToReps[mrn]) <= 0:
            continue

        
        reps = sorted( mrnToReps[mrn],key=itemgetter('Report_Date_TimePlusX') )

        if len(reps) < 2 or not reps[0]['Institution'] == 'MGH':
            continue
        
        for i,r in enumerate(reps):
            lowText = r['Report_Text_Segmented'].lower()
            if hasCancer(r) or 'invasive mammary carcinoma' in lowText:# or 'excision' in lowText :
                continue


            side = r['Red BreastSide']
            date = r['Report_Date_TimePlusX']
            def hasFollow():
                for j in range(0, len(reps)):
                    if j == i:
                        continue
                    rj  = reps[j]
                    if (rj['Report_Date_TimePlusX'] - date).days < 180 and (rj['Report_Date_TimePlusX'] - date).days > 0 and rj['Red BreastSide'] == side:
                        return True
                return False

            if not hasFollow():
                continue

            ## look for prior cancer and get atyp
            if hasAtyp(r):
                def priorCancer():
                    canc = []
                    for j in range(0, len(reps)):
                        rj  = reps[j]
                        if hasCancer(rj) and (date - rj['Report_Date_TimePlusX']).days < 90 and (date - rj['Report_Date_TimePlusX']).days >= 0:
                            return True
                    return False
                if not priorCancer():
                    resultDict[r['MRNPlusX']] = r

    results = [resultDict[k] for k in resultDict]

    return results

def atypsOverTime(reps):
    ratios = []
    increment = 3
    for ran in range(1992, 2016, increment):
        low = ran
        high = low + increment
        def yearFilt(r):
            return r['Report_Date_TimePlusX'].year > low and r['Report_Date_TimePlusX'].year <= high  and r['BiopsyType']=='Incision'

        seed = [r for r in reps if yearFilt(r) and r['Institution']=="MGH"]
        numPatients = len(set([r['MRNPlusX'] for r in seed if r['BiopsyType']=='Incision']))
        numPatientsAtyp = len(set([r['MRNPlusX'] for r in seed if hasAtyp(r) and not hasCancer(r)]))
        percAtyp = numPatientsAtyp *1. / numPatients        
        ratios.append(percAtyp)
        print "in years", low, high, "percent atyp is ", numPatientsAtyp*1. / numPatients, ",num patients in range is", numPatients

    print "Len(Y)", len(ratios)
    X =  [k for k in range(1995,2017,increment)]
    print "Len(X)",len(X)

    plt.plot(X, ratios)
    plt.title("Atypia per Biopsy since 1995")
    plt.xlabel("year")
    plt.ylabel("Percent benign biopsies with atypia")
    # # plt.ylim((.08,.25))
    # plt.xlim((1995,2015))
    # plt.show()

def getAtypTime(reps):
    def inYear(r):
        y = r['Report_Date_TimePlusX'].year
        return True
        #return (y > 2007 and y <= 2011)  or (y>= 2013 and y<=2016)

    results = [r for r in reps if inYear(r) and r['Institution']=='mv']
    return reps
    # return results


def getAtypTime2(reps):

    results = []
    mrnToReps = {} 
    for r in reps:
        mrn = r['MRNPlusX']
        if not mrn in  mrnToReps:
            mrnToReps[mrn] = []
        mrnToReps[mrn].append(r)

    for mrn in mrnToReps:
        if len(mrnToReps[mrn]) < 0:
            continue
        reps = sorted( mrnToReps[mrn],key=itemgetter('Report_Date_TimePlusX') ) 
        results.append(reps[0])

    def inYear(r):
        y = r['Report_Date_TimePlusX'].year
        return (y > 2007 and y <= 2011)  or (y>= 2013 and y<=2016)

    results = [r for r in results if inYear(r)]

    return results




def hasCat(r, cat):
    for c in cat:
        if r[c] == 'Present':
            return True
    return False

def hasTrumpedAtypia(r, atyp):
    for a in trumpOrderAtyp:
        if a in r and r[a] == "Present":
            return a == atyp
    return False

def getAtypTrump(r):
    for a in trumpOrderAtyp:
        if a in r and r[a] == "Present":
            return a
    return False

def getCancerTrump(r):
    trumpOrder = ['Red ILC','Red IDC', 'Red DCIS', 'Red CancerNOS']
    for a in trumpOrder:
        if a in r and r[a] == "Present":
            return a
    return False

def hasTrumpedCancer(exis):
    trumpOrder = ['Red ILC','Red IDC', 'Red DCIS', 'Red CancerNOS']
    for a in trumpOrder:
        for r in exis:
            if a in r and r[a] == "Present":
                if a in ['Red ILC', 'Red IDC']:
                    return "Invasive"
                elif a == "Red DCIS":
                    return "DCIS"

    return False
  
def hasAtyp(r):
    return hasCat(r, atypias)

def hasCancer(r):
    return hasCat(r, cancers)


def buildIncisExisMap(incisL):
    ieMap = {}
    ieMapMRN = {}
    outMap = {}

    for i in incisL:    
        ieMap[i['ReportID']] =  {'incis': i, 'exisList':[]}
        if not i['MRNPlusX'] in ieMapMRN:
            ieMapMRN[i['MRNPlusX']] = []    

        ieMapMRN[i['MRNPlusX']].append( i)
            

    for r in reps:
        mrn = r['MRNPlusX']

        if not mrn in ieMapMRN:
            continue

        assert len(ieMapMRN[mrn]) < 2
        for inc in ieMapMRN[mrn]:
            date = inc['Report_Date_TimePlusX']
            side = inc['Red BreastSide']

            def dateDif(d):
                return (d['Report_Date_TimePlusX'] - date).days

            def validFollowup(d):
                useExis = False
                return ( not useExis or d['BiopsyType'] == 'Excision') and dateDif(d) > 0  and dateDif(d) < 180 and d['Red BreastSide'] == side

            if validFollowup(r):
                ieMap[inc['ReportID']]['exisList'].append(r)

    for repId in ieMap:

        exis = sorted( ieMap[repId]['exisList'], key=itemgetter('Report_Date_TimePlusX') )

        if len(exis) > 0:

            ieMap[repId]['excis'] = exis[0]
            
            outMap[repId] = {'incis': ieMap[repId]['incis'], 'excis':exis }

    return outMap

def rowUpgrade(row):
    for exis in row['excis']:
        if hasCancer(exis):
            return True
    return False

def rowUpgradeCat(row, cat):
    for exis in row['excis']:
        if hasCat(exis,cat):
            return True

    return False


def buildTableCounts(upgrades):
    print " ,"+",".join(cancers)
    for atyp in atypias:
        rowStr = atyp
        for cancer in cancers:
            seed = [u for u in upgrades if hasCat(u['incis'],[atyp]) ]
            countTile = len([u for u in seed if rowUpgradeCat(u,[cancer]) ])
            rowStr += "," + str(countTile)
        print rowStr

    ## benign row
    rowStr = "benign"
    for cancer in cancers:
        seed = [u for u in upgrades if not hasAtyp(u['incis']) ]
        countTile = len([u for u in seed if 
            rowUpgradeCat(u,[cancer])])
        rowStr += "," +  str(countTile)

    print rowStr

    return 0

def buildTablePerc(upgrades):
    print " ,"+",".join(['Invasive', 'DCIS'])
    for atyp in atypias:
        rowStr = atyp
        for cancer in ['Invasive', 'DCIS']:
            seed = [u for u in upgrades if hasTrumpedAtypia(u['incis'],atyp) ]
            if len(seed) == 0:
                continue
            countTile = round(len([u for u in seed if hasTrumpedCancer(u['excis']) == cancer ])*1./len(seed),2)
            rowStr += "," + str(countTile)
        print rowStr

    ## benign row
    rowStr = "benign"
    seed = [u for u in upgrades if not hasAtyp(u['incis']) ]
    if len(seed) == 0:
        return 0

    for cancer in cancers:
        countTile = round(len([u for u in seed if rowUpgradeCat(u,[cancer])]) *1. / len(seed), 2)
        rowStr += "," +  str(countTile)

    print rowStr

    return 0

def buildSourceTablePerc(ieMap):
    seeds = {}
    for atyp in atypias:
        def isCohort(row):
            return hasTrumpedAtypia(row['incis'], atyp) and rowUpgrade(row)

        seed = [ieMap[i] for i in ieMap if hasTrumpedAtypia(ieMap[i]['incis'],atyp)]

        countUpgrades = [ieMap[i] for i in ieMap if isCohort(ieMap[i])]
        seeds[atyp] = countUpgrades

        perc = round(len(countUpgrades)*1./len(seed),2) if len(seed) > 0 else 0
        print atyp, "Upgrades:", len(countUpgrades), "Total", len(seed), \
            ", perc Upgrade", perc
    return seeds

def noFollowDist(db):
    print "NO FOLLOW DIST"
    for a in atypias:

        seed = [u for u in db if hasTrumpedAtypia(u, a) ]
        countTile = round(len(seed) *1./ len(db),2), len(seed)

        print a, countTile
    print "NO FOLLOWDIST END"
    return 0

def noFollow(db, ieMap):

    return [u for u in db if not u['ReportID'] in ieMap ]



reps = p.load(open('../reportDB+new.p','rb'))


print "num patients", len(set([r['MRNPlusX'] for r in reps if r['Institution']=='MGH']))

incis = reps#getIncis(reps)


print "num incisions", len(set([r['MRNPlusX'] for r in incis])), round(len(incis)*1./len(reps),2)

incisNum = len([r['MRNPlusX'] for r in incis])

atypias = const_atypias

cancers = const_cancers

# atypsOverTime(reps)


print "ADH vs ALH in incis", len([ r['MRNPlusX'] for r in incis if hasCat(r, ['Red ADH','Red ALH']) and not hasCancer(r)] )


bengin = [a for a in incis if not hasCancer(a)]
benginAtyp = getAtypIncis(reps)

print "num incis with benging", len(bengin)
print "num incis with atyp and no canc", len(benginAtyp)

# candidates = getAtypTime(reps)
# filtCandidate = [r for r in candidates if hasAtyp(r) and not hasCancer(r) ]
# exportCandidate = [ {'MRNPlusX':r['MRNPlusX']} for r in filtCandidate]


# numAtyps = len([r['MRNPlusX'] for r in filtCandidate ])
# print "num atyp", numAtyps, numAtyps*1./incisNum


ieMapAtyp = buildIncisExisMap(benginAtyp)

# atypNoFollow = noFollow(benginAtyp, ieMapAtyp)
# noFollows = [{'MRNPlusX':r['MRNPlusX'], 
#             'Report_Date_TimePlusX':r['Report_Date_TimePlusX'], 'Institution': r['Institution'],
#             'Report_Text_Segmented':r['Report_Text_Segmented']}
#                 for r in atypNoFollow]
# noFollowsMRNs = set([r['MRNPlusX'] for r in noFollows])
# assert len(set([r['MRNPlusX'] for r in noFollows])) == len(set([r['MRNPlusX'] for r in atypNoFollow]))
# assert len(noFollowsMRNs) == len(set([r['MRNPlusX'] for r in noFollows]))
# print len(noFollowsMRNs)
# noFollowDist(atypNoFollow)
# print 
print 


patientsFollow = [ieMapAtyp]
print "num followup from benignAtyp", len(ieMapAtyp), round(len(ieMapAtyp)*1./len(benginAtyp),2)

assert len(set([ ieMapAtyp[r]['incis']['MRNPlusX'] for r in ieMapAtyp])) == len(ieMapAtyp)

# ieMap = buildIncisExisMap(bengin)
# print "num followup from bengin", len(ieMap), round(len(ieMap)*1./len(bengin),2)

# upgrades = [ ieMap[i] for i in ieMap if rowUpgrade(ieMap[i])]
# print 'overall upgrade from benign', len(upgrades), round(len(upgrades)*1./len(ieMap),2)

print '-------------------'
upgradesAtyp = [ ieMapAtyp[i] for i in ieMapAtyp if rowUpgrade(ieMapAtyp[i])]
print 'overall upgrade from benignAtyp', len(upgradesAtyp), round(len(upgradesAtyp)*1./len(ieMapAtyp),2)
print' --------------------'

for upgrade in upgradesAtyp:
    incis = upgrade['incis']
    atyp = getAtypTrump(incis)
    if atyp in []:#'Red ALH', 'Red LCIS', 'Red FlatEpithelial']:
        print "atyp is", atyp
        print "rep also has ADH", incis['Red ADH']
        print "rep also has SevADH", incis['Red ADH_DCIS']

        print "incis report", incis['Report_Text_Segmented']
        print 'date', incis['Report_Date_TimePlusX']
        print '--'
        print 'excis report', upgrade['excis'][0]['Report_Text_Segmented']
        print 'date', upgrade['excis'][0]['Report_Date_TimePlusX']
        print 'canc', getCancerTrump(upgrade['excis'][0])
        raw_input()

seeds = buildSourceTablePerc(ieMapAtyp)
buildTablePerc(upgradesAtyp)

lcisMRNs = [ {'MRNPlusX': r['incis']['MRNPlusX'], 'Report_Date_TimePlusX': r['incis']['Report_Date_TimePlusX']} for r in seeds['Red LCIS'] ]
print len(lcisMRNs), "number MRNs for the LCIS upgrades"

# examples = [ieMap[i]['incis'] for i in ieMap if not hasAtyp(ieMap[i]['incis']) ]
# examples2 = [ieMap[i]['excis'] for i in ieMap if not hasAtyp(ieMap[i]['incis']) ]

# print "len export", len(examples)
# print "len export2", len(examples2)
# print "len noFollow", len(atypNoFollow)
# print "lenExportCandidate", len(exportCandidate)


# noFollowReps = [ r for r in reps if r['MRNPlusX'] in noFollowsMRNs ]


# print len(noFollows), "number MRNs for no follows"
# print len(noFollowReps), "number Reps for no follows"


# # keys = ['MRNPlusX', 'Report_Date_TimePlusX', 'Institution' ]
# keys = noFollows[0].keys()


# with open("atypiasNoFollowupsFocus.csv", "wb") as outCSV:

#     writer = DictWriter(outCSV, keys)#,  delimiter = "$")
#     writer.writeheader()
#     writer.writerows(noFollows)


# with open("benignLeadingToExcision.csv", "wb") as outCSV:

#     writer = DictWriter(outCSV, keys)#,  delimiter = "$")
#     writer.writeheader()
#     writer.writerows(examples)

# with open("benignFollwups.csv", "wb") as outCSV:

#     writer = DictWriter(outCSV, keys)#,  delimiter = "$")
#     writer.writeheader()
#     writer.writerows(examples2)


# with open("atypiaNoFollowup.csv", "wb") as outCSV:

#     writer = DictWriter(outCSV, keys)#,  delimiter = "$")
#     writer.writeheader()
#     writer.writerows(atypNoFollow)
