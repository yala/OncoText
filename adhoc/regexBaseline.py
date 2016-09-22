import pickle as p
import sys
sys.path.append("..")
import re
from constants import *
from createEpisodes import preprocessReports
import datetime

def replaceSpaces(w):
    return "_".join(w.split())

def guess(rep,diag):
    regex = "z%"
    result = 0

    if diag == "Red DCIS":
        regex = r'(ductal carcinoma in situ)|dcis'
    if diag == "Red LCIS":
        regex = r'(lobular carcinoma in situ)|lcis'
    if diag == "Red ADH":
        regex = r'(atypical ductal)|adh'
    if diag == "Red ALH":
        regex = r'(atypical lobular)|alh'
    if diag == "Red IDC":
        regex = r'(invasive ductal)|idc'
    if diag == "Red ILC":
        regex = r'(invasive lobular)|ilc'
    if diag == "Red FlatEpithelial":
        regex = r'(flat epithelial)|fea'
    if diag == "Red BluntAdenosis":
        regex = r'(blunt)'    
    if diag == "Red LobularNeoplasia":
        regex = r'(neoplasia)'  

    if not diag == "Red BreastSide":
        result= "Present" if not re.search(regex, rep.lower())== None else "Absent"
    else:
        result = "RIGHT" if not re.search(r'right', rep.lower())== None else "LEFT"
    
    debug = False
    if debug:
        print "-------- ", diag, "  -------"
        print rep
        print diag,result
        raw_input()

    return result
testSets = p.load(open('../buildTaghianClassifierTestSets.p','rb'))

for diag in testSets:
    if not diag in diagnoses:
        continue
    test = testSets[diag]
    labels = constantValidLabelDict[diag]
    with open("../classification_results/Breast/regex_"+replaceSpaces(diag)+'.txt','wb') as f:
        for rep, gold in test:
            line = ""
            gue = guess(rep, diag)
            for label in labels:
                if label == gold:
                    line += "1 "
                else:
                    line += "0 "
            for label in labels:
                if label == gue:
                    line += "1 "
                else:
                    line += "0 "
            f.write(line+"\n")
