import csv

allPath = "flatAtypExports.csv"
oldPath = "flatAtypExportsOld.csv"
exportPath = "flatAtypExportsNew.csv"

allData = set()
oldData = set()

result = []

with open(oldPath, 'rb') as f2:
    allDataReader = csv.reader(f2, quoting=csv.QUOTE_ALL)
    for row in allDataReader:
        oldData = set(row)

with open(allPath, 'rb') as f1:
    allDataReader = csv.reader(f1, quoting=csv.QUOTE_ALL)
    for row in allDataReader:
        allData = set(row)

for d in allData:
    if not d in oldData:
        result.append(d)

print len(result)

with open(exportPath, 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(result)
