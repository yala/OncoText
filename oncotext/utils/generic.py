import pdb

def getOrgan(r, config):
    best = ["", 0]
    for o in config['COLUMN_KEYS']:
        matches = len(r.keys() & config['POST_DIAGNOSES'][o].keys())
        if matches >= best[1]:
            best[0] = o
            best[1] = matches

    return best[0]


def hasCat(r, cat, loose=False):
    for c in cat:
        if not loose:
            if r[c] == '1':
                return True
        else:
            if c in r:
                return True
    return False


def contains_annotations(reports, organ, config):
    diagnoses = config['DIAGNOSES'][organ]
    for r in reports:
        if hasCat(r, diagnoses, loose=True):
            return True
    return False
