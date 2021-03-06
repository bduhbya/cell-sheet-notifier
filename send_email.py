#! /usr/bin/python

import smtplib

CRED_FILE = 'email_user_pass.txt'
REC_FILE = 'email_recipients.txt'

def sendNotificationMail(subject, message):
    credsFile = open(CRED_FILE, 'r')
    recFile = open(REC_FILE, 'r')
    mailUser  = credsFile.readline()
    mailPass = credsFile.readline()
    credsFile.close()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(mailUser, mailPass)
 
    for mailRec in recFile:    
        newMessage = 'Subject: %s\n\n%s' % (subject, message)
        server.sendmail(mailUser, mailRec, newMessage)

    recFile.close()
    server.quit()

def unitTests():
    sendNotificationMail('Test SUBJECT', 'Unit testing message from python mail sender')

if __name__ == '__main__':
    unitTests()
