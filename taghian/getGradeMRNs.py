import pickle as p
from csv import DictWriter

dataPath = "../reportDB.p"
exportPath = "reportID_ReportText_Grade"

db = p.load( open (dataPath, 'rb'))


potentailGrade = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][:100]
potentialNot   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][:50]

potentailGrade2 = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][100:200]
potentialNot2   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][50:100]

potentailGrade3 = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][300:400]
potentialNot3   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][100:150]

exportMolly = potentailGrade2 + potentialNot2
exportLaura = potentialNot3 + potentailGrade3

for export, path in [(exportLaura,exportPath+'Laura.csv'),
    (exportMolly, exportPath+'Molly.csv')]:
    exportRecors = []

    for e in export:
        exportRecors.append({
            'ReportID': e['ReportID'],
            'Report_Text': e['Report_Text'],
            'TumorGrade'  : ''
            })

    keys = ['ReportID', 'Report_Text', 'TumorGrade']
    with open(path, "wb") as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(exportRecors)
    

