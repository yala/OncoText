import openpyxl as xl
import csv
import warnings
warnings.filterwarnings("ignore")

def scrape(pth):
    rows = []
    wb = xl.load_workbook(pth)
    sheet = wb.get_active_sheet()
    legend = []
    legendBool = True
    for row in sheet.iter_rows():
        if legendBool:
            for indx, col in enumerate(row):
                legend.append(col.value)
            legendBool = False
        else:
            rowDict = {}

            for indx, col in enumerate(row):
                rowDict[legend[indx]] = col.value

            rows.append(rowDict)
    return rows


pathSufs = ['disagreement_on_ADH.xlsx','disagreement_on_ALH.xlsx', 'disagreement_on_BluntAdenosis.xlsx',"disagreement_on_DCIS.xlsx",
"disagreement_on_FlatEpithelial.xlsx","disagreement_on_IDC.xlsx","disagreement_on_ILC.xlsx","disagreement_on_LCIS.xlsx",
"disagreement_on_LobularNeoplasia.xlsx"]

paths = ["../externalDataSources/disagreements/"+p for p in pathSufs]
feilds = ['text','MG Annotations', 'Side','ruleLabel','mlLable', "Winner"]

allRows = []
for pth in paths:        
    allRows.extend(scrape(pth))
    if "Bilateral" in [r['Winner'] for r in scrape(pth)]:
        print pth
        raw_input()

print "lenall", len(allRows), "ml Win", len([r for r in allRows if r['Winner']=='mlLabel']), "rulewin",len([r for r in allRows if r['Winner']=='ruleLabel']), "bilat?",len([r for r in allRows if r['Winner']=='Bilateral'])
print set([r['Winner'] for r in allRows])


print "Haga"