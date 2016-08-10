import pickle as p
from csv import DictWriter


reps = p.load(open('reportDB.p', 'rb'))
ilcReps = [r['MRNPlusX'] for r in reps if r['ILC'] == 1]
print 'len irlReps', len(ilcReps)
mrns = set( ilcReps )
print "Len mrns", len(mrns)

resReps = [r for r in reps if r['MRNPlusX'] in mrns]

print 'len(resReps)', len(resReps)

keys = resReps[0].keys()
with open("AllRecordsForILCs.csv", "wb") as outCSV:
    writer = DictWriter(outCSV, keys)
    writer.writeheader()
    writer.writerows(resReps)
    
