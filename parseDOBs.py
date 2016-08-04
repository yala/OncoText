import pickle as p
import xmltodict
import openpyxl as xl
from csv import DictWriter


debugList = ['598763', '947949']

if __name__ == "__main__":

    rawReps = p.load( open('rawBreastPathReport.p', 'rb'))

    oldDobs = xmltodict.parse(open('FEAStudy/DOBmrnplusx.xml', 'rb'))['dataroot']['DOBmrnplusx']
    newDobs = xmltodict.parse( open('FEAStudy/DataForAdamOn2010_2016WithDOB.xml', 'rb') )['dataroot']['DataForAdamOn2010_2016']
    missingDobs = []
    missingMRNs = []
    #Get missings dbs from xcel sheet
    wb = xl.load_workbook('FEAStudy/MissingDOBsforAdam.xlsx')
    sheet = wb.get_active_sheet()
    legend = ['MRNPlusX', 'DOBPlusX']
    legendBool = True
    for row in sheet.iter_rows():
        if legendBool:
            legendBool = False
        else:
            rowDict = {}
            for indx, col in enumerate(row):
                ## Use makes mrns into strings and leave dates alone
                rowDict[legend[indx]] = str(col.value) if indx == 0 else col.value

            instSet = set([r['Institution'] for r in rawReps if r['MRNPlusX'] == rowDict['MRNPlusX']])
            assert len(instSet) <= 1

            if len(instSet) == 0:
                print "Missing MRN", rowDict
                missingMRNs.append(rowDict['MRNPlusX'])
            else:
                rowDict['MRN_Type'] = instSet.pop()
                assert isinstance(rowDict['MRNPlusX'], str)
                print rowDict
                missingDobs.append(rowDict)

    p.dump(missingDobs, open('graceLatestDOBs', 'wb'))

    print "Num DOBs from grace", len(missingDobs)

    dobs = oldDobs + newDobs + missingDobs
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

    for rep in rawReps:
        mrn, inst = rep['MRNPlusX'], rep['Institution']
        if (mrn, inst) in dobDict:
            rep['DOBPlusX'] = dobDict[ (mrn, inst) ]

        if rep['MRNPlusX'] in debugList:
            if not 'DOBPlusX' in rep:
                print mrn, inst
                print dobDict[ (mrn, inst)] if (mrn, inst) in dobDict else "MRN, inst pair not in dobDict!"
            


    print "Num reps with no DOB", len([r for r in rawReps if (not 'DOBPlusX' in r) or r['DOBPlusX'] == 0])
    print "Num reps with DOB", len([r for r in rawReps if ('DOBPlusX' in r) and not r['DOBPlusX'] == 0])

    print "Num mrns with no DOB", len(set([r['MRNPlusX'] for r in rawReps if (not 'DOBPlusX' in r) or r['DOBPlusX'] == 0]))
    print "Num mrns with DOB", len(set([r['MRNPlusX'] for r in rawReps if ('DOBPlusX' in r) and not r['DOBPlusX'] == 0]))


    noDOBs = [ {'MRNPlusX':r['MRNPlusX'], 'Institution':r['Institution']} for r in rawReps\
     if (not 'DOBPlusX' in r) or r['DOBPlusX'] == 0] 
    noDOBInsts = set([r['Institution'] for r in noDOBs])
    noDOBInstCounts = {}
    for inst in noDOBInsts:
        noDOBInstCounts[inst] = len([r for r in noDOBs if r['Institution'] == inst])

    print "No DB Institution Distribution", noDOBInstCounts

    keys = noDOBs[0].keys()
    with open("FEAStudy/mrnsWithoutDOBs.csv", "wb") as outCSVRecords:
        writer = DictWriter(outCSVRecords, keys)
        writer.writeheader()
        writer.writerows(noDOBs)


    raw_input("Redump rawBreastPathReps ?")
    p.dump(rawReps, open('rawBreastPathReport.p', 'wb'))
