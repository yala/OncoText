import requests
import cPickle as p
import json
#import datetime
from datetime import date, datetime
import numpy as np
from constants import *

domain = "http://localhost:5000/"
#un_reps = p.load(open('oldReports.p','rb'))
#un_reps = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))
# un_reps = p.load(open('/home/nlp/pathology/reportDBAPI_test_small2.p', 'rb'))
# for t in test_reps:
#     for k in t:
#         if isinstance(t[k], (datetime.date, datetime.datetime, datetime.time)):
#             t[k] = t[k].isoformat()

# for u in un_reps:
#     if 'date' in u:
#         u['date'] = u['date'].isoformat()
#     # if 'Report_Date_Time' in u:
#     #     u['Report_Date_Time'] = u['Report_Date_Time'].isoformat()
#     if 'Report_Date_TimePlusX' in u:
#         u['Report_Date_TimePlusX'] = u['Report_Date_TimePlusX'].isoformat()
#     u['test_set'] = True
#     del_keys = []
#     for d in u:
#         if isinstance(u[d], np.ndarray):
#             del_keys.append(d)
#     for d in del_keys:
#         del u[d]   


name = "mghMar"

# add train
#addTrainResp = requests.post(domain+"addTrain",data=json.dumps(test_reps),params={"name":name,"raw":True})
#assert addTrainResp.status_code==200

# add unlabeled
#addUnlabeledResp = requests.post(domain+"addUnlabeled", data=json.dumps(un_reps) , params={'name':name, 'raw':True})
#assert addUnlabeledResp.status_code == 200

# update train
#updateTrainResp = requests.get(domain+"updateTrainSet", params={'name':name})
#assert updateTrainResp.status_code == 200

# update unlabeled
#updateUnlResp = requests.get(domain+"updateUnlabeledSet", params={'name':name})
#assert updateUnlResp.status_code == 200

# train
#trainResp = requests.get(domain+"train" , params={'name':name})
#assert trainResp.status_code == 200

# predict
predResp = requests.get(domain+"predict" , params={'name':name, "debug":"True"})
assert predResp.status_code == 200

#newDb = json.loads(predResp.text)['reportDB']
#print(len(newDb))
#p.dump(newDb, open('labeledReps_Convention.p','wb'))
