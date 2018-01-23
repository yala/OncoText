import json
import os
import requests
import unittest
import pdb
import pickle
import uuid

DOMAIN = "http://localhost:5000/"
TRAIN_DB_PATH = "pickle_files/reportDBAPI_train.p"
UNK_DB_PATH = "pickle_files/reportDBAPI_test.p"
ADD_TRAIN_PATH = "tests/data/addit_train.p"
ADD_UNK_PATH = "tests/data/addit_unlabeled.p"




class Test_MIT_App(unittest.TestCase):

    def setUp(self):

        self.prod_name = "default"

    def tearDown(self):
        pass

    def test_train_pred_prod(self):
        params = {"name":self.prod_name}
        payload = {}

        response = requests.get( os.path.join(DOMAIN, 'train'),
                                 params=params )
        self.assertEqual(response.status_code, 200)

        response = requests.get( os.path.join(DOMAIN, 'predict'),
                                 data = payload,
                                 params=params )
        self.assertEqual(response.status_code, 200)
        

if __name__ == '__main__':
    unittest.main()
