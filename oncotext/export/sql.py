import MySQLdb
import pdb

def replace_sql_table(table, reports, column_keys,
                      sql_host, sql_user, sql_pass, sql_db, logger):
    if len(reports) == 0:
        logger.warn("Export SQL: Skip export {} because had 0 reports".format(table))
        return

    
    db = MySQLdb.connect(host=sql_host,
                         user=sql_user,
                         passwd=sql_pass,
                         db=sql_db)
    cur = db.cursor()

    dbKeys, placeholders = [], []
    for k in column_keys:
        if k in reports[0]:
            dbKeys.append(k)
            placeholders.append("%s")
    try:
        logger.info("Export SQL: Drop table {}".format(table))
        cur.execute("DROP TABLE {}".format(table))
    except Exception as e:
        logger.info("Export SQL: Drop table {} failed!".format(table))
        pass

    logger.info("Export SQL: Create table {}".format(table))
    cur.execute("CREATE TABLE {}  (  {} TEXT)".format(table, " TEXT, ".join(dbKeys) ))
    db.commit()


    logger.info("Export SQL:  Start populating table")

    sql_statement = ("INSERT INTO {} ( {} ) VALUES ({})").format(
                                    table,
                                    ", ".join(dbKeys),
                                    ", ".join(placeholders))

    for report in reports:
        try:
            values = [report[k] for k in dbKeys]
        except Exception as e:
            missing_keys = [k for k in dbKeys if not k in report]
            logger.error("Export SQL: Keys not found. Missing keys [{}]".format(missing_keys))
            continue

        try:
            cur.execute(sql_statement, tuple(values))
        except Exception as e:

            logger.error("Export SQL: SQL Insert failed. \nException({}). SQL statement {}".format(e, sql_statement))
            cur.close()
            db.close()
            return False

    db.commit()
    logger.info("Export SQL:  Done populating table")

    cur.close()
    db.close()
    return True


def export(reportDB, config, logger):
    prune_key = config['PRUNE_KEY']
    sql_host = config['SQL_HOST']
    sql_user = config['SQL_USER']
    sql_pass = config['SQL_PASSWD']
    sql_db = config['SQL_DB']
    breast_table = config['BREAST_REPORT_TABLE']
    nonbreast_table = config['NOBREAST_REPORT_TABLE']
    column_keys = config['COLUMN_KEYS']


    reportDB_breast = [r for r in reportDB if r[prune_key] == '1']
    reportDB_other = [r for r in reportDB if r[prune_key] == '0']

    logger.info( "Export SQL: Found {} Breast reports. Found {} Non-breast reports".format(len(reportDB_breast), len(reportDB_other)))


    for table, reports in [ (breast_table, reportDB_breast), (nonbreast_table, reportDB_other)]:

        sql_insert_fail = replace_sql_table(table, reports, column_keys,
                      sql_host, sql_user, sql_pass, sql_db, logger)

        if sql_insert_fail:
            return False
    return True
