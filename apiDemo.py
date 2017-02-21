import requests
import cPickle as p
import json
from  datetime import datetime as date


domain = "http://172.17.140.132:5000/"
tr_reps = p.load(open('unlabled_reps.test.p','rb'))[:10] 
un_reps = p.load(open('train_reps.test.p','rb'))[:10] 

name = "test"

# add train
addTrainResp = requests.post(domain+"addTrain", data=json.dumps(tr_reps) , params={'name':name})
assert addTrainResp.status_code == 200

# add unlabeled
addUnlabeledResp = requests.post(domain+"addUnlabeled", data=json.dumps(un_reps) , params={'name':name, 'raw':True})
assert addUnlabeledResp.status_code == 200

# update train
updateTrainResp = requests.post(domain+"updateTrainSet",  , params={'name':name})
assert updateTrainResp.status_code == 200

# update unlabeled
updateUnlResp = requests.post(domain+"updateUnlabeledSet" , params={'name':name})
assert updateUnlResp.status_code == 200

# train
trainResp = requests.post(domain+"train" , params={'name':name})
assert trainResp.status_code == 200

# predict

predResp = requests.post(domain+"predict" , params={'name':name})
assert predResp.status_code == 200
newDb = json.loads(predResp.text)
print(len(newDb))

