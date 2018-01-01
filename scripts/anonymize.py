import xmltodict
import pickle as p
import re

months = ["jan", "feb", "mar", "apr", "jun", "jul", "sep", "oct", "nov", "dec", "january", "febuary", "march", "april", "june", "july", "september", "october", "november", "december"]

replaceStrings = ["REMOVED_DATE", "REMOVED_MONTH", "REMOVED_PATIENT_NAME", "REMOVED_ACCESSION_ID", "REMOVED_CASE_ID"]


# dump xml file into a deindentified python dictionary called deIdentifiedDict
def deIden(data):
    print "Calling Deint data"
    print "Number of dirty reports", len(data)
    debug = False
    examplesShown = 0
    cleanedData = []
    for pathReport in data:
        cleanedReport = {}
        for key in pathReport:
            # These keys constitute the annotation
            if not key == reportKey:
                cleanedReport[key] = pathReport[key]
        # This is the raw patient report. Might contain Patient Name, or dates or Accession number
        # All of which must be removed
        try:
            dirtyText = pathReport[reportKey]
            cleanText = deIdenText(dirtyText)
            cleanedReport[reportKey] = cleanText
            cleanedData.append(cleanedReport)

            if examplesShown < numExamples:
                print "dirty Text"
                print dirtyText
                print "-------------------"
                print "deidentified text"
                print cleanText
                print "#########################"
                examplesShown += 1
                raw_input()

        except Exception:
            if debug:
                print "Example diff report"
                print pathReport
                raw_input()
                showEx = False

    print "Number of clean reports", len(cleanedData)
    return cleanedData


# Takes a single path report and removes names, dates, and ID numbers
def deIdenText(dirtyText):
    debug = False
    if debug:
        print "calling deIdenDirtyText"
        print "DirtyText looks like"
        print dirtyText
        print '***************************'
    cleanLines = []
    lines = dirtyText.split('\n')
    for line in lines:
        # Check for dates (12/23/1212) format and if it matches months
        # Check for accesion number and &quot&
        # Check for patient names, with PATIENT
        # Remove Pathology Report Number
        # Format is [UPPERCASE]+[NUMBER]+

        cleanLine = stripDates(line)
        cleanLine = stripPatientName(cleanLine)
        cleanLine = stripAccesionNumber(cleanLine)

        cleanLines.append(cleanLine)

    cleanedText = "\n".join(cleanLines)

    if debug:
        raw_input()
        print "Cleaned text"
        print 
        print cleanedText
        raw_input()

    return cleanedText


# remove ,.?;; from end of string
def stripDelims(word):
    if word[-1] in ",.?;:":
        return word[:-1]
    else:
        return word


# Remove dates and replaces with REMOVED_DATE or REMOVED_MONTH
def stripDates(line):
    cleanWords = []

    words = line.split()
    # Remove months
    for w in words:
        word = stripDelims(w.lower())
        if word in months:
            cleanWords.append('REMOVED_MONTH')
        else:
            cleanWords.append(w)

    cleanedLine = " ".join(cleanWords) + " "
    # Replace "1.2 cm" with "1.2cm" so we don't remove measurments as dates
    cleanedLine = re.sub(mmMeasurementRegex, "mm ", cleanedLine)
    cleanedLine = re.sub(cmMeasurementRegex, "cm ", cleanedLine)
    cleanedLine = re.sub(dateRegex, " REMOVED_DATE ", cleanedLine)

    return cleanedLine


# Remove names of patients and replace with REMOVED_PATIENT_NAME
def stripPatientName(line):
    result = line
    if "PATIENT:" in result:
        result = re.sub(nameRegex, " REMOVED_PATIENT_NAME ", result)
    if "Patient Name" in result:
        result = re.sub(nameRegex2, " REMOVED_PATIENT_NAME ", result)
    
    return result


# Remove all occurances of accession number and repalce with "REMOVED_ACCESSION_ID"
def stripAccesionNumber(line):
    cleanedLine = re.sub(accesionNumberRegex, ' REMOVED_ACCESSION_ID ', line)
    cleanedLine = re.sub(caseNumberRegex, " REMOVED_CASE_ID ", cleanedLine)
    cleanedLine = re.sub(nameRegex3, "REMOVE_PATIENT_NAME", cleanedLine)    
    cleanedLine = re.sub(mrnRegex, "REMOVE_MRN", cleanedLine)    

    return cleanedLine


dateRegex = r"[ ]+\d+[- /.]+\d+[- /.]?\d*[ ,.;:?\n]"
mmMeasurementRegex = r"[ ]+mm[ .,;:?\n]?"
cmMeasurementRegex = r"[ ]+cm[ .,;:?\n]?"
accesionNumberRegex = r"[A-Z]+[0-9]+[-]?[A-Z]*[0-9]*[-]?[A-Z]*[0-9]*"
caseNumberRegex = r"\d{2}\d+"
nameRegex = r"[ ]*PATIENT:[ ]+[\w]+ \w*"
nameRegex2 = r"[ ]*Patient Name:[ ]*[\S]+[ ]+[\S]+"
nameRegex3 = r"labeled \"?\w+ \w+"
mrnRegex = r"#\d+-\d+-\d+"


testString = "Accession Number: S0430461B                   Report Status Final\n" + "Type Surginal 03\nPathology Report  S04-30465-B BREAST CORE NEEDLE\n" + "Accesioned On: 05/02003\nRICHARDSON, ANDREA, K, M,D~PH.D\nPATIENT: Adam Yala\n" + "Something on June first/second/third yaknow 02/25/1995 Feb, 02, 2016, 1992/02/12, 1992-02-12, 0-2-1992\n" + "Case NUMBER: 425752 with report id being S04-304-61B 0.12 cm" + "PATIENT: Adam Yala other content 32cm 23 mm haha 12 mm 15 in 1.2 mm 02/1995" + "Patient Name: Adam, yala roye jorce, gsdf sdfhsd fsdfh"

goldString = "Accession Number: REMOVED_ACCESSION_ID                   Report Status Final\n" + "Type Surginal 03\nPathology Report  REMOVED_ACCESSION_ID BREAST CORE NEEDLE\n" + "Accesioned On: REMOVED_DATE\nRICHARDSON, ANDREA, K, M,D~PH.D\nPATIENT: REMOVED_PATIENT_NAME\n" + "Something on REMOVED_MONTH first/second/third yaknow REMOVED_DATE REMOVED_MONTH, 02, 2016, REMOVED_DATE, REMOVED_DATE, REMOVED_DATE 0.12 cm"


test = False
readXmlFile = True
deanon = True
dump = True

# TODO: Matt, change these variables to point to where the XML file is, and what the path report column is labeled.
xmlPath = "/c/Users/ksh1/Desktop/ReportDiagnosesByMRNDateSideMaxDXAll.xml"
outPath = "deidentifiedPathReports.p"
reportKey = "Report_Text"
numExamples = 2


if __name__ == '__main__':
    if readXmlFile:
        print "Begin reading XML File"
        with open(xmlPath, 'rb') as fd:
            allData = xmltodict.parse(fd.read())
            pathReports = allData['dataroot']['ReportDiagnosesByMRNDateSideMaxDXAll']

        print "Begin deanon step"
        if deanon:
            cleanData = deIden(pathReports)

            print "Begin dump"
            if dump:
                p.dump(cleanData, open(outPath, 'wb')) 

    if test:
        cleanedAttempt = deIdenText(testString)
        print cleanedAttempt
