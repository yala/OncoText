import sys
sys.path.append("..")
from constants import *
import pickle as p


reps = p.load(open('../rawBreastPathReport.p', 'rb'))

golds = [r for r in reps if 'Correct' in r and r['Correct'] == 'Y']
print len(golds)

cancers = [ u'DCIS', u'ILC', u'IDC', u'LCIS']
atypias = [u'ADH',u'LobularNeoplasia', u'FlatEpithelial',  u'ALH']

for r in reps:
    if 'Correct' in r and r['Correct'] == 'Y': 
        for c in cancers:
            if r[c] == '1':
                r['cancer'] = '1'

        if not 'cancer' in r:
            r['cancer'] = '0'

        for a in atypias:
            if a in r and r[a] == '1':
                r['atypia'] = '1'

        if not 'atypia' in r:
            r['atypia'] = '0'

print 'numCacnr', len([r for r in reps if 'cancer' in r and r['cancer'] == '1']) , len([r for r in reps if 'cancer' in r and r['cancer'] == '0'])
print 'numAtypia', len([r for r in reps if 'atypia' in r and r['atypia'] == '1']) , len([r for r in reps if 'atypia' in r and r['atypia'] == '0']) 

p.dump(reps, open('../rawBreastPathReport.p', 'wb'))

