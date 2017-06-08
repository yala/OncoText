import cPickle as p
import sys
sys.path.append("..")
import numpy as np
from constants import *


def main() :
	db = p.load(open('/home/nlp/pathology/returnedDB_mghMar.p','rb'))
	testSet = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))

	text_to_gold = {}
	for d in testSet:
		for k in diagToConventionDict:
			if not k in d:
                            continue 
			##Convert label from diag format to clean conv
			d[diagToConventionDict[k]] = d[k]
			## convert frome onehot to str label
			label_ind = np.argmax(d[k])
			d[diagToConventionDict[k]] = constantValidLabelDict[k][label_ind]

		text_to_gold[ d['Report_Text_Segmented']] = d

	text_to_pred = {}
	for d in db:
		if d["Report_Text_Segmented"] in text_to_gold:
			text_to_pred[d['Report_Text_Segmented']] = d

	results = []
	for d in conventionToDiagDict:
		res = {'name':d}
		texts = [t for t in text_to_pred]		
		pred, gold = [text_to_pred[t][d] for t in texts],  [text_to_gold[t][d] for t in texts]
		if len(pred) == 0:
                    continue
		res['accuracy'] = sum([ pred[i] == gold[i] for i in range(pred)] )*100./ len(pred)
		results.append(res)
	print results
	return results



if __name__ == "__main__":
	main()
