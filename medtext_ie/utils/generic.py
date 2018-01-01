
def hasCat(r, cat, loose=False):
    for c in cat:
        if not loose:
            if r[c] == '1':
                return True
        else:
            if c in r:
                return True
    return False


def isAnnotation(r):
    return hasCat(r, diagnoses, loose=True)


def validateTrainDb(trainDb):
    for r in trainDb:
        if "Report_Text_Segmented" not in r:
            print "Report_Text_Segmented not found in db!"
            return False

        for d in diagnoses:
            if d in r and not r[d] in diagnoses[d]:
                print "Found "+str(r[d])+" as value for diag "+str(d)+" but valid labels are only", diagnoses[d]
                return False
    return True
