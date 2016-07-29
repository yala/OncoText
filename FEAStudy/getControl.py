import pickle as p
import sys
sys.path.append("..")
from constants import *

diagnoses = [ u'DCIS', u'ILC', u'Phylodes', u'CancerSuspicious', \
 u'CancerNOS', u'TubularCancer', u'IDC', u'LCIS', 'InsituNOS', \
 u'ADH', u'CancerInvInsituNOS',\
 u'ClingingCarcinoma', u'InvasiveSuspicious', u'LobularNeoplasia', 
 u'Medullary', u'ALH', u'ADH_DCIS', 'Borderline', 'FlatEpithelial']


def filt(r):
    for diag in diagnoses:
            assert report[diag] == 1 or report[diag] == 0
            if report[diag] == 1:
                return False
    return True


feas = p.load(open('AllRecordsForFEAs.p', 'rb'))
reps = p.load(open('../'+outPath, 'rb'))

print "Len FEAS", len(feas)
feaDOBs = [f for f in feas if 'DOBPlusX' in r]

possControls = [r for r in reps if filt(r)]

print "Len Poss Controls", len(possControls)

possControlsWithDOBs = [r for r in possControls if 'DOBPlusX' in r]

print "Len Poss Controls with dobs", len(possControlsWithDOBs)





