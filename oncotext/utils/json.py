import datetime
import json
import pdb

def make_json_compliant(data):
    for r in data:
        for k, v in r.items():
            if isinstance(v, (datetime.datetime, datetime.date)):
                r[k] = v.isoformat()
            if isinstance(v, bytes):
                r[k] = str(v)
            if isinstance(k, bytes):
                r[str(k)] = v
                del r[k]
    return data



