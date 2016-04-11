#! /usr/bin/python

import smtplib

CRED_FILE = 'email_user_pass.txt'
REC_FILE = 'email_recipients.txt'

def sendNotificationMail(msg):
    credsFile = open(CRED_FILE, 'r')
    recFile = open(REC_FILE, 'r')
    mailUser  = credsFile.readline()
    mailPass = credsFile.readline()
    mailRec = recFile.readline()
    credsFile.close()
    recFile.close()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(mailUser, mailPass)
     
    server.sendmail(mailUser, mailRec, msg)
    server.quit()

def unitTests():
    sendNotificationMail('Last test message from python')

if __name__ == '__main__':
    unitTests()
