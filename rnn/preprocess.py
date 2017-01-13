import cPickle as p
import word2vec
import random
import sys
sys.path.append("..")
from constants import *
import re
import numpy as np

allData = p.load(open('../reportDB+red+clean.p','rb'))

def preprocessText(text):
	cleanText = re.sub(r"\W", " ", text) 
	cleanText = ' '.join(cleanText.split('\n'))
	cleanText = re.sub(r"(----)+", "", cleanText)
	cleanText = re.sub(r"(====)+", "", cleanText)
	cleanText = cleanText.lower()
	return cleanText

def oneHot(diag, label):
	try:
		arr = np.zeros( (len(constantValidLabelDict[diag]), ))
		arr[ constantValidLabelDict[diag].index(label) ]  = 1
	except Exception, e:
		print diag, label
		return np.zeros( (len(constantValidLabelDict[diag]), ))
	return arr

allSentences = []

diagDict = {}

load = False
if load:
	j=0
	for diag in diagnoses:
		diagDict[diag] = ([],[])
		for i, r in enumerate(allData):
			if diag in r:
				raw_Text = r["Report_Text_Segmented"].lower()
				pre_Text = preprocessText(r["Report_Text_Segmented"])
				allSentences.append(pre_Text)
				# sentences = raw_Text.split(".")
				# for s in sentences:
				# 	allSentences.extend(s.splitlines())

				# if j < 10:
				# 	j +=1
				# 	print sentences[j]

				diagDict[diag][0].append( pre_Text  )
				diagDict[diag][1].append( oneHot(diag, r[diag]) )
		print 'len report/label for ', diag ,(len(diagDict[diag][0]), len(diagDict[diag][1]))

	print "done splitting into diff diags"
	p.dump(diagDict, open('diagDict.p','wb'))
	# for i,s in enumerate(allSentences):
	# 	allSentences[i] = preprocessText(s)

	p.dump(allSentences, open('sentenceList.p','wb'))
else:
	sentences = p.load(open('sentenceList.p','rb'))
	diagDict = p.load(open('diagDict.p','wb'))

make_vecs = True
if make_vecs:
	print 'starting to embedd'
	word2vec.word2vec('sentenceList.p', 'embeddings.bin', 100, verbose=True)
	model = word2vec.load('embeddings.bin')
	embeddings = model.vectors
	vocab      = model.vocab

	p.dump(embeddings, open('embeddings.p','rb'))
	p.dump(vocab, open('vocab.p','rb'))






