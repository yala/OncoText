import xmltodict
import sys
sys.path.append("..")
from constants import *
import pickle 


paths = ['../../AdamMollyShared/ForAdam/NewTrainingFeb24_2017/' + p for p in  \
	['Retrain.xml','TrainCancerInBreastNotBreastCancer.xml','TrainLobularNeoplasia.xml','TrainOrganNotBreast.xml'] 
]

allTrain = []
for path in paths:
	with open(path,'rb') as fd:
		xml = xmltodict.parse(fd.read())
		raws = xml['dataroot'][[ k for k in xml['dataroot'].keys() if not "@" in k][0] ]

		train = []
		for row in raws:

			newRow = {}
			for key in row:
				if key in conventionToDiagDict:
					newRow[conventionToDiagDict[key]] = row[key]
				else:
					newRow[key] = row[key]
			train.append(newRow)

		allTrain.extend(train)

print "num train rows", len(allTrain)
for diag in diagnoses:
	print "num annot for ", diag, ":", len([t for t in allTrain if diag in t])
pickle.dump(allTrain, open('../additionalTrainRepsMar10.p','wb'))