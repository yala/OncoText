import cPickle as p
import sys
sys.path.append("..")
from operator import itemgetter
from dicttoxml import dicttoxml
import csv
from csv import DictWriter
from constants import *

dataPath = "../labeledReps_Convention.p"

db = p.load( open (dataPath, 'rb'))

resultRecords = db

for r in resultRecords:
    if "ruleBreastSide" in r:
        del r["ruleBreastSide"]


keys = [k for k in key_order_convention if k in resultRecords[0].keys()] + [k for k in resultRecords[0].keys() if not k in key_order_convention]

div = 8
for i in range(div):
	exportPath = "allRepsMar_"+str(i+1)+".csv"
	recs = resultRecords[ i * len(resultRecords)/div : (i+1)*len(resultRecords)/div]
	print "len(recs)", len(recs)
	with open(exportPath, "wb") as outCSV:
	    writer = DictWriter(outCSV, keys)
	    writer.writeheader()
	    writer.writerows(recs)
	print exportPath
        