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

#Test data/functions
TEST_GOOD_PROD_NUM = '477'
TEST_BAD_PROD_NUM = '500'
TEST_GOOD_PROD = VIEW_URL_PREFIX + TEST_GOOD_PROD_NUM
TEST_BAD_PROD = VIEW_URL_PREFIX + TEST_BAD_PROD_NUM
SAMPLE_POPULATED_PAGE = 'TestData/sample-populated-checklist.html'
SAMPLE_POPULATED_HEADER = 'Football 2016 Panini Collegiate Draft Picks Checklist'
SAMPLE_EMPTY_PAGE = 'TestData/sample-empty-product-page.html'
SAMPLE_EMPTY_HEADER = 'Checklist'
TEST_PROD_NUM_RESOURCE = 'TestData/' + PROD_NUM_FILE_NAME

findHeaderTests = {SAMPLE_POPULATED_PAGE:SAMPLE_POPULATED_HEADER, SAMPLE_EMPTY_PAGE:SAMPLE_EMPTY_HEADER}
isEmptyTests = {SAMPLE_POPULATED_PAGE:False, SAMPLE_EMPTY_PAGE:True}
nextProdNumTests = {TEST_PROD_NUM_RESOURCE:'400'}

def validate(testName, actual, expected):
    if actual != expected:
        print 'FAIL - ' + testName + ': Expected ' + str(expected) + ', got: ' + str(actual)
    else:
        print 'PASS - ' + testName + ': Expected and actual results match: ' + str(actual)

def testFindHeader():
    for key, value in findHeaderTests.iteritems():
        testPage = open(key, 'r')
        html = testPage.read()
        soup = BeautifulSoup(html, 'html.parser')
        result = findHeader(soup)
        validate('testFindHeader', result, value)
        testPage.close()

def testIsEmpty():
    for key, value in isEmptyTests.iteritems():
        testPage = open(key, 'r')
        html = testPage.read()
        soup = BeautifulSoup(html, 'html.parser')
        header = findHeader(soup)
        result = isEmpty(header)
        validate('testIsEmpty', result, value)
        testPage.close()

def testGetNextProdNum():
    for key, value in nextProdNumTests.iteritems():
        result = getNextProdNum(True)
        validate('testGetNextProdNum', result, value)

def testUpdateNextProdNum():
    prevProd = getNextProdNum(True)
    expected = str(int(prevProd) + 1)
    updateNextProdNum(prevProd, True)
    actual = getNextProdNum(True)
    validate('testUpdateNextProdNum', expected, actual)
    #Put original value back
    updateNextProdNum(str(int(prevProd) - 1), True)

unitTestFuncs = (testFindHeader, testIsEmpty, testGetNextProdNum, testUpdateNextProdNum)

#===============Module functional code=========================================

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

#Helper function, not unit tested
def getProductResource(unitTesting, write):
    mode = None
    if write:
        mode = 'w'
    else:
        mode = 'r'

    if not unitTesting:
        return open(PROD_NUM_FILE_NAME, mode)
    else:
        return open(TEST_PROD_NUM_RESOURCE, mode)

#Gets the next product number to check
#TODO: Update to use cloud DB
def getNextProdNum(unitTesting=False):
    prodNumFile = getProductResource(unitTesting, False)
    nextProdNum = prodNumFile.readline().rstrip()
    prodNumFile.close()
    print 'Next product number: ' + nextProdNum
    return nextProdNum

#Updates the data storage for the next product number to check
#on the next run
#TODO: Update to use cloud DB
def updateNextProdNum(lastProdNum, unitTesting=False):
    nextProdNum = str(int(lastProdNum) + 1)
    print 'Updating db with next prodnum: ' + nextProdNum
    prodNumFile = getProductResource(unitTesting, True)
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

#Sends notification of products through notification service
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


def unitTest():
    for testFunc in unitTestFuncs:
        testFunc()
        print '*************'

if __name__ == "__main__":
    unitTest()
