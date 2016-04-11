#! /usr/bin/python

from bs4 import BeautifulSoup
from get_soup_page import getProductPageSoup
from send_email import sendNotificationMail

CHECKLIST_HEADER_TAG = 'h1'
H1_BEGIN_TAG = '<h1>'
H1_END_TAG = '</h1>'
EMPTY_PRODUCT = 'Checklist'
VIEW_URL_PREFIX = 'http://www.paniniamerica.net/dspFullChecklistbyID.cfm?prod='
DLOAD_URL_PREFIX = 'http://www.paniniamerica.net/excelChecklist.cfm?prod='
PROD_NUM_FILE_NAME = 'next_prod_num.txt'
SUBJECT_LINE = 'New Panini Checklist(s) Released'

#Test data
TEST_GOOD_PROD_NUM = '477'
TEST_BAD_PROD_NUM = '500'
TEST_GOOD_PROD = VIEW_URL_PREFIX + TEST_GOOD_PROD_NUM
TEST_BAD_PROD = VIEW_URL_PREFIX + TEST_BAD_PROD_NUM

#Finds the title of the product header in the returned web page
def findHeader(soup):
    for header in soup.find_all(CHECKLIST_HEADER_TAG):
        content = str(header).split(H1_BEGIN_TAG)
        content = content[1].split(H1_END_TAG)
        return content[0].lstrip()

#Determines if the product is an 'empty' product.  For Panini, an
#empty product has the title defined above.  A valid product has
#a specific name
def isEmpty(headerContent):
    print('Found header data: ' + str(headerContent))
    return headerContent == EMPTY_PRODUCT

#Gets the next product number to check
#TODO: Update to use cloud DB
def getNextProdNum():
    prodNumFile = open(PROD_NUM_FILE_NAME, 'r')
    nextProdNum = prodNumFile.readline()
    prodNumFile.close()
    print 'Next product number: ' + nextProdNum
    return nextProdNum

#Updates the data storage for the next product number to check
#on the next run
#TODO: Update to use cloud DB
def updateNextProdNum(lastProdNum):
    nextProdNum = str(int(lastProdNum) + 1)
    print 'Updating db with next prodnum: ' + nextProdNum
    prodNumFile = open(PROD_NUM_FILE_NAME, 'w')
    prodNumFile.write(nextProdNum)
    prodNumFile.close()
    

#Checks for the existance of the next product from data
#storage
def checkNewProduct():
    #Get next porduct number to check
    nextProdNum = getNextProdNum()
    print 'Checking for existence of product number: ' + nextProdNum
    url = VIEW_URL_PREFIX + nextProdNum
    dloadUrl = DLOAD_URL_PREFIX + nextProdNum
    soup = getProductPageSoup(url)
    if soup is not None:
        returnData = []
        content = findHeader(soup)
        if isEmpty(content) is False:
            updateNextProdNum(nextProdNum)
            returnData.append(content)
            returnData.append(dloadUrl)
            returnData.append('\r\n')
            return returnData

    return None

def notifiyRecipients(products):
    message = 'New checklist(s) uploaded to Panini\r\n\r\n'
    prodList = "\r\n".join(products)
    print 'Notifying recipients of new products: ' + prodList
    sendNotificationMail(SUBJECT_LINE, message + prodList)

#Checks if the next product number is empty or populated.
#If populated, notifies registered recipients and continues checking
#until products are not available
def checkForPaniniUpdates():
    products = []
    prodData = checkNewProduct()
    while prodData is not None:
        for value in prodData:
            products.append(value)
        prodData = checkNewProduct()

    if(len(products) > 0):
        notifiyRecipients(products)

# Testing functions
def validate(actual, expected):
    if actual != expected:
        print 'FAIL: Expected ' + str(expected) + ', got: ' + str(actual)
    else:
        print 'PASS: Product does not exist: ' + str(actual)

def unitTest():
#    soup = getProductPageSoup(TEST_GOOD_PROD)
#    content = findHeader(soup)
#    print 'Validating product num: ' + TEST_GOOD_PROD_NUM
#    validate(isEmpty(content), False)
#
#    soup = getProductPageSoup(TEST_BAD_PROD)
#    content = findHeader(soup)
#    print 'Validating product num: ' + TEST_BAD_PROD_NUM
#    validate(isEmpty(content), True)

#    updateNextProdNum(400)
    prodData = checkNewProduct()
    print("\r\n".join(prodData))

#    checkForUpdates()

if __name__ == "__main__":
    unitTest()
