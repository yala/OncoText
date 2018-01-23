import pdb

def hasCat(r, cat, loose=False):
    for c in cat:
        if not loose:
            if r[c] == '1':
                return True
        else:
            if c in r:
                return True
    return False


def contains_annotations(reports, config):
    diagnoses = config['DIAGNOSES']
    for r in reports:
        if hasCat(r, diagnoses, loose=True):
            return True
    return False
