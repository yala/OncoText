# import pickle as p
# from csv import DictWriter

# dataPath = "../reportDB+new.p"
# exportPath = "gradeUnlabeled"

# db = p.load( open (dataPath, 'rb'))


# papilQuery = [' papillary', 'papilloma', 'papil','pappil']
# def hasText(query, r):
#     for q in query:
#         if q in r['Report_Text_Segmented'].lower():
#             return True
#     return False


# potentialPapill = [r for r in db if hasText(papilQuery, r)]

    
# for export, path in [ 
#     (potentialPapill, 'papilAnnotations.csv')]:
#     exportRecors = []

#     for e in export:
#         exportRecors.append({
#             'ReportID': e['ReportID'],
#             'Institution': e['Institution'],
#             'text': e['Report_Text'],
#             'Papill'  : ''
#             })
#     print "Num exported", len(export)
#     keys = ['ReportID', 'Institution','text', 'Papill']
#     with open(path, "wb") as outCSV:
#         writer = DictWriter(outCSV, keys)
#         writer.writeheader()
#         writer.writerows(exportRecors)
