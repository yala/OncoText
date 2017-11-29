import cPickle as p
from datetime import datetime as date
import sys, os
sys.path.append("/home/nlp/RecordManagement")
from utils import parseXLS
sys.path.append("..")
import re
import numpy as np
from constants import *
from csv import DictWriter
from twilio.rest import Client
import pdb
import smtplib
import string

ACCOUNT_SID = 'AC7d8e9d65e6c370c90c464417090c1e75'
AUTH_TOKEN = '10e49b7b726debdfcd044f6b9ed2dbc5'

name = "mghMar"

def preprocessText(text):
    import re
    cleanText = re.sub(r"\W", " ", text)
    cleanText = ' '.join(cleanText.split('\n'))
    cleanText = re.sub(r"(----)+", "", cleanText)
    cleanText = re.sub(r"(====)+", "", cleanText)
    cleanText = cleanText.lower()
    return cleanText

def send_text_msg(results,path):
    num_categories = len(results)
    average_accur = sum([r['accuracy'] for r in results]) / num_categories
    msg = "Pathology Parser update: Retraining completed today! Average accuracy was "+ str(average_accur)+ " and full results are stored at "+path+"."
    print "Sending msg", msg  
    
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for number in [ '+12244657241', '+16176427014', '+18572651715']:
        client.messages.create(
           to= number, from_='+12248083411', body=msg)   
    return "Success"


def send_mail(msg):
    HOST = "nlp.partners.org"
    FROM =  "nlp@nlp.partners.org"
    SUBJECT = "Pathology Parser Update! (testing)"

    server = smtplib.SMTP(HOST)

    print "Sending msg", msg  

    for email in ["cyli@mgh.harvard.edu"]:#, "ayala@mgh.harvard.edu"]:
        BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % email,
            "Subject: %s" % SUBJECT ,
            "",
            msg
        ), "\r\n")

        server.sendmail(FROM, email, BODY)
    server.quit()


def calcScores(inFile, outPath=RESULTSDIR):
    reports = p.load(open('/home/nlp/pathology/returnedDB_'+name+'.p', 'rb'))
    db = [r for r in reports if ('filename' in r and r['filename']==inFile)]
    testSet = parseXLS(EVALDIR+inFile)
    text_to_gold = {}
    for d in testSet:
        #if not 'Report_Text_Segmented' in d:
        d['Report_Text_Segmented'] = preprocessText(d['Report_Text'])
        text_to_gold[ d['Report_Text_Segmented']] = d
    print "Len gold", len(text_to_gold)

    text_to_pred = {}
    for d in db:
        if d['Report_Text_Segmented'] in text_to_gold:
            text_to_pred[d['Report_Text_Segmented']] = d
    print "Len db", len(db)
    print "Len text_to_pred", len(text_to_pred)

    results = []
    for d in post_diagnoses:
        res = {'NAME':d}
        texts = [t for t in text_to_pred]

        #for t in texts:
            #if d in text_to_gold[t] and type(text_to_gold[t][d]) != str:
                #text_to_gold[t][d] = str(unicode(text_to_gold[t][d]).encode('utf-8'))
            #if d in text_to_gold[t] and text_to_gold[t][d] not in post_diagnoses[d]:
                #texts.remove(t)
                #print "Removing report with unknown value "+text_to_gold[t][d]+" for "+d

        pred, gold = [text_to_pred[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]],  [text_to_gold[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]]
        
        if len(pred) == 0:
            continue
        res['ACCURACY'] = sum([pred[i] == gold[i] for i in range(len(pred))])*100. / len(pred)
        res['PERCENTPOS'] = sum([g in ['1'] for g in gold])*100. / len(gold)

        truePos = sum([gold[i] == '1' and pred[i] == '1' for i in range(len(pred))])
        falsePos = sum([gold[i] == '0' and pred[i] == '1' for i in range(len(pred))])
        trueNeg = sum([gold[i] == '0' and pred[i] == '0' for i in range(len(pred))])
        falseNeg = sum([gold[i] == '1' and pred[i] == '0' for i in range(len(pred))])

        #print d
        #print "truePos", truePos
        #print "falsePos", falsePos
        #print "falseNeg", falseNeg
        precision = 1.*truePos / (truePos+falsePos) if (truePos+falsePos) > 0 else 0
        recall = 1.*truePos / (truePos+falseNeg) if (truePos+falseNeg) > 0 else 0
        f1 = 2.*(precision*recall)/(precision+recall) if (precision+recall) >0 else 0

        res['PRECISION'] = precision
        res['RECALL'] = recall
        res['F1'] = f1

        results.append(res)
    
    overallRes = {'NAME':'AVERAGE'}
    overallRes['ACCURACY'] = sum([r['ACCURACY'] for r in results]) / len(results)
    overallRes['PRECISION'] = sum([r['PRECISION'] for r in results]) / len(results)
    overallRes['RECALL'] = sum([r['RECALL'] for r in results]) / len(results)
    overallRes['F1'] = sum([r['F1'] for r in results]) / len(results)
    overallRes['PERCENTPOS'] = 'NA'

    results.append(overallRes)

    print results
   
    today = date.now().strftime("%Y-%d-%m")
    #dateStr = "-".join([str(s) for s in today])
    setName = inFile.split('.')[0]
    path = outPath+setName+'_'+today+'.csv'
    keys = ['NAME', 'PERCENTPOS', 'ACCURACY', 'PRECISION', 'RECALL', 'F1']
    print "Saving results to", path
    with open(path,'w') as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(results)

    return results, path
    
def main(sendText=True):
    message = ""
    for goldset in os.listdir(EVALDIR):
        if goldset.endswith('.xlsx'):
            results, path = calcScores(goldset)
            message += "\nRetraining completed today for "+str(goldset)+"!\nAverage accuracy was "+str(results[-1]['ACCURACY'])+". Full results are stored at "+path+".\n"

    if sendText:
        print "Sending email update..."
        send_mail(message)
    return results

if __name__ == "__main__":
    main(sendText=True)
