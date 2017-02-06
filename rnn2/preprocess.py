import cPickle as p
import word2vec
import random
import sys
sys.path.append("..")
from constants import *
import re
import numpy as np




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

load = True
if load:
    allData = p.load(open('../reportDB+red+clean.p','rb'))
    j=0
    for diag in diagnoses:
        diagDict[diag] = ([],[])
        for i, r in enumerate(allData):
            if diag in r:
                raw_Text = r["Report_Text_Segmented"].lower()
                pre_Text = preprocessText(r["Report_Text_Segmented"])
                diagDict[diag][0].append( pre_Text  )
                diagDict[diag][1].append( oneHot(diag, r[diag]) )
        print 'len report/label for ', diag ,(len(diagDict[diag][0]), len(diagDict[diag][1]))

    for r in allData:
        pre_Text = preprocessText(r["Report_Text_Segmented"])
        allSentences.append(pre_Text)


    print "done splitting into diff diags"
    p.dump(diagDict, open('diagDictTrainText.p','wb'))
    # for i,s in enumerate(allSentences):
    #   allSentences[i] = preprocessText(s)
    print "num sentences", len(allSentences)
    p.dump(allSentences, open('sentenceList.p','wb'))
    

make_vecs = False
if make_vecs:
    sentences = p.load(open('sentenceList.p','rb'))
    print 'starting to embedd'
    word2vec.word2vec('sentenceList.p', 'embeddings.bin', 100, verbose=True)
    model = word2vec.load('embeddings.bin')
    embeddings = model.vectors
    vocab      = model.vocab

    p.dump(model, open('word2vecModel.p','wb'))
    p.dump(embeddings, open('embeddings.p','wb'))
    p.dump(vocab, open('vocab.p','wb'))


get_vecs = True
if get_vecs:
    print "start get vecs"
    diagDict = p.load(open('diagDictTrainText.p','rb'))
    w2vM = p.load(open('word2vecModel.p','rb'))

    print "build vocab"
    vocab = w2vM.vocab
    vocabIndxDict = {}
    for i,v in enumerate(vocab):
        vocabIndxDict[v] = i

    print "done create vocab"
    p.dump(vocabIndxDict, open('vocabIndxDict.p','wb'))

    print "dumped voab dit"

    for j,diag in enumerate(diagDict):
        indexSentences = []
        sents = diagDict[diag][0]
        print diag, "num sentences", len(sents)
        for sent in sents:
            words = sent.split(" ")
            indices = [ vocabIndxDict[w] for w in words if w in vocabIndxDict]
            indexSentences.append( (np.array(indices), len(indices)) )

        def getLen(s):
            return s[1]
        sortedSentences = sorted(indexSentences, key = getLen)
        
        hist = 
        print "diag bins", np.hist()
        
        diagDict[diag] =  (indexSentences , diagDict[diag][1])
        print "done with ", j, len(diagDict)
        
    p.dump(diagDict, open('diagDictTrain.p','wb'))







