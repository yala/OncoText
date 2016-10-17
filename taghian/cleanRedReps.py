import pickle as p
import sys
sys.path.append("..")
from constants import *


redReps = p.load(open('../reportDB+red.p', 'rb'))
labelDict = p.load(open('../redLabelDict.p', 'rb'))

surgDiag = 'Type of Surgery'
biopDiag = 'Type of biopsy'
biopTypeDiag = 'BiopsyType'

countGold = 0
countDif = 0
debug = False
for r in redReps:
    if 'TaghianGold' in r and r['TaghianGold'] == 1:
        countGold += 1

        if surgDiag in r:
            if debug:
                print '----------------------'
                print "SURGERY TYPE", r[surgDiag]
                print "Report text:"
                print r['Report_Text']
                print r[surgDiag]
                print "****************"
                raw_input()
            if r[surgDiag] in ['2nd Re-Excision', '1st Re-Excision', 'Excisional biopsy (Lumpectomy)']:
                r[biopTypeDiag] = "Excision"
                countDif += 1
        elif biopDiag in r:
            if debug:
                print '----------------------'
                print "BIOPSY TYPE", r[biopDiag]
                print "Report text:"
                print r['Report_Text']
                print r[biopDiag]
                print "****************"
                raw_input()
            if r[biopDiag] in ['Needle biopsy',  'Core biopsy',  'Incisional biopsy']:
                r[biopTypeDiag] = "Incision"
                countDif += 1

        if (surgDiag in r or biopDiag in r) and not biopTypeDiag in r:
            r[biopTypeDiag] = "No_breast_biopsy"
            countDif += 1


        for d in ['ER', 'PR', 'Her2 (Fish)']:
            if d in r and not r[d] in labelDict[d]:
                r[d] = defaultLabelDict[d]

        if 'ECE' in r:
            if r['ECE'] in ['Yes, (macroscopic)', 'Yes (macroscopic)', 'Yes, (microscopic)', 'Yes (microscopic)', 'Yes (Micro)', 'Yes (Macro)']:
                r['ECE'] = 'Yes'
                countDif += 1

            if r['ECE'] == 'Not_Reported':
                r['ECE'] = 'No '
                countDif += 1


        if 'TumorGrade' in r:
            if r['TumorGrade'] == 'Undifferentiated':
                r['TumorGrade'] = 'Poor (grade III)'
                countDif += 1

        if 'LVI' in r:
            if r['LVI'] == 'Suspicious':
                r['LVI'] = 'No'
                countDif += 1

        if 'BVI' in r:
            if r['BVI'] == 'Suspicious':
                r['BVI'] = 'No'
                countDif += 1

        if 'ITC ' in r:
            if r['ITC '] == 'Not Reported':
                r['ITC '] = 'No'
                countDif += 1

        if 'ECE' in r:
            if r['ECE'] == 'Not Reported':
                r['ECE'] = 'No'
                countDif += 1
misses = set({})
for r in redReps:
    if ('TaghianGold' in r and r['TaghianGold'] == 1 )or ('Correct' in r and r['Correct'] == 1):
        for d in HueAnotationSource:

            if not ('Correct' in r and r['Correct'] == 1 and d in r):
                continue
            target = "Red "+d

            if target in r:
                if r[target] in ["Present", "Absent"]:
                    print "Skiping because already writen"
                    assert (r[d] == '1' and r[target] == "Present") or (r[d] == '0' and r[target] == "Absent")
                    continue
            if str(r[d]) == 1:
                r[target] = 'Present'
                countDif += 1
            if str(r[d]) == 0:
                r[target] = 'Absent'
                countDif += 1

            if 'BreastSide' in r:
                r['Red BreastSide'] = "RIGHT" if r['BreastSide'] in ['RIGHT',1, '1'] else 'LEFT'

        for d in BiopAnotationSource + SurgAnotationSource:
            if not ('TaghianGold' in r and r['TaghianGold'] == 1  and d in r):
                continue

            target = "Red "+d.split()[0]

            if r[d] in ["Checked", "Unifocal", "Multifocal", "Unifocal or multifocal" ]:
                r[target] = "Present"
                countDif +=1
            elif r[d] in ["Unchecked", "None"]:
                r[target] = "Absent"
            else:
                print d
                misses.add(r[d])


print "misses", misses
print "Count gold", countGold
print "countDif", countDif

p.dump(redReps, open('../reportDB+red+clean.p', 'wb'))
