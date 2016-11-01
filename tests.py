from classifierAPI  import *
import datetime
import json
import unittest



class TestStringMethods(unittest.TestCase):

    def test_addTraining(self):
        sampleTrainNotPreprocessed = [{
            'ReportID':12,
            'Report_Text':"Bolease",
            "Red DCIS": "Present",
            "Red BreastSide": "RIGHT"

        }]
        with self.assertRaises(AssertionError):
            updateTrainSet(sampleTrainNotPreprocessed)

        sampleTrainValid= [{
            'ReportID':12,
            'Report_Text':"Bolasd sadasd",
            'Report_Text_Segmented':"Bolease",
            "Red DCIS": "Present",
            "Red BreastSide": "RIGHT"
        }]

        self.assertEqual(updateTrainSet(sampleTrainValid), 0)



if __name__ == '__main__':
    unittest.main()
