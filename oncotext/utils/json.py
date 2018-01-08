import datetime

def make_json_compliant(data):
    for report in data:
        for key in report.items():
            if isinstance(r[k], (datetime.datetime, datetime.date)):
                r[k] = r[k].isoformat()
    return data



