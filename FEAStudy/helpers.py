from operator import itemgetter

def getMRNDB(db):
    mrns = {}

    for report in db:
        mrn = report['MRNPlusX']
        if mrn in mrns:
            mrns[mrn].append(report)
        else:
            mrns[mrn] = [report]

    for mrn in mrns:
        reports = mrns[mrn]
        
        sortedReports = sorted( reports, key=itemgetter('Report_Date_TimePlusX') )

        mrns[mrn] = sortedReports

    return mrns    