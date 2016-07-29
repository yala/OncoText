import pickle as p
import xmltodict


if __name__ == "__main__":
    dobs = xmltodict.parse(open('DOBmrnplusx.xml', 'rb'))['dataroot']['DOBmrnplusx']
    dobDict = {}

    dobKey = 'DOB_x002B_x'
    mrnKey = 'MRN_x002B_x'
    instKey = 'MRN_Type'

    for d in dobs:
        if mrnKey in d:
            dobDict[d[mrnKey]] = d[dobKey]

    print "Num DOB MRN pairs", len(dobDict)
    print "---------------"

    rawReps = p.load( open('rawBreastPathReport.p', 'rb'))

    for rep in rawReps:
        if rep['MRNPlusX'] in dobDict:
            rep['DOBPlusX'] = dobDict[ rep['MRNPlusX'] ]

    print "Num reps with no DOB", len([r for r in rawReps if not 'DOBPlusX' in r])
    print "Num reps with DOB", len([r for r in rawReps if 'DOBPlusX' in r])

    print "Num mrns with no DOB", len(set([r['MRNPlusX'] for r in rawReps if not 'DOBPlusX' in r]))
    print "Num mrns with DOB", len(set([r['MRNPlusX'] for r in rawReps if 'DOBPlusX' in r]))

    raw_input("Redump rawBreastPathReps ?")
    p.dump(rawReps, open('rawBreastPathReport.p', 'wb'))
