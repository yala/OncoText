import pickle as p
from operator import itemgetter
from csv import DictWriter
import sys
sys.path.append("..")
from constants import *

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
            for r in reps:
                if r['BiopsyType'] == 'Incision' and r['Institution'] == 'MGH': #needle' in r['Report_Text'].lower() and 'biopsy' in r['Report_Text'].lower():# \
                #and not 'surgery' in r['Report_Text'].lower() and not 'excision' in r['Report_Text'].lower():
                    results.append(r)
        else:
            results.append(reps[0])

    return results

def getAtypTime(reps):
    def inYear(r):
        y = r['Report_Date_TimePlusX'].year
        return True
        #return (y > 2007 and y <= 2011)  or (y>= 2013 and y<=2016)

    results = [r for r in reps if inYear(r) and r['Institution']=='MGH']
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

def hasAtyp(r):
    return hasCat(r, atypias)

def hasCancer(r):
    return hasCat(r, cancers)

def getFollowup(rep):
    mrn = rep['MRNPlusX']
    date = rep['Report_Date_TimePlusX']
    def dateDif(r):
        return (r['Report_Date_TimePlusX'] - date).days

    # exis = [r for r in reps if r['MRNPlusX'] == mrn and r['BiopsyType'] == 'Excision' 
    #     and dateDif(r) > 0  and dateDif(r) < 185] 

    exis = [r for r in reps if r['MRNPlusX'] == mrn and r['Red BreastSide'] == rep['Red BreastSide']
        and dateDif(r) > 0  and dateDif(r) < 185] 

    exis = sorted( exis, key=itemgetter('Report_Date_TimePlusX') )

    return exis


def buildIncisExisMap(incis):
    ieMap = {}
    ieMapMRN = {}
    outMap = {}

    for i in incis:    
        ieMap[i['ReportID']] =  {'incis': i, 'exisList':[]}
        if not i['MRNPlusX'] in ieMapMRN:
            ieMapMRN[i['MRNPlusX']] = []    

        ieMapMRN[i['MRNPlusX']].append( i)
            

    for r in reps:
        mrn = r['MRNPlusX']

        if not mrn in ieMapMRN:
            continue

        for inc in ieMapMRN[mrn]:
            date = inc['Report_Date_TimePlusX']

            def dateDif(d):
                return (d['Report_Date_TimePlusX'] - date).days

            def validFollowup(d):
                useExis = False
                return ( not useExis or d['BiopsyType'] == 'Excision') and dateDif(d) > 0  and dateDif(d) < 365./2

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
    print " ,"+",".join(cancers)
    for atyp in atypias:
        rowStr = atyp
        for cancer in cancers:
            seed = [u for u in upgrades if hasCat(u['incis'],[atyp]) ]
            if len(seed) == 0:
                continue
            countTile = round(len([u for u in seed if rowUpgradeCat(u ,[cancer]) ])*1./len(seed),2)
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
    for atyp in atypias:
        def isCohort(row):
            return hasCat(row['incis'], [atyp]) and rowUpgrade(row)

        seed = [ieMap[i] for i in ieMap if hasCat(ieMap[i]['incis'], [atyp])]
        countUpgrades = [ieMap[i] for i in ieMap if isCohort(ieMap[i])]

        print atyp, "Upgrades:", len(countUpgrades), "Total", len(seed), \
            ", perc Upgrade", round(len(countUpgrades)*1./len(seed),2)

def noFollowDist(db, ieMap):

    rootSeed = [u for u in db if not u['ReportID'] in ieMap ]
    for a in atypias:

        seed = [u for u in db if rootSeed and hasCat(u,[a]) ]
        countTile = round(len(seed) *1./ len(rootSeed),2), len(seed)

        print a, countTile

    return 0

def noFollow(db, ieMap):

    return [u for u in db if not u['ReportID'] in ieMap ]



reps = p.load(open('../reportDB+new.p','rb'))

print "num reps", len([r for r in reps if r['Institution']=='MGH'])

incis = getIncis(reps)


print "num incisions", len(incis), round(len(incis)*1./len(reps),2)

incisNum = len([r['MRNPlusX'] for r in incis])

atypias = const_atypias

cancers = const_cancers



print "ADH vs ALH in incis", len([ r['MRNPlusX'] for r in incis if hasCat(r, ['Red ADH','Red ALH']) and not hasCancer(r)] )


bengin = [a for a in incis if not hasCancer(a)]
benginAtyp = [a for a in incis if hasAtyp(a) and not hasCancer(a)]

print "num incis with benging", len(bengin)
print "num incis with atyp and no canc", len(benginAtyp)

candidates = getAtypTime(reps)
filtCandidate = [r for r in candidates if hasAtyp(r) and not hasCancer(r) ]
exportCandidate = [ {'MRNPlusX':r['MRNPlusX']} for r in filtCandidate]


numAtyps = len([r['MRNPlusX'] for r in filtCandidate ])
# print "num atyp", numAtyps, numAtyps*1./incisNum


ieMapAtyp = buildIncisExisMap(benginAtyp)

atypNoFollow = noFollow(benginAtyp, ieMapAtyp)
print 
print 


patientsFollow = [ieMapAtyp]
print "num followup from benignAtyp", len(ieMapAtyp), round(len(ieMapAtyp)*1./len(benginAtyp),2)

ieMap = buildIncisExisMap(bengin)
print "num followup from bengin", len(ieMap), round(len(ieMap)*1./len(bengin),2)

upgrades = [ ieMap[i] for i in ieMap if rowUpgrade(ieMap[i])]
print 'overall upgrade from benign', len(upgrades), round(len(upgrades)*1./len(ieMap),2)

upgradesAtyp = [ ieMapAtyp[i] for i in ieMapAtyp if rowUpgrade(ieMapAtyp[i])]
print 'overall upgrade from benignAtyp', len(upgradesAtyp), round(len(upgradesAtyp)*1./len(ieMapAtyp),2)

buildSourceTablePerc(ieMapAtyp)
buildTablePerc(upgradesAtyp)


# examples = [ieMap[i]['incis'] for i in ieMap if not hasAtyp(ieMap[i]['incis']) ]
# examples2 = [ieMap[i]['excis'] for i in ieMap if not hasAtyp(ieMap[i]['incis']) ]

# print "len export", len(examples)
# print "len export2", len(examples2)
# print "len noFollow", len(atypNoFollow)
# print "lenExportCandidate", len(exportCandidate)



# keys = examples[0].keys() 
# keys2 = exportCandidate[0].keys()

# with open("atypiaMRNs.csv", "wb") as outCSV:

#     writer = DictWriter(outCSV, keys2)#,  delimiter = "$")
#     writer.writeheader()
#     writer.writerows(exportCandidate)


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