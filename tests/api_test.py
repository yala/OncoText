import json
import os
import requests
import unittest
import pdb
import pickle
import uuid
from config import Config

DOMAIN = "http://localhost:5000/"
TRAIN_DB_PATH = Config.DB_TRAIN_PATH
UNK_DB_PATH = Config.DB_UNLABLED_PATH

ADDITIONAL_DATA = { }
FAKE_REPORT_TEXT = "Foo blah blah DCIS glue"
ADDITIONAL_DATA[Config.RAW_REPORT_TEXT_KEY] = FAKE_REPORT_TEXT





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
        payload = json.dumps(ADDITIONAL_DATA)
        params = {"name":self.name}


        response = requests.post( os.path.join(DOMAIN, 'addTrain'),
                                 data=payload,
                                 params=params )

        self.assertEqual(response.status_code, 200)

    def test_add_unk(self):
        payload = json.dumps(ADDITIONAL_DATA)
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
