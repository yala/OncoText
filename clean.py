import xmltodict
import pickle as p



xmlPath = "/c/Users/ksh1/Desktop/ReportDiagnosesByMRNDateSideMaxDXAll.xml"
outPath = "deidentifiedPathReports.p"
readXmlFile = True
deanon = True

def deIden(data):
    for row in data:
        print row

if __name__ == 'main':
    if readXmlFile:
        with open(xmlPath, 'rb') as fd:
            data = xmltodict.parse(fd.read())

        if deanon:
            deIden(data)





