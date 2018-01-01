import openpyxl as xl
import sys
sys.path.append("..")
sys.path.append("../buildNewDataset")
from constants import *
import datetime
from operator import itemgetter
# from anonymize import deIdenText
import cPickle as p
import xmltodict

def parseXLS(inp, out, legend=None):
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
