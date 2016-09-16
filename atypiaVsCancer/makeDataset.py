import sys
sys.path.append("..")
from constants import *
import pickle as p


reps = p.load(open('../reportDB+red+clean.p', 'rb'))

golds = [r for r in reps if 'Correct' in r and r['Correct'] == 'Y']
print len(golds)

cancers = [ u'Red DCIS', u'Red ILC', u'Red IDC', u'Red LCIS']
atypias = [u'Red ADH',u'LobularNeoplasia', u'FlatEpithelial',  u'Red ALH']

for r in reps:
    if ('Correct' in r and r['Correct'] == 1) or ('TaghianGold' in r and r['TaghianGold'] == 1): 
        if ('TaghianGold' in r and r['TaghianGold'] == 1):
            print "mmhmm"
            for c in cancers:
                if c in r and r[c] == '1':
                    r['cancer'] = '1'

        if not 'cancer' in r:
            r['cancer'] = '0'

        if ('Correct' in r and r['Correct'] == 1) and ('TaghianGold' in r and r['TaghianGold'] == 1): 
            print "guchi"
            for a in atypias:
                if a in r and r[a] == '1':
                    r['atypia'] = '1'

        if not 'atypia' in r:
            r['atypia'] = '0'

print 'numCacnr', len([r for r in reps if 'cancer' in r and r['cancer'] == '1']) , len([r for r in reps if 'cancer' in r and r['cancer'] == '0'])
print 'numAtypia', len([r for r in reps if 'atypia' in r and r['atypia'] == '1']) , len([r for r in reps if 'atypia' in r and r['atypia'] == '0']) 

p.dump(reps, open('../reportDB+red+clean.p', 'wb'))

