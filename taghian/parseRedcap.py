import pickle as p
import openpyxl as xl
import sys
sys.path.append("..")
from constants import *

def parseXLS():
    print "loading wb"
    wb = xl.load_workbook('redcap.xlsx')

    print "getting sheet"
    sheet = wb.get_active_sheet()

    data = []

    legendRowBool = True
    print "Getting iterator"
    legend = []
    for row in sheet.iter_rows():
        rowDict = {}
        for indx, col in enumerate(row):
            if legendRowBool:
                legend.append(col.value)
            else:
                rowDict[legend[indx]] = col.value

        if not legendRowBool:
            data.append(rowDict)
        else:
            print 'processing legend row'

        legendRowBool = False
        
    print 'dumping'

    p.dump(data, open('redcap.p', 'wb'))
    return data


def normalizeMRN(mrn):
    res = str(mrn).strip()
    while len(res) < 8:
        res = '0' + res
    return res


def preprocessDB(data):
    mrnDB = {}
    for rep in data:
        try:
            mrn = normalizeMRN(rep['Registry ID'])
        except Exception, e:
            print rep['Registry ID']
            continue

        rep['MRNPlusX'] = mrn

        if mrn in mrnDB:
            mrnDB[mrn].append(rep)
        else:
            mrnDB[mrn] = [rep]

    print "Number of unique MRNs in recap DB", len(mrnDB)
    p.dump(mrn, open('redcapMRNDB.p', 'wb'))

    return mrnDB

def findMatchingReports(db):
    pathMrns = {}
    pathReps = p.load(open('../'+outPath, 'rb'))
    for r in pathReps:
        pathMRN = normalizeMRN(r['MRNPlusX'])

        if pathMRN in pathMrns:
            pathMrns[pathMRN].append( r )
        else:
            pathMrns[pathMRN] = [r]

    joinedDB = {}
    for mrn in db:
        if not mrn in pathMrns:
            continue

        joinedDB[mrn] = {'hughes':pathMrns[mrn], 'taghian':db[mrn]}

    p.dump(joinedDB, open('redcapWithPathReps.p', 'wb'))

    print "Size of taghian hughes MRN overlap", len(joinedDB)
    return joinedDB



parseXLSBool = False
preprocessDBBool = True
findMatchingReportsBool = True

if __name__ == "__main__":

    redcap = p.load(open('redcap.p','rb')) if not parseXLSBool else parseXLS()
    mrnDB = preprocessDB(redcap) if preprocessDBBool else p.load(open('redcapMRNDB.p','rb'))
    joinedDB = findMatchingReports(mrnDB) if findMatchingReportsBool else p.load(open('redcapWithPathReps.p', 'rb'))



