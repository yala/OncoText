import pickle as p
from csv import DictWriter

dataPath = "../reportDB+new.p"
exportPath = "reportID_ReportText_Grade.csv"

db = p.load( open (dataPath, 'rb'))


potentailGrade = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][:100]
potentialNot   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][:50]

export = potentailGrade + potentialNot

exportRecors = []

for e in export:
    exportRecors.append({
        'ReportID': e['ReportID'],
        'Report_Text': e['Report_Text'],
        'TumorGrade'  : ''
        })

keys = ['ReportID', 'Report_Text', 'TumorGrade']
with open(exportPath, "wb") as outCSV:
    writer = DictWriter(outCSV, keys)
    writer.writeheader()
    writer.writerows(exportRecors)
    

