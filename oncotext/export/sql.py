import MySQLdb

# sends all breast reports to the AccessDB
def updateAccesDB(reportDB):
    reportDB = [r for r in reportDB if ('filename' not in r or r['filename'] not in os.listdir(EVALDIR))]
    reportDB = postProcessRules(reportDB)
    reportDB = aggregateEpisodes(reportDB)
    # reportDB = exportToJSON.portToJSON(reportDB)

    reportDBJ = [r for r in reportDB if r['Organ'] == '1']
    reportDBO = [r for r in reportDB if r['Organ'] == '0']
    print "Exporting", len(reportDBJ), "breast records"
    print "Exporting", len(reportDBO), "other records"

    p.dump(reportDBJ, open('/home/nlp/pathology/reportDB_access.p', 'wb'))

    db = MySQLdb.connect(host="localhost", user="root", passwd="nlpdb", db="reports")
    cur = db.cursor()
    dbKeys, placeholders = [k for k in columnKeys if k in reportDBJ[0]], ["%s" for i in columnKeys if i in reportDBJ[0]]

    try:
        cur.execute("DROP TABLE " + backupTableName)
    except Exception as e:
        print str(e)
        pass

    try:
        cur.execute("DROP TABLE " + backupNoBreastTableName )
    except Exception, e:
        print str(e)
        pass

    print "Moving breast reports to backup table..."
    cur.execute("CREATE TABLE " + backupTableName + " LIKE " + reportsTableName)
    cur.execute("INSERT INTO " + backupTableName + " SELECT * FROM " + reportsTableName)
    db.commit()
    cur.execute("DROP TABLE " + reportsTableName)
    cur.execute("CREATE TABLE " + reportsTableName + " (" + " TEXT, ".join(dbKeys) + " TEXT)")
    db.commit()
    print "done."

    print "Exporting breast records..."
    sql = ("INSERT INTO " + reportsTableName + " (" + ", ".join(dbKeys) + ") VALUES (" + ", ".join(placeholders) + ")")
    for report in reportDBJ:
        try:
            values = [report[k] for k in dbKeys]
        except Exception, e:
            print e
            print report.keys(), "but looking for keys", [k for k in dbKeys]
            continue

        try:
            cur.execute(sql, tuple(values))
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print report
                return None
            except IndexError:
                print "MySQL Error: %s" % str(e)
                print report
                return None
        except TypeError, e:
            print("MySQL TypeError", e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError", e)
            print report
            return None
    db.commit()
    print "done."

    print "Moving non breast reports to backup table..."
    cur.execute("CREATE TABLE " + backupNoBreastTableName + " LIKE " + reportsNoBreastTableName)
    cur.execute("INSERT INTO " + backupNoBreastTableName + " SELECT * FROM " + reportsNoBreastTableName)
    db.commit()
    cur.execute("DROP TABLE " + reportsNoBreastTableName)
    cur.execute("CREATE TABLE " + reportsNoBreastTableName + " (" + " TEXT, ".join(dbKeys) + " TEXT)")
    db.commit()
    print "done."

    print "Exporting non breast records..."
    sql = ("insert into " + reportsNoBreastTableName + " (" + ", ".join(dbKeys) + ") VALUES (" + ", ".join(placeholders) + ")")
    # print reportDBO[0]
    for report in reportDBO:
        try:
            values = [report[k] for k in dbKeys]
        except Exception, e:
            print e
            print report.keys(), "but looking for keys", [k for k in dbKeys]
            continue

        try:
            cur.execute(sql, tuple(values))
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                print report
                return None
            except IndexError:
                print "MySQL Error: %s" % str(e)
                print report
                return None
        except TypeError, e:
            print("MySQL TypeError", e)
            print report
            return None
        except ValueError, e:
            print("MySQL ValueError", e)
            print report
            return None
    db.commit()
    print "done."
    cur.close()
    db.close()

    return "Success"