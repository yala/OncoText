import smtplib


def send_mail(msg, config):
    HOST = config['HOST']
    FROM =  config['FROM']
    SUBJECT = config['SUBJECT']

    server = smtplib.SMTP(HOST)

    for email in config['EMAIL_LIST']:
        BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % email,
            "Subject: %s" % SUBJECT ,
            "",
            msg
        ), "\r\n")

        server.sendmail(FROM, email, BODY)
    server.quit()