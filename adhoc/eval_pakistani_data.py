import requests
import cPickle as p
import json
import  datetime
import sys
sys.path.append("..")
sys.path.append("../analysis")
from constants import *
import evalModelRun
import openpyxl as xl

def parseXLS(inp, out='pakistani_data.p', legend=None):
    wb = xl.load_workbook(inp)

    sheet = wb.get_active_sheet()

    data = []

    legendRowBool = legend == None
    legend = [] if legend == None else legend
    for row in sheet.iter_rows():
        rowDict = {}
        for indx, col in enumerate(row):
            if legendRowBool:
                if not col.value in legend:
                    newName = col.value
                    legend.append(newName)
                else:
                    counter = 2
                    newName = str(counter) + " " + col.value
                    while newName in legend:
                        counter += 1
                        newName = str(counter) + " " + col.value
                    legend.append(newName)
            else:
                rowDict[legend[indx]] = col.value

        if not legendRowBool:
            data.append(rowDict)
    

        legendRowBool = False
        
    p.dump(data, open(out, 'wb'))
    return data

target_diagnoses = {
	'IDC':'IDC',
	'ILC':'ILC',
	'LVI':'LVI',
	'DCIS':'DCIS',
	'ALH':'ALH',
	'ADH':'ADH',
	'ADH_DCIS':'ADH_DCIS',
	'Flat Epithelial':'FlatEpithelial',
	'Blunt Adenosis':'BluntAdenosis'
}

domain = "http://localhost:5000/"
#un_reps = p.load(open('oldReports.p','rb'))
un_reps = parseXLS('../externalDataSources/Pakistani_data.xlsx')
for u in un_reps:
	u['pakistani'] = True
	u['Report_Text'] = u['Final_Histopathological_Diagnosis']
	u['MRN'] = u['S.No']
	u['Institution'] = 'Pakistan'
	u['Report_Date'] = u['Surgery_Date']

	for t in target_diagnoses:
		d = target_diagnoses[t]
		u[d] = 'Present' if u[t] == 1 else 'Absent'

p.dump(un_reps, open("../externalDataSources/pakistani_data.p","w"))

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
predResp = requests.get(domain+"predict" , params={'name':name})
assert predResp.status_code == 200

evalModelRun.main('pakistani')

#newDb = json.loads(predResp.text)['reportDB']
#print(len(newDb))
#p.dump(newDb, open('labeledReps_Convention.p','wb'))
