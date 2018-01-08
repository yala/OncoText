import urllib2
import json
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

        self.name = "test_user-{}".format(uuid.uuid4())
        self.prod_name = "mghMar"

    def tearDown(self):
        train_db = pickle.load( open(TRAIN_DB_PATH,'rb'))
        if self.name in train_db:
            del train_db[key]
        pickle.dump(train_db, open(TRAIN_DB_PATH, 'wb'))

        unk_db = pickle.load( open(UNK_DB_PATH,'rb'))
        if self.name in unk_db:
            del unk_db[key]
        pickle.dump(unk_db, open(UNK_DB_PATH, 'wb'))

    def test_add_train(self):
        addit_train = pickle.load(open(ADD_TRAIN_PATH,'rb'))
        payload = json.dumps(addit_train)
        params = {"name":self.name}


        response = requests.post( os.path.join(DOMAIN, 'addTrain'),
                                 data=payload,
                                 params=params )

        assertEquals(response.status_code == 200)

    def test_add_unk(self):
        addit_unk = pickle.load(open(ADD_UNK_PATH,'rb'))
        payload = json.dumps(addit_unk)
        params = {"name":self.name}

        response = requests.post( os.path.join(DOMAIN, 'addUnlabeled'),
                                 data=payload,
                                 params=params )

        assertEquals(response.status_code == 200)

    def test_train(self):
        params = {"name":self.name}

        response = requests.get( os.path.join(DOMAIN, 'train'),
                                 params=params )

        assertEquals(response.status_code == 200)

    def test_predict_flow(self):
        addit_unk = pickle.load(open(ADD_UNK_PATH,'rb'))
        payload = json.dumps(addit_unk)
        params = {"name":self.name}

        response = requests.post( os.path.join(DOMAIN, 'addUnlabeled'),
                                 data=payload,
                                 params=params )
        response = requests.get( os.path.join(DOMAIN, 'train'),
                                 params=params )
        assertEquals(response.status_code == 200)
        response = requests.get( os.path.join(DOMAIN, 'predict'),
                                 params=params )
        assertEquals(response.status_code == 200)


    def test_predict_prod(self):
        params = {"name":self.prod_name}
        response = requests.get( os.path.join(DOMAIN, 'predict'),
                                 params=params )
        assertEquals(response.status_code == 200)

if __name__ == '__main__':
    unittest.main()
