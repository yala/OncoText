import sys
sys.path.append("..")
from constants import *
import pickle as p


reps = p.load(open('../reportDB+red+clean.p', 'rb'))

golds = [r for r in reps if 'Correct' in r and r['Correct'] == 'Y']
print len(golds)

cancers = [ u'Red DCIS', u'Red ILC', u'Red IDC', u'Red LCIS']
atypias = [u'Red ADH',u'Red LobularNeoplasia', u'Red FlatEpithelial',  u'Red ALH']

for r in reps:
    if ('Correct' in r and r['Correct'] == 1) or ('TaghianGold' in r and r['TaghianGold'] == 1): 
        if ('TaghianGold' in r and r['TaghianGold'] == 1):
            print "mmhmm"
            for c in cancers:
                if c in r and r[c] == '1':
                    r['cancer'] = 'Present'

        if not 'cancer' in r:
            r['cancer'] = 'Absent'

        if ('Correct' in r and r['Correct'] == 1) and ('TaghianGold' in r and r['TaghianGold'] == 1): 
            print "guchi"
            for a in atypias:
                if a in r and r[a] == '1':
                    r['atypia'] = 'Present'

        if not 'atypia' in r:
            r['atypia'] = 'Absent'

print 'numCacnr', len([r for r in reps if 'cancer' in r and r['cancer'] == 'Present']) , len([r for r in reps if 'cancer' in r and r['cancer'] == 'Absent'])
print 'numAtypia', len([r for r in reps if 'atypia' in r and r['atypia'] == 'Present']) , len([r for r in reps if 'atypia' in r and r['atypia'] == 'Absent']) 

p.dump(reps, open('../reportDB+red+clean.p', 'wb'))

