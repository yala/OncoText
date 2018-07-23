import requests
'''
    This is running example of how to use OncoText at test time.
    This assumes you have already downloaded snapshots from the MIT team or
    trained your own models using the "addTrain" and "train" interface.
'''
#0. Set up paths, user, and organ system you want to use.
request_path = 'http://localhost:5000/addUnlabeled'
oncotext_user = 'demo'
organ = "OrganBreast"

#1.  Add Unlabled example


# Format data, as list of reports, where each report is a dictionary:
reports = [ {
    'Report_Text': 'Place your pathology report raw text in this field',
    'EMPI': 'patientID',
    'MRN': 'another patient ID',
    'any_abritrary_key_you_want_preserved': 'If you add any key to the report dictionary (that isn"t and attribute we are labeling), it will be preserved.'
}
]

# 2. Send the request to OncoText
response = requests.post(request_path, data=json.dumps(reports),
                            params={'name':oncotext_user, 'organ':organ})

## Will return a 200 if it succeeds. Note, watch the logs for bad behavior
assert response.status_code == 200


# 3. Call predict

request_path = 'http://localhost:5000/predict'
response = requests.get(request_path, params={'name':oncotext_user,'organ':'organ'})
reports_with_predictions = json.loads(response.text)

print reports_with_predictions

