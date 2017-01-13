from twilio.rest import TwilioRestClient
# put your own credentials here
ACCOUNT_SID = 'AC7d8e9d65e6c370c90c464417090c1e75'
AUTH_TOKEN = '10e49b7b726debdfcd044f6b9ed2dbc5'

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

client.messages.create(
    to = '(224) 465-7241',
    from_ = '(224) 801-3040 ',
    body = 'Test',
)
                    