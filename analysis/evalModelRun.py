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

evalDir = '/home/nlp/Dropbox (Partners HealthCare)/Extraction/EvalSets/'
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


def send_mail(results, path):
    HOST = "nlp.partners.org"
    FROM =  "nlp@nlp.partners.org"
    SUBJECT = "Pathology Parser Update! (testing)"

    server = smtplib.SMTP(HOST)

    num_categories = len(results)
    average_accur = sum([r['accuracy'] for r in results]) / num_categories
    msg = "Retraining completed today! Average accuracy was "+ str(average_accur)+ " and full results are stored at "+path+"."
    print "Sending msg", msg  

    for email in ["cyli@mgh.harvard.edu", "ayala@mgh.harvard.edu"]:
        BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % email,
            "Subject: %s" % SUBJECT ,
            "",
            msg
        ), "\r\n")

        server.sendmail(FROM, email, BODY)
    server.quit()



def main(inFile, outPath='/home/nlp/Dropbox (Partners HealthCare)/NLP_Results/',sendText=True) :

    #if mode == 'eval':
    #    db = p.load(open('/home/nlp/pathology/evalDB_'+name+'.p','rb'))
    #    testSet = p.load(open('/home/nlp/pathology/rnn/devReps.p','rb')) + p.load(open('/home/nlp/pathology/rnn/testReps.p','rb'))
    #elif mode == 'pakistani':
    #    db = p.load(open('/home/nlp/pathology/pakistaniDB_'+name+'.p','rb'))
    #    testSet = p.load(open('/home/nlp/pathology/externalDataSources/pakistani_data.p','rb'))

    reports = p.load(open('/home/nlp/pathology/returnedDB_'+name+'.p', 'rb'))
    db = [r for r in reports if ('filename' in r and r['filename']==inFile)]
    testSet = parseXLS(evalDir+inFile)
    text_to_gold = {}
    for d in testSet:
        # if mode == 'eval' or True:
        #     for k in diagToConventionDict:
        #         if not k in d:
        #             continue 
        #         ##Convert label from diag format to clean conv
        #         d[diagToConventionDict[k]] = d[k]
        #         ## convert frome onehot to str label
        #         label_ind = np.argmax(d[k])
        #         d[diagToConventionDict[k]] = constantValidLabelDict[k][label_ind]
        if not 'Report_Text_Segmented' in d:
            d['Report_Text_Segmented'] = preprocessText(unicode(d['Report_Text']).encode('utf-8'))
        text_to_gold[ d['Report_Text_Segmented']] = d
    print "Len gold", len(text_to_gold)
    text_to_pred = {}
    for d in db:
        if d["Report_Text_Segmented"] in text_to_gold:
            text_to_pred[d['Report_Text_Segmented']] = d
    print "len db", len(db)
    print "len text_to_pred", len(text_to_pred)
    results = []
    for d in conventionToDiagDict:
        res = {'name':d}
        texts = [t for t in text_to_pred]

        for t in texts:
            if d in text_to_gold[t] and type(text_to_gold[t][d]) != str:
                text_to_gold[t][d] = str(unicode(text_to_gold[t][d]).encode('utf-8'))
            if d in text_to_gold[t] and text_to_gold[t][d] not in constantValidLabelDict[conventionToDiagDict[d]]:
                try:
                    text_to_gold[t][d] = sqlToLabelDict[conventionToDiagDict[d]][text_to_gold[t][d]]
                except KeyError:
                    texts.remove(t)
                    print t, d
                    print text_to_gold[t][d]

        pred, gold = [text_to_pred[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]],  [text_to_gold[t][d] for t in texts if d in text_to_pred[t] and d in text_to_gold[t]]
        
        if len(pred) == 0:
            continue
        res['accuracy'] = sum([ pred[i] == gold[i] for i in range(len(pred))] )*100./ len(pred)
        res['percentPos'] = sum ([ g in ['Present','Yes'] for g in gold]) * 100./ len(gold)
        
        truePos =  sum([gold[i] in ['Present', 'Yes'] and pred[i] in ['Present', 'Yes'] for i in range(len(pred))])
        falsePos = sum([gold[i] in ['Absent', 'No'] and pred[i] in ['Present', 'Yes'] for i in range(len(pred))])
        trueNeg  = sum([gold[i] in ['Absent', 'No'] and pred[i] in ['Absent', 'No'] for i in range(len(pred))])
        falseNeg = sum([gold[i] in ['Present', 'Yes'] and pred[i] in ['Absent', 'No'] for i in range(len(pred))])


        precision = 1. * truePos / (truePos + falsePos) if (truePos + falsePos) > 0 else 0
        recall    =  1. * truePos / (truePos + falseNeg) if (truePos + falseNeg) > 0 else 0
        f1        =  2. * (precision * recall)  / (precision + recall) if (precision + recall) >0 else 0

        res['precision'] = precision
        res['recall'] = recall
        res['f1'] = f1

        results.append(res)
    
    overallRes = {'name':'average'}
    overallRes['accuracy'] = sum([r['accuracy'] for r in results]) / len(results)
    overallRes['precision'] = sum([r['precision'] for r in results]) / len(results)
    overallRes['recall'] = sum([r['recall'] for r in results]) / len(results)
    overallRes['f1'] = sum([r['f1'] for r in results]) / len(results)
    overallRes['percentPos'] = 'NA'

    results.append(overallRes)

    print results
   
    today = date.now().isocalendar()
    dateStr = "-".join([str(s) for s in today])
    setName = inFile.split('.')[0]
    path = outPath+setName+'_'+dateStr+'.csv'
    keys = ['name', 'percentPos', 'accuracy', 'precision', 'recall', 'f1']
    print "Saving results to", path
    with open(path,'w') as outCSV:
        writer = DictWriter(outCSV, keys)
        writer.writeheader()
        writer.writerows(results)
    if sendText:
        print "Sending email update..."
        send_mail(results, path)
    return results



if __name__ == "__main__":
    main(inFile='evalDB.xlsx' , sendText=True)
