import datetime

DEFUALT_DATE = datetime.datetime(1900, 1, 1)

def utc_to_date(date):
    '''
        Given some date feild, return datetime.dateitme object
    '''
    if isinstance(date, datetime.date):
        return datetime.datetime(date.year, date.month, date.day)
    if isinstance(date, datetime.datetime):
        return date
    try:
        yyyymmdd = date[:8]
        return datetime.datetime.strptime(yyyymmdd, '%Y%m%d')
    except Exception:
        try:
            yyyymmdd = date[:8]
            year, mo, day = int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8])
            return datetime.date(year, mo, day)
        except Exception:
            try:
                yyyymmdd = date[:10]
                return datetime.datetime.strptime(yyyymmdd, '%Y-%m-%d')
            except Exception:
                try:
                    mmddyyyy = date.split()[0]
                    return datetime.datetime.strptime(mmddyyyy, '%m/%d/%Y')
                except Exception:
                    return DEFUALT_DATE

def set_timestamp(report, time_key, logger):
    '''
        Set report[time_key] to be a datetime obj
    '''
    if time_key in report:
        date = utc_to_date(report[time_key])
    elif 'Report_Date_TimePlusX' in report:
        date = utc_to_date(report['Report_Date_TimePlusX'])
    elif 'Report_Date_Time' in report:
        date = utc_to_date(report['Report_Date_Time'])
    else:
        date = DEFUALT_DATE
        logger.warn("date- date to set to {}. No known datefeild identified".format(DEFUALT_DATE))

    report[time_key] = date
    return report
