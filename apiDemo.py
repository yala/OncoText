import requests
import cPickle as p
import json
from  datetime import datetime as date

domain = "http://localhost:5000/"
#reps = p.load(open('tempReports.p','rb'))
name = "mghUsrTempTemp"

#addDataResp = requests.post(domain+"addData", data=json.dumps(reps) , params={'name':name, 'raw':True})


#assert addDataResp.status_code == 200

#inspectResp = requests.get(domain+"inspect")
#print inspectResp.text


#print "hit add data"
#raw_input()

#params = {"name": name, "mode":"Prod"}
#updateTrainResp = requests.get(domain+"updateTrainSet", params=params)
#assert updateTrainResp.status_code == 200
#print "hit updateTrain"

#raw_input("wait for update to fin")

#tAndPRes = requests.get(domain+"trainAndPredict", params=params)
#assert tAndPRes.status_code == 200
#raw_input("wait for train and pred to finish")

newDbRes = requests.get(domain+"getPredictions",params={"name":name})
assert newDbRes.status_code == 200
newDb = json.loads(newDbRes.text)
