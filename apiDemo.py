import requests
import cPickle as p
import json
import  datetime


domain = "http://localhost:5000/"
#un_reps = p.load(open('oldReports.p','rb'))
un_reps = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))
for u in un_reps:
	u['test_set'] = True


name = "mghMar"

# add train
#addTrainResp = requests.post(domain+"addTrain",data=json.dumps([]),params={"name":name,"raw":False})
#assert addTrainResp.status_code==200

# add unlabeled
addUnlabeledResp = requests.post(domain+"addUnlabeled", data=json.dumps(un_reps) , params={'name':name, 'raw':True})
assert addUnlabeledResp.status_code == 200

# update train
#updateTrainResp = requests.get(domain+"updateTrainSet",   params={'name':name})
#assert updateTrainResp.status_code == 200

# update unlabeled
updateUnlResp = requests.get(domain+"updateUnlabeledSet" , params={'name':name})
assert updateUnlResp.status_code == 200

# train
#trainResp = requests.get(domain+"train" , params={'name':name})
#assert trainResp.status_code == 200

# predict
#predResp = requests.get(domain+"predict" , params={'name':name})
#assert predResp.status_code == 200

#newDb = json.loads(predResp.text)['reportDB']
#print(len(newDb))
#p.dump(newDb, open('labeledReps_Convention.p','wb'))
