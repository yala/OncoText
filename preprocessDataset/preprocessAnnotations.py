import pickle as p
import sys
sys.path.append("..")
from constants import *


redReps = p.load(open('../reportDB+red.p', 'rb'))
labelDict = constantValidLabelDict

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
            if r[surgDiag] in ['2nd Re-Excision', '1st Re-Excision', 'Excisional biopsy (Lumpectomy)', 'Incisional biopsy']:
                r[biopTypeDiag] = "Excision"
        elif biopDiag in r:
            if r[biopDiag] in ['Needle biopsy',  'Core biopsy']:
                r[biopTypeDiag] = "Incision"

        if (surgDiag in r or biopDiag in r) and not biopTypeDiag in r:
            r[biopTypeDiag] = "No_breast_biopsy"


        for d in ['ER', 'PR', 'Her2 (Fish)']:
            if d in r and not r[d] in labelDict[d]:
                r[d] = defaultLabelDict[d]

        if 'ECE' in r:
            if r['ECE'] in ['Yes, (macroscopic)', 'Yes (macroscopic)', 'Yes, (microscopic)', 'Yes (microscopic)', 'Yes (Micro)', 'Yes (Macro)']:
                r['ECE'] = 'Yes'

            if r['ECE'] == 'Not_Reported':
                r['ECE'] = 'No '


        if 'TumorGrade' in r:
            if "grade III" in r['TumorGrade']:
                r['TumorGrade'] = 'Poor_(grade_III)_Undifferentiated'
            
            elif  "grade II" in r['TumorGrade']:
                r['TumorGrade'] = 'Moderate_(grade_II)'

            elif  "grade I" in r['TumorGrade']:
                r['TumorGrade'] = 'Well_differentiated_(grade_I)'
                
            elif r['TumorGrade'] == 'Not assessed':
                r['TumorGrade'] = 'Not_assessed'

        if 'Oncotype score' in r:
            if r['Oncotype score'] == 'Low risk':
                r['Oncotype score'] = 'Low_risk'

            if r['Oncotype score'] == 'High risk':
                r['Oncotype score'] = 'High_risk'

        if 'LVI' in r:
            if r['LVI'] == 'Suspicious':
                r['LVI'] = 'No'

        if 'BVI' in r:
            if r['BVI'] == 'Suspicious':
                r['BVI'] = 'No'

        if 'ITC ' in r:
            if r['ITC '] == 'Not Reported':
                r['ITC '] = 'No'

        if 'ECE' in r:
            if r['ECE'] == 'Not Reported':
                r['ECE'] = 'No'

for r in redReps:
    if ('TaghianGold' in r and r['TaghianGold'] == 1 )or ('Correct' in r and r['Correct'] == 'Y'):
        for d in HueAnotationSource:

            if not ('Correct' in r and r['Correct'] == 'Y' and d in r):
                continue
            target = "Red "+d

            if target in r:
                if r[target] in ["Present", "Absent"]:
                    print "Skiping because already writen"
                    if not (r[d] == '1' and r[target] == "Present") or (r[d] == '0' and r[target] == "Absent"):
                        print r[d], r[target]

                    continue
            if str(r[d]) == '1':
                r[target] = 'Present'

            if str(r[d]) == '0':
                r[target] = 'Absent'

            if 'BreastSide' in r:
                r['Red BreastSide'] = "RIGHT" if r['BreastSide'] in ['RIGHT',1, '1'] else 'LEFT'

        for d in BiopAnotationSource + SurgAnotationSource:
            if not ('TaghianGold' in r and r['TaghianGold'] == 1  and d in r):
                continue

            target = "Red "+d.split()[0]

            if r[d] in ["Checked", "Unifocal", "Multifocal", "Unifocal or multifocal" ]:
                r[target] = "Present"

            elif r[d] in ["Unchecked", "None"]:
                r[target] = "Absent"
            else:
                misses.add(r[d])


print "Count gold", countGold

for r in redReps:
    if ('Correct' in r and r['Correct'] == 'Y') or ('TaghianGold' in r and r['TaghianGold'] == 1): 
        if ('TaghianGold' in r and r['TaghianGold'] == 1):

            for c in const_cancers:
                if c in r and r[c] == 'Present':
                    r['cancer'] = 'Present'

        if not 'cancer' in r:
            r['cancer'] = 'Absent'

        if ('Correct' in r and r['Correct'] == 'Y') or ('TaghianGold' in r and r['TaghianGold'] == 1): 
            for a in const_atypias:
                if a in r and r[a] == 'Present':
                    r['atypia'] = 'Present'

        if not 'atypia' in r:
            r['atypia'] = 'Absent'

reps = redReps
print 'numCacnr', len([r for r in reps if 'cancer' in r and r['cancer'] == 'Present']) , len([r for r in reps if 'cancer' in r and r['cancer'] == 'Absent'])
print 'numAtypia', len([r for r in reps if 'atypia' in r and r['atypia'] == 'Present']) , len([r for r in reps if 'atypia' in r and r['atypia'] == 'Absent']) 


p.dump(redReps, open('../reportDB+red+clean.p', 'wb'))
