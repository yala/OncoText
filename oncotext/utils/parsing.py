from openpyxl import load_workbook
from collections import OrderedDict
import xmltodict

def parse_XLS(path):
    wb = load_workbook(path)
    sheet = wb.active
    data = OrderedDict()
    for row in sheet.rows:
        values = [str(cell.value) for cell in row if cell.value is not None]
        if len(values) > 0:
            if len(values) > 1:
                data[values[0]] = values[1: ]
            else:
                data[values[0]] = []
    return data

def parse_XML(path):
    xml = xmltodict.parse(open(path, 'rb'))
    dataroot = xml[list(xml.keys())[0]]
    reportsKey = [key for key in dataroot.keys() if ('@' not in key)][-1]
    annotatedReports = dataroot[reportsKey]
    annotatedReports = [r for r in annotatedReports if r!=None and len(r)>0]
    for r in annotatedReports:
        r['filename'] = path

    return annotatedReports
