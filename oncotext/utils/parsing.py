from openpyxl import load_workbook
from collections import OrderedDict

def parse_XLS(inp):
    wb = load_workbook(inp)
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