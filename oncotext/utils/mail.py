import smtplib


def send_mail(msg, config):
    HOST = config['HOST']
    FROM =  config['FROM']
    SUBJECT = config['SUBJECT']

    server = smtplib.SMTP(HOST)

    for email in config['EMAIL_LIST']:
        BODY = "From: {} \n\rTo: {} \n\rSubject:{}\n\r{}".format(
                                                        FROM,
                                                        email,
                                                        SUBJECT,
                                                        msg)

        server.sendmail(FROM, email, BODY)
    server.quit()
