
def send_now(missing):
    from datetime import date
    import smtplib
    from smtplib import SMTPException

    from email.message import EmailMessage

    sender = 'Nexus Vlan Audit <no_reply@bics.com>'
    receivers = ['osama.aboelfath@bics.com']
    msg = EmailMessage()
    


    if missing is True:
        msg_body = """ Nexus audit report is ready and missing vlans were discovered
Find that attached report!"""
        msg.set_content(msg_body)
        #msg.add_header('Content-Disposition', 'attachment', filename='missing-{}.txt'.format(date.today()))
        with open('results/{}/missing.txt'.format(date.today()), 'rb') as content_file:
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype='txt', filename='missing-{}.txt'.format(date.today()))
    else:
        msg_body = """ Nexus audit report were just executed and no missing vlans were found!
Have a nice day
                   """

    msg['From'] = sender
    msg['To'] = receivers
    msg['Subject'] = 'Nexus Audit report for {}!'.format(date.today())

    message = ' This is a test e-mail message. '

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.send_message(msg)
        print("Mail sent!")
    except SMTPException:
        print("Error: unable to send email")

