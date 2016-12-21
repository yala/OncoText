import requests
import cPickle as p
import json
from  datetime import datetime as date

domain = "http://rosetta2.csail.mit.edu:5000/"
reps = p.load(open('preprocessDataset/data/susPhyllodesOct.p','rb'))
name = "mghUsrTempTemp"

addDataResp = requests.post(domain+"addData", data=json.dumps(reps) , params={'name':name, 'raw':True})


assert addDataResp.status_code == 200

inspectResp = requests.get(domain+"inspect")
print inspectResp.text


print "hit add data"
raw_input()

params = {"name": name, "mode":"Prod"}
updateTrainResp = requests.get(domain+"updateTrainSet", params=params)
assert updateTrainResp.status_code == 200
print "hit updateTrain"

updateTrainResp = requests.get(domain+"updateTrainSet", params=params)
assert updateTrainResp.status_code == 200
print "hit updateTrain"

tAndPRes = requests.get(domain+"trainAndPredict", params=params)
assert tAndPRes.status_code == 200

newDbRes = requests.get(domain+"getPredictions",params={"name":name})
assert newDbRes.status_code == 200
newDb = json.loads(newDbRes.text)