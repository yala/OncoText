import pickle as p
import xmltodict


if __name__ == "__main__":
    oldDobs = xmltodict.parse(open('FEAStudy/DOBmrnplusx.xml', 'rb'))['dataroot']['DOBmrnplusx']
    newDobs = xmltodict.parse( open('FEAStudy/DataForAdamOn2010_2016WithDOB.xml', 'rb') )['dataroot']['DataForAdamOn2010_2016']
    dobs = oldDobs + newDobs
    dobDict = {}

    dobKey = 'DOB_x002B_x'
    mrnKey = 'MRN_x002B_x'
    mrnKey2 = "MRNPlusX"
    dobKey2 = 'DOBPlusX'
    instKey = 'MRN_Type'

    verbose = False

    countDOBdups = 0
    for d in dobs:
        if mrnKey in d:
            #Check that mrn in dobDict and inst the same
            if (d[mrnKey], d[instKey]) in dobDict:
                if verbose:
                    print d
                    print dobDict[(d[mrnKey2], dobDict[instKey])]
                countDOBdups += 1

            dobDict[  (d[mrnKey], d[instKey])  ] = d[dobKey]
        
        if mrnKey2 in d:
            if (d[mrnKey2], d[instKey]) in dobDict:
                if verbose:
                    print d
                    print dobDict[ (d[mrnKey2], dobDict[instKey])]
                countDOBdups += 1

            dobDict[  (d[mrnKey2], d[instKey])  ] = d[dobKey2]


    print "Num dups", countDOBdups
    print "Num DOB MRN pairs", len(dobDict)
    print "---------------"

    rawReps = p.load( open('rawBreastPathReport.p', 'rb'))

    for rep in rawReps:
        if rep['MRNPlusX'] in dobDict:
            mrn, inst = rep['MRNPlusX'], rep['Institution']
            rep['DOBPlusX'] = dobDict[ (mrn, inst) ]

    print "Num reps with no DOB", len([r for r in rawReps if not 'DOBPlusX' in r])
    print "Num reps with DOB", len([r for r in rawReps if 'DOBPlusX' in r])

    print "Num mrns with no DOB", len(set([r['MRNPlusX'] for r in rawReps if not 'DOBPlusX' in r]))
    print "Num mrns with DOB", len(set([r['MRNPlusX'] for r in rawReps if 'DOBPlusX' in r]))

    raw_input("Redump rawBreastPathReps ?")
    p.dump(rawReps, open('rawBreastPathReport.p', 'wb'))
