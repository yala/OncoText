import xmltodict
import pickle as p



xmlPath = "/c/Users/ksh1/Desktop/ReportDiagnosesByMRNDateSideMaxDXAll.xml"
outPath = "deidentifiedPathReports.p"
readXmlFile = True
deanon = True
dump = True

def deIden(data):
    for row in data:
        print row
    return data

if __name__ == '__main__':
    if readXmlFile:
        print "Begin reading XML File"
        with open(xmlPath, 'rb') as fd:
            data = xmltodict.parse(fd.read())

        print "Begin deanon step"
        if deanon:
            cleanData = deIden(data)

        if dump:
            p.dump(cleanData, dump)








