import requests
import cPickle as p
import json
import pdb
import  datetime
import numpy as np
from getAtypias import updateAccesDB
import sys
sys.path.append('../buildNewDataset')
import exportToJSON
sys.path.append('..')
from constants import *

un_reps = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))
db = p.load(open('/home/nlp/pathology/evalDB_mghMar.p','r'))

text_to_pred = {}
for d in db:
    text_to_pred[d['Report_Text_Segmented']] = d

key_match_dict = {'Her2_x0020__x0028_Fish_x0029_': 'Her2 (Fish)', 'Are_x0020_there_x0020_positive_x0020_LN_x003F_':'Are there positive LN?', 'Cancer_x0020_Invasive':'Red CancerInvasive'}

alt_reps = []
for u in un_reps:
    if not u['Report_Text_Segmented'] in text_to_pred:
        continue
    for k in key_match_dict:
	u[key_match_dict[k]] = u[k]
        del u[k] 
    m = text_to_pred[u['Report_Text_Segmented']]
    u['test_set'] = True
    del_keys = ['NN_Text']
    for d in u:
        if isinstance(u[d], np.ndarray) and not d in del_keys:
            label_ind = np.argmax(u[d])
            u[d] = constantValidLabelDict[d][label_ind]

    for d in [z for z in del_keys if z in u]:
        del u[d]   
    for d in [z for z in diagnoses if z in diagToConventionDict]:
	k = diagToConventionDict[d]
        if not d in u and k in m:
            u[d] = m[k]
    alt_reps.append(u)
reps = exportToJSON.portToJSON(alt_reps)
updateAccesDB(reps, 'GoldReports')

updateAccesDB( p.load(open('/home/nlp/pathology/pakistaniDB_mghMar.p','r')), 'PakistaniReports')
