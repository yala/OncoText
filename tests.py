from classifierAPI  import *
import datetime
import json
import unittest



class TestStringMethods(unittest.TestCase):

    def test_addData(self):
        sampleTrainNotPreprocessed = [{
            'ReportID':12,
            'Report_Text':"Bolease",
            "Red DCIS": "Present",
            "Red BreastSide": "RIGHT"

        }]
        with self.assertRaises(AssertionError):
            addData(sampleTrainNotPreprocessed, name="test")

        sampleTrainValid= [{
            'ReportID':12,
            'Report_Text':"Bolasd sadasd",
            'Report_Text_Segmented':"Bolease",
            "Red DCIS": "Present",
            "Red BreastSide": "RIGHT"
        }]

        self.assertEqual(addData(sampleTrainValid, name="test"), 0)


    def test_updateTrainSet(self):
        name = "test"
        model= "Boost"
        mode= ["Dev", "Prod"]

        for m in mode:
            self.assertEqual(updateTrainSet(name,model,m), 0)

    def test_trainAndPredict(self):
        name="test"
        mode="Dev"
        self.assertEqual(trainAndPredict(name,mode), 0)


    def test_interpretResults(self):
        name="test"
        results = interpretResults(name)
        self.assertEquals(0, 0)

    def test_getPredictions(self):
        name="test"
        repDb, epDb = getPredictions(name)
        for r in repDb:
            assert 'Owner' in r and r['Owner']==name
        self.assertEquals(0, 0)





if __name__ == '__main__':
    unittest.main()
