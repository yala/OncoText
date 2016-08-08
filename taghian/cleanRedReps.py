import pickle as p
import sys
sys.path.append("..")
from constants import *


redReps = p.load(open('../reportDB+red.p', 'rb'))
labelDict = p.load(open('../redLabelDict.p', 'rb'))

surgDiag = 'Type of Surgery'
biopDiag = 'Type of biopsy'

for r in redReps:
    if 'TaghianGold' in r:
        if surgDiag in r:
            if r[surgDiag] == 'bilateral reduction mammoplasty':
                r[surgDiag] = defaultLabelDict[surgDiag]

            r[biopDiag] = defaultLabelDict[biopDiag]
        elif biopDiag in r:
            r[surgDiag] = defaultLabelDict[surgDiag]

        for d in ['ER', 'PR', 'Her2 (Fish)']:
            if d in r and not r[d] in labelDict[d]:
                r[d] = defaultLabelDict[d]
        if 'ECE' in r:
            if r['ECE'] in ['Yes, (macroscopic)', 'Yes (macroscopic)']:
                r['ECE'] = 'Yes (Macro)'
            if r['ECE'] in ['Yes, (microscopic)', 'Yes (microscopic)']:
                r['ECE'] = 'Yes (Micro)'

p.dump(redReps, open('../reportDB+red+clean.p', 'wb'))