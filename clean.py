import xmltodict
import pickle as p
import re
import datefinder

months = ["jan", "feb", "mar", "apr", "jun", "jul", "sep", "oct", "nov", "dec",\
"january", "febuary", "march", "april", "june", "july", "september", "october", "november", "december"]

replaceStrings = ["REMOVED_DATE", "REMOVED_MONTH", "REMOVED_PATIENT_NAME", "REMOVED_ACCESSION_ID", "REMOVED_CASE_ID"]
#Script to dump xml file into a deIdentifiedDict
def deIden(data):
    print "Calling Deint data"
    cleanedData = []
    for pathReport in data[:1]:
        cleanedReport = {}
        for key in pathReport:
            #These keys constitute the annotation
            if not key == 'Report_Text':
                cleanedReport[key] = pathReport[key]
        #This is the raw patient report. Might contain Patient Name, or dates or Accession number 
        ## All of which must be removed
        dirtyText = pathReport['Report_Text']
        cleanText = deIdenText(dirtyText)
        cleanedReport['Report_Text'] = cleanText

        cleanData.append(cleanedReport)
        
    return cleanedData

def deIdenText(dirtyText):
    print "calling deIdenDirtyText"
    print "DirtyText looks like"
    print dirtyText
    print '***************************'
    cleanLines = []
    lines = dirtyText.split('\n')
    for line in lines:
        ## TODO Check for dates (12/23/1212) format and if it matches months
        ## Check for accesion number and &quot&
        ## Check for patient names, with PATIENT
        ## Remove Pathology Report Number
        ## Format is [UPPERCASE]+[NUMBER]+

        cleanLine = stripDates(line)
        cleanLine = stripPatientName(cleanLine)
        cleanLine = stripAccesionNumber(cleanLine)

        cleanLines.append(cleanLine)

    cleanedText = "\n".join(cleanLines)
    raw_input()
    print "Cleaned text"
    print 
    print cleanedText
    raw_input()

    return cleanedText

#remove ,.?;;'"|/
def stripDelims(word):
    if word[-1] in ",.?;:":
        return word[:-1]
    else:
        return word


#Remove dates of format ##/##/##### and replaces with REMOVED_DATE or REMOVED_MONTH
def stripDates(line):
    cleanWords = []

    words = line.split()
    #Remove months
    for w in words:
        word = stripDelims(w.lower())
        if word in months:
            cleanWords.append('REMOVED_MONTH')
        else:
            cleanWords.append(w)

    cleanedLine = " ".join(cleanWords)
    cleanedLine = re.sub(dateRegex, " REMOVED_DATE ", cleanedLine)

    return cleanedLine

#Remove names of patients and replace with REMOVED_PATIENT_NAME
def stripPatientName(line):
    if "PATIENT:" in line:
        return "PATIENT: REMOVED_PATIENT_NAME"
    else:
        return line

#Remove all occurances of accession number and repalce with "REMOVED_ACCESSION_ID"
def stripAccesionNumber(line):
    cleanedLine = re.sub(accesionNumberRegex, 'REMOVED_ACCESSION_ID', line)
    cleanedLine = re.sub(caseNumberRegex, "REMOVED_CASE_ID", cleanedLine)

    return cleanedLine


dateRegex = r"[ ]+\d+[- /.]+\d+[- /.]?\d*[,.;:?]?"
accesionNumberRegex = r"[A-Z]+[0-9]+[-]?[A-Z]*[0-9]*[-]?[A-Z]*[0-9]*"
caseNumberRegex = r"\d{4}\d+"

testString = "Accession Number: S0430461B                   Report Status Final\n"+\
            "Type Surginal 03\nPathology Report  S04-30465-B BREAST CORE NEEDLE\n"+\
            "Accesioned On: 05/02003\nRICHARDSON, ANDREA, K, M,D~PH.D\nPATIENT: Adam Yala\n"+\
            "Something on June first/second/third yaknow 02/25/1995 Feb, 02, 2016, 1992/02/12, 1992-02-12, 0-2-1992\n"+\
            "Case NUMBER: 425752 with report id being S04-304-61B" 

goldString = "Accession Number: REMOVED_ACCESSION_ID                   Report Status Final\n"+\
            "Type Surginal 03\nPathology Report  REMOVED_ACCESSION_ID BREAST CORE NEEDLE\n"+\
            "Accesioned On: REMOVED_DATE\nRICHARDSON, ANDREA, K, M,D~PH.D\nPATIENT: REMOVED_PATIENT_NAME\n"+\
            "Something on REMOVED_MONTH first/second/third yaknow REMOVED_DATE REMOVED_MONTH, 02, 2016, REMOVED_DATE, REMOVED_DATE, REMOVED_DATE" 

test = False
xmlPath = "/c/Users/ksh1/Desktop/ReportDiagnosesByMRNDateSideMaxDXAll.xml"
outPath = "deidentifiedPathReports.p"
readXmlFile = True
deanon = True
dump = True


if __name__ == '__main__':
    if readXmlFile:
        print "Begin reading XML File"
        with open(xmlPath, 'rb') as fd:
            allData = xmltodict.parse(fd.read())
            pathReports = allData['dataroot']['ReportDiagnosesByMRNDateSideMaxDXAll']

        print "Begin deanon step"
        if deanon:
            cleanData = deIden(pathReports)

            if dump:
                p.dump(cleanData, open(outPath, 'wb')) 

    if test:
        cleanedAttempt = deIdenText(testString)







