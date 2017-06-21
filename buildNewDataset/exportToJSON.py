import pickle as p
import re
import random
import datetime
import pprint
from operator import itemgetter
import json
import sys
sys.path.append("..")
sys.path.append('../preprocessDataset')
import preprocessRawDb
from constants import *


def portToJSON(data, path=None, episodeMode = False, write=False):
    for report in data:
        try:
            for k in report:
                l = report[k]
                if isinstance(l, datetime.datetime) or isinstance(l, datetime.date):
                    report[k] = preprocessRawDb.utcToDate(l).isoformat()
        except Exception, e:
            print 'wtf'
            print report
            raw_input()

        if episodeMode:
            redLabels = labelsForEpisodes
        else:
            redLabels = diagnoses

        assert "ECE" in redLabels
        for label in redLabels:

            #Replace spaces in label name because otherwise website will breast
            assert "Red DCIS" in JSONLabelNameDict
            if label in JSONLabelNameDict:
                temp = report[label]
                del report[label]
                assert not label in report
                report[ JSONLabelNameDict[label] ] = temp
        
        if "MRNPlusX" in report:
            mrn =  report["MRNPlusX"]
            del report["MRNPlusX"]
            report["FakeMRN"] = mrn
        #assert "EIC" in report

    if write:
        chunkLen = len(data)/10
        for i in range(10):    
            jsonData = json.dumps(data[i* chunkLen : (i+1)*chunkLen])
            print "Len data to dump to JSON", len(jsonData)
            with open(path.split('.')[0]+'_'+str(i)+".json", 'wb') as f:
                f.write(jsonData)
    else:
        return data

if __name__ == "__main__":

    reportDB = p.load( open(outPath, 'rb'))
    episodeDB = p.load( open(episodePath, 'rb'))

    print "Dumping ReportDB"
    portToJSON(reportDB, JSONReportPath, write=True)
    print "Dumping EpisodeDB"
    portToJSON(episodeDB, JSONEpisodePath, True, write=True)



