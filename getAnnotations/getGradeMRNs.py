import pickle as p
from csv import DictWriter

dataPath = "../reportDB+new.p"
exportPath = "gradeUnlabeled"

db = p.load( open (dataPath, 'rb'))


# potentailGrade = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][:100]
# potentialNot   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][:50]

# potentailGrade2 = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][100:200]
# potentialNot2   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][50:100]

# potentailGrade3 = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][300:400]
# potentialNot3   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][100:150]

# potentailGrade4 = [r for r in db if 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() ][400:450]
# potentialNot4   = [r for r in db if not( 'grade' in r['Report_Text'].lower() or 'differentia' in r['Report_Text'].lower() )][150:250]


papilQuery = [' papillary', 'papilloma', 'papil','pappil']
def hasText(query, r):
    for q in query:
        if q in r['Report_Text_Segmented'].lower():
            return True
    return False


potentialPapill = [r for r in db if hasText(papilQuery, r)]



# exportMolly = potentailGrade4 + potentialNot4
# exportLaura = potentialNot3 + potentailGrade3

# for export, path in [ #(exportLaura,exportPath+'Laura.csv'),
#     (exportMolly, exportPath+'Molly.csv')]:
#     exportRecors = []

#     for e in export:
#         exportRecors.append({
#             'ReportID': e['ReportID'],
#             'text': e['Report_Text'],
#             'TumorGrade'  : ''
#             })

#     keys = ['ReportID', 'text', 'TumorGrade']
#     with open(path, "wb") as outCSV:
#         writer = DictWriter(outCSV, keys)
#         writer.writeheader()
#         writer.writerows(exportRecors)
    
for export, path in [ 
    (potentialPapill, 'papilAnnotations.csv')]:
    exportRecors = []

    for e in export:
        exportRecors.append({
            'ReportID': e['ReportID'],
            'Institution': e['Institution'],
            'text': e['Report_Text'],
            'Papill'  : ''
            })
    print "Num exported", len(export)
    keys = ['ReportID', 'Institution','text', 'Papill']
    with open(path, "wb") as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(exportRecors)