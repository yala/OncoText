from operator import itemgetter
import cPickle as p
import os, sys
sys.path.append("..")

def getMRNDB(db, id_key, date_key):
    mrns = {}

    for report in db:
        mrn = report[id_key]
        if mrn in mrns:
            mrns[mrn].append(report)
        else:
            mrns[mrn] = [report]

    for mrn in mrns:
        reports = mrns[mrn]
        sortedReports = sorted(reports, key=lambda x: x.get(date_key, ""))
        mrns[mrn] = sortedReports
    return mrns


def fits_criteria(report, include, exlude):

    for diag in exlude:
        assert str(report[diag]) in ['1', '0']
        if str(report[diag]) in ['1']:
            return False

    for diag in include:
        assert str(report[diag]) in ['1', '0']
        if str(report[diag]) in ['1']:
            return True

    return 'neither'

def run_query(exclude, include, yearFilt, config, logger):

    date_key = config['REPORT_TIME_KEY']
    id_key = config['PATIENT_ID_KEY']
    side_key = config['SIDE_KEY']

    results = []
    resultRecords = []
    resultFirstRecs = []

    mrns = getMRNDB(db, id_key, date_key)

    for mrn in mrns:
        reports = mrns[mrn]

        indx = 0
        firstRep = reports[indx]
        passes = fits_criteria(firstRep, include, exclude)
        queryIndx = indx

        def crit():
            repBool = passes == 'neither'
            return repBool and queryIndx < len(reports)-1

        while crit():
            queryIndx += 1
            passes = filt(reports[queryIndx], include, exclude)

        if passes is True:
            if yearFilt and sortedReports[queryIndx]['date'].year >= 2010:
                continue

            concurrent_exlcusion = False

            def inRange(r):
                return abs((r['date'] - reports[queryIndx]['date']).days) < 183

            concReps = [r for r in reports if inRange(r)]
            for r in concReps:
                conc = filt(r, include, exclude)
                if conc is False:
                    concurrent_exlcusion = True

            if not concurrent_exlcusion:
                results.extend(reports)

    return results



def export(reports, config, logger):

    sql_host = config['SQL_HOST']
    sql_user = config['SQL_USER']
    sql_pass = config['SQL_PASSWD']
    sql_db = config['SQL_DB']
    breast_table = config['BREAST_REPORT_TABLE']
    nonbreast_table = config['NOBREAST_REPORT_TABLE']
    column_keys = config['columnKeys']

    atypia_tables = config['ATYPIA_TABLES']

    for i, table_details in enumerate(export_tables):

        table, exclusion_crit, inclusion_crit, yearFilt = table_details
        reports = run_query(exclusion_crit, inclusion_crit, yearFilt)

        replace_sql_table(table, reports, column_keys,
                      sql_host, sql_user, sql_pass, sql_db)

        logger.info("Atypias: Export {} with {} Records".format(table,
                                                             len(reports))
