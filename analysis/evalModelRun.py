import cPickle as p
sys.path.append("..")
import numpy as np
from constants import *


def main() :
	db = p.load(open('/home/nlp/pathology/returnedDB_mghMar.p','rb'))
	testSet = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))

	text_to_gold = {}
	for d in testSet:
		for k in diagToConventionDict:
			##Convert label from diag format to clean conv
			d[k] = d[diagToConventionDict[k]]
			## convert frome onehot to str label
			label_ind = np.argmax(d[k])
			d[k] = constantValidLabelDict[k][label_ind]

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
		res['accuracy'] = sum([ pred[i] == gold[i] for i in range(pred)] )*100./ len(pred)
		results.append(res)
	print results
	return results



if __name__ === "__main__":
	main()