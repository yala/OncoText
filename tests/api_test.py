import json
import os
import requests
import unittest
import pdb
import pickle
import uuid

DOMAIN = "http://localhost:5000/"
TRAIN_DB_PATH = "/home/yala/oncotext_files/reportDBAPI_train.p"
UNK_DB_PATH = "/home/yala/oncotext_files/reportDBAPI_test.p"
ADD_TRAIN_PATH = "/home/yala/oncotext_files/test_data/addit_train.p"
ADD_UNK_PATH = "/home/yala/oncotext_files/test_data/addit_unlabeled.p"




class Test_MIT_App(unittest.TestCase):

    def setUp(self):

        self.name = "test_user-{}".format(uuid.uuid4())
        self.prod_name = "default"

    def tearDown(self):
        with open(TRAIN_DB_PATH,'rb') as f:
            train_db = pickle.load(f, encoding='bytes')
        if self.name in train_db:
            del train_db[self.name]
            with open(TRAIN_DB_PATH, 'wb') as f:
                pickle.dump(train_db, f)

        with open(UNK_DB_PATH,'rb') as f:
            unk_db = pickle.load( f, encoding='bytes')
        if self.name in unk_db:
            del unk_db[self.name]
            with open(UNK_DB_PATH, 'wb') as f:
                pickle.dump(unk_db, f)

    def test_add_train(self):
        with open(ADD_TRAIN_PATH,'rb') as f:
            addit_train = pickle.load(f)
        payload = json.dumps(addit_train)
        params = {"name":self.name}


        response = requests.post( os.path.join(DOMAIN, 'addTrain'),
                                 data=payload,
                                 params=params )

        self.assertEqual(response.status_code, 200)

    def test_add_unk(self):
        with open(ADD_UNK_PATH,'rb') as f:
            addit_unk = pickle.load(f)
        payload = json.dumps(addit_unk)
        params = {"name":self.name}

        response = requests.post( os.path.join(DOMAIN, 'addUnlabeled'),
                                 data=payload,
                                 params=params )

        self.assertEqual(response.status_code, 200)

    def test_full_predict_flow(self):
        addit_unk = pickle.load(open(ADD_UNK_PATH,'rb'))
        payload = json.dumps(addit_unk)
        params = {"name":self.name}

        response = requests.post( os.path.join(DOMAIN, 'addUnlabeled'),
                                 data=payload,
                                 params=params )
        self.assertEqual(response.status_code, 200)
        response = requests.get( os.path.join(DOMAIN, 'train'),
                                 params=params )
        self.assertEqual(response.status_code, 500)
        response = requests.post( os.path.join(DOMAIN, 'addTrain'),
                                 data=payload,
                                 params=params )
        self.assertEqual(response.status_code, 200)
        response = requests.get( os.path.join(DOMAIN, 'train'),
                                 params=params )
        self.assertEqual(response.status_code, 200)
        response = requests.get( os.path.join(DOMAIN, 'predict'),
                                 params=params )
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
