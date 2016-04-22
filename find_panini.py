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
unitTesting = False #Global switch to access test resources instead of live resources
TEST_GOOD_PROD_NUM = '477'
TEST_BAD_PROD_NUM = '500'
TEST_GOOD_PROD = VIEW_URL_PREFIX + TEST_GOOD_PROD_NUM
TEST_BAD_PROD = VIEW_URL_PREFIX + TEST_BAD_PROD_NUM
SAMPLE_POPULATED_PAGE = 'TestData/sample-populated-checklist.html'
SAMPLE_POPULATED_HEADER = 'Football 2016 Panini Collegiate Draft Picks Checklist'
SAMPLE_EMPTY_PAGE = 'TestData/sample-empty-product-page.html'
SAMPLE_NULL_PAGE = 'NOT_A_FILE'
SAMPLE_EMPTY_HEADER = 'Checklist'
TEST_PROD_NUM_RESOURCE = 'TestData/' + PROD_NUM_FILE_NAME

#Updated for each unit test with specific product resource
CHECK_NEW_PROD_TEST_CUR_RESOURCE = None

findHeaderTests = {SAMPLE_POPULATED_PAGE:SAMPLE_POPULATED_HEADER, SAMPLE_EMPTY_PAGE:SAMPLE_EMPTY_HEADER}
isEmptyTests = {SAMPLE_POPULATED_PAGE:False, SAMPLE_EMPTY_PAGE:True}
nextProdNumTests = {TEST_PROD_NUM_RESOURCE:'400'}
checkNewProductTests = {SAMPLE_POPULATED_PAGE:True, SAMPLE_EMPTY_PAGE:False, SAMPLE_NULL_PAGE:False}

def validate(testName, actual, expected):
    if actual != expected:
        print 'FAIL - ' + testName + ': Expected ' + str(expected) + ', got: ' + str(actual)
    else:
        print 'PASS - ' + testName + ': Expected and actual results match: ' + str(actual)

def getSoupFromFile(fileName):
    try:
        testPage = open(fileName, 'r')
    except IOError:
        return None
    
    html = testPage.read()
    testPage.close()
    return BeautifulSoup(html, 'html.parser')

def testFindHeader():
    for key, value in findHeaderTests.iteritems():
        soup = getSoupFromFile(key)
        result = findHeader(soup)
        validate('testFindHeader', result, value)

def testIsEmpty():
    for key, value in isEmptyTests.iteritems():
        testPage = open(key, 'r')
        html = testPage.read()
        soup = BeautifulSoup(html, 'html.parser')
        header = findHeader(soup)
        result = isEmpty(header)
        validate('testIsEmpty', result, value)
        testPage.close()

#TODO: Update when db changes from file to real db
def restoreTestDbProduct(productNum):
    #Put original value back
    updateNextProdNum(str(int(productNum) - 1))

def testGetNextProdNum():
    for key, value in nextProdNumTests.iteritems():
        result = getNextProdNum()
        validate('testGetNextProdNum', result, value)

def testUpdateNextProdNum():
    prevProd = getNextProdNum()
    expected = str(int(prevProd) + 1)
    updateNextProdNum(prevProd)
    actual = getNextProdNum()
    validate('testUpdateNextProdNum', expected, actual)
    restoreTestDbProduct(prevProd)

def testCheckNewProduct():
    global CHECK_NEW_PROD_TEST_CUR_RESOURCE
    for key, value in checkNewProductTests.iteritems():
        CHECK_NEW_PROD_TEST_CUR_RESOURCE = key
        testDbProduct = getNextProdNum()
        #TODO: Update to ensure product number from test db is restored
        result = checkNewProduct()
        actual = (result is not None)
        validate('testCheckNewProduct', value, actual)
        restoreTestDbProduct(testDbProduct)

unitTestFuncs = (testFindHeader, testIsEmpty, testGetNextProdNum, testUpdateNextProdNum, testCheckNewProduct)

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
def getProductResource(write):
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
def getNextProdNum():
    prodNumFile = getProductResource(False)
    nextProdNum = prodNumFile.readline().rstrip()
    prodNumFile.close()
    print 'Next product number: ' + nextProdNum
    return nextProdNum

#Updates the data storage for the next product number to check
#on the next run
#TODO: Update to use cloud DB
def updateNextProdNum(lastProdNum):
    nextProdNum = str(int(lastProdNum) + 1)
    print 'Updating db with next prodnum: ' + nextProdNum
    prodNumFile = getProductResource(True)
    prodNumFile.write(nextProdNum)
    prodNumFile.close()

def getProdSoup(nextProdNum):
    soup = None
    if not unitTesting:
        url = VIEW_URL_PREFIX + nextProdNum
        print 'Checking for product at URL: ' + url
        soup = getProductPageSoup(url)
    else:
        soup = getSoupFromFile(CHECK_NEW_PROD_TEST_CUR_RESOURCE)

    return soup

#Checks for the existance of the next product from data
#storage
def checkNewProduct():
    #Get next porduct number to check
    nextProdNum = getNextProdNum()
    print 'Checking for existence of product number: ' + nextProdNum
    soup = getProdSoup(nextProdNum)
    if soup is not None:
        returnData = []
        content = findHeader(soup)
        if isEmpty(content) is False:
            dloadUrl = DLOAD_URL_PREFIX + nextProdNum
            updateNextProdNum(nextProdNum)
            returnData.append(content)
            returnData.append(dloadUrl)
            returnData.append('\r\n')
            return returnData
    else:
        print 'ERROR: soup was None.  Issue with url'

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
    global unitTesting
    unitTesting = True
    for testFunc in unitTestFuncs:
        print 'Running test: ' + testFunc.__name__
        testFunc()
        print '*************'

if __name__ == "__main__":
    unitTest()
