import requests
import cPickle as p
import json
import  datetime
import xmltodict

domain = "http://localhost:5000/"
fh = xmltodict.parse( open('../externalDataSources/FH and BWH Breast Path RPDRMay21_2017.xml','r'))
data = fh['dataroot']['FH_x0020_and_x0020_BWH_x0020_Breast_x0020_Path_x0020_RPDR']
for d in data:
    if d['Report_Description'] == 'Cytology':
        d['PathologyType'] = 'Cytology'
    if d['Report_Description'] == 'Surgical Pathology':
        d['PathologyType'] = 'Anatomic'

name = "mghMar"

# add train
#addTrainResp = requests.post(domain+"addTrain",data=json.dumps(data),params={"name":name,"raw":True})
#assert addTrainResp.status_code==200

#add unlabeled
for d in data:
    if 'PathologyType' in d:
        del d['PathologyType']
addUnlabeledResp = requests.post(domain+"addUnlabeled", data=json.dumps(data) , params={'name':name, 'raw':True})
assert addUnlabeledResp.status_code == 200

# update train
#updateTrainResp = requests.get(domain+"updateTrainSet",   params={'name':name})
#assert updateTrainResp.status_code == 200

# update unlabeled
#updateUnlResp = requests.get(domain+"updateUnlabeledSet" , params={'name':name})
#assert updateUnlResp.status_code == 200

# train
#trainResp = requests.get(domain+"train" , params={'name':name})
#assert trainResp.status_code == 200

# predict
#predResp = requests.get(domain+"predict" , params={'name':name})
#assert predResp.status_code == 200

#newDb = json.loads(predResp.text)['reportDB']
#print(len(newDb))
#p.dump(newDb, open('labeledReps_Convention.p','wb'))
