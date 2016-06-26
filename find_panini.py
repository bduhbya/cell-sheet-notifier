#! /usr/bin/python

import os
import shutil
from bs4 import BeautifulSoup
from get_soup_page import getProductPageSoup
from send_email import sendNotificationMail
from panini_test_classes import ProdSearchTest
import platform

END_LINE = None
if platform.system() is 'Windows':
    END_LINE = '\n\r'
else:
    END_LINE = '\n'

CHECKLIST_HEADER_TAG = 'h1'
H1_BEGIN_TAG = '<h1>'
H1_END_TAG = '</h1>'
B_BEGIN_TAG = '<b>'
B_END_TAG = '</b>'
TD_BEGIN_TAG = '<td>'
SEQ_ENTRY = 'Seq.'
TABLE_CELL_TAG = 'td'
EMPTY_PRODUCT = 'Checklist'
VIEW_URL_PREFIX = 'http://www.paniniamerica.net/dspFullChecklistbyID.cfm?prod='
DLOAD_URL_PREFIX = 'http://www.paniniamerica.net/excelChecklist.cfm?prod='
PROD_NUM_FILE_NAME = 'next_prod_num.txt'
SKELETON_PROD_NUMS_FILE_NAME = 'skeleton_prod_nums.txt'
SCRATCH_FILE = 'tempDb.txt'
NEW_PROD_SUBJECT_LINE = 'New Panini Checklist(s) Released'
SKELETON_PROD_SUBJECT_LINE = 'Skeleton Panini Checklist(s) Released'
NEW_PROD_MESSAGE = 'New checklist(s) uploaded to Panini\r\n\r\n'
SKELTON_PROD_MESSAGE = 'Skeleton checklist(s) uploaded to Panini\r\n\r\n'

#Test data/functions
unitTesting = False #Global switch to access test resources instead of live resources
TEST_GOOD_PROD_NUM = '477'
TEST_BAD_PROD_NUM = '500'
TEST_GOOD_PROD = VIEW_URL_PREFIX + TEST_GOOD_PROD_NUM
TEST_BAD_PROD = VIEW_URL_PREFIX + TEST_BAD_PROD_NUM
SAMPLE_POPULATED_PAGE = 'TestData/sample-populated-checklist.html'
SAMPLE_POPULATED_HEADER = 'Football 2016 Panini Collegiate Draft Picks Checklist'
SAMPLE_EMPTY_PAGE = 'TestData/sample-empty-product-page.html'
SAMPLE_SKELETON_PAGE = 'TestData/sample-skeleton-cheklist.html'
SAMPLE_NULL_PAGE = 'NOT_A_FILE'
TEST_DATA_PREFIX = 'TestData/'
SAMPLE_EMPTY_HEADER = 'Checklist'
CUR_TEST_PROD_NUM_RESOURCE = None
TEST_PROD_NUM_RESOURCE = TEST_DATA_PREFIX + PROD_NUM_FILE_NAME
TEST_SKELETON_WRITE_RESOURCE = TEST_DATA_PREFIX + 'test-skeleton-write.txt'
TEST_SKELETON_REMOVE_RESOURCE = TEST_DATA_PREFIX + 'test-skeleton-remove.txt'
TEST_SKELETON_FIRSTRUN_RESOURCE = TEST_DATA_PREFIX + 'test-skeleton-nofile.txt'
TEST_CURPROD_PROC_RESOURCE_INITIAL = TEST_DATA_PREFIX + 'test-curprod-proc-prodfile-initial.txt'
TEST_CURPROD_PROC_SKEL_RESOURCE_INITIAL = TEST_DATA_PREFIX + 'test-curprod-proc-skelfile-initial.txt'
TEST_CURPROD_PROC_RESOURCE = TEST_DATA_PREFIX + 'test-curprod-proc-prodfile.txt'
TEST_CURPROD_PROC_SKEL_RESOURCE = TEST_DATA_PREFIX + 'test-curprod-proc-skelfile.txt'

#Updated for each unit test with specific product resource
CHECK_NEW_PROD_TEST_CUR_RESOURCE = None
CHECK_SKELETON_PROD_TEST_CUR_RESOURCE = None
TEST_SKELETON_PROD_NUMS_FILE_NAME = None

findHeaderTests = {SAMPLE_POPULATED_PAGE:SAMPLE_POPULATED_HEADER, SAMPLE_EMPTY_PAGE:SAMPLE_EMPTY_HEADER}
isEmptyTests = {SAMPLE_POPULATED_PAGE:False, SAMPLE_EMPTY_PAGE:True}
nextProdNumTests = {TEST_PROD_NUM_RESOURCE:'400'}
isValidProductTests = {SAMPLE_POPULATED_PAGE:True, SAMPLE_EMPTY_PAGE:False, SAMPLE_NULL_PAGE:False}
isSkeletonTests = {SAMPLE_SKELETON_PAGE:True, SAMPLE_POPULATED_PAGE:False}
addSkeletonProdNumTests = {'400':['400'], '400,401':['400', '401'], '400,401,401,402':['400', '401', '402']}

#Skeleton removing item from list with one value
removeSkeletonSingleProdnumTestInit = ['400']
removeSkeletonSingleProdNumTests = {'400':[], '300':['400']}

#Skeleton removing item from list with multiple values
removeSkeletonMultiProdnumTestInit = ['400', '401', '402']
removeSkeletonMultiProdNumTests = {'400':['401', '402'], '401':['400', '402'], '402':['400', '401'], '403':['400', '401', '402']}

removeSkeletonProdNumTestNames = ('removeSkeletonSingleProdnumTest', 'removeSkeletonMultiProdNumTest')
removeSkeletonProdNumTestsInits = (removeSkeletonSingleProdnumTestInit, removeSkeletonMultiProdnumTestInit)
removeSkeletonProdNumTestsValues = (removeSkeletonSingleProdNumTests, removeSkeletonMultiProdNumTests)
NUM_SKELETON_TESTS = len(removeSkeletonProdNumTestNames)

#Current product procesing testing
populatedOrSkeletonProductTestMessageBodyOneProd = [SAMPLE_POPULATED_HEADER, 'http://www.paniniamerica.net/excelChecklist.cfm?prod=400', '\r\n']

populatedOrSkeletonProductTestMessageBodyTwoProd = [SAMPLE_POPULATED_HEADER, 'http://www.paniniamerica.net/excelChecklist.cfm?prod=400', '\r\n', \
                                                    SAMPLE_POPULATED_HEADER, 'http://www.paniniamerica.net/excelChecklist.cfm?prod=400', '\r\n']

populatedOrSkeletonProductTestMessageBodyThreeProd = [SAMPLE_POPULATED_HEADER, 'http://www.paniniamerica.net/excelChecklist.cfm?prod=400', '\r\n', \
                                                      SAMPLE_POPULATED_HEADER, 'http://www.paniniamerica.net/excelChecklist.cfm?prod=400', '\r\n', \
                                                      SAMPLE_POPULATED_HEADER, 'http://www.paniniamerica.net/excelChecklist.cfm?prod=400', '\r\n']

curProductNextResourceOneValid = (
                                  ProdSearchTest(SAMPLE_POPULATED_PAGE, False, populatedOrSkeletonProductTestMessageBodyOneProd, []), \
                                  ProdSearchTest(SAMPLE_EMPTY_PAGE, True, populatedOrSkeletonProductTestMessageBodyOneProd, []) \
                                 )

curProductNextResourceOneSkeleton = (
                                     ProdSearchTest(SAMPLE_SKELETON_PAGE, False, [], populatedOrSkeletonProductTestMessageBodyOneProd), \
                                     ProdSearchTest(SAMPLE_EMPTY_PAGE, True, [], populatedOrSkeletonProductTestMessageBodyOneProd) \
                                    )

curProductNextResourceOneValidOneSkeleton = (
                                             ProdSearchTest(SAMPLE_POPULATED_PAGE, False, populatedOrSkeletonProductTestMessageBodyOneProd, []), \
                                             ProdSearchTest(SAMPLE_SKELETON_PAGE, False, populatedOrSkeletonProductTestMessageBodyOneProd, populatedOrSkeletonProductTestMessageBodyOneProd), \
                                             ProdSearchTest(SAMPLE_EMPTY_PAGE, True, populatedOrSkeletonProductTestMessageBodyOneProd, populatedOrSkeletonProductTestMessageBodyOneProd) \
                                            )

curProductNextResourceOneSkeletonOneValid = (
                                             ProdSearchTest(SAMPLE_SKELETON_PAGE, False, [], populatedOrSkeletonProductTestMessageBodyOneProd), \
                                             ProdSearchTest(SAMPLE_POPULATED_PAGE, False, populatedOrSkeletonProductTestMessageBodyOneProd, []), \
                                             ProdSearchTest(SAMPLE_EMPTY_PAGE, True, populatedOrSkeletonProductTestMessageBodyOneProd, populatedOrSkeletonProductTestMessageBodyOneProd) \
                                            )

curProductNextResourceThreeValid = (
                                    ProdSearchTest(SAMPLE_POPULATED_PAGE, False, populatedOrSkeletonProductTestMessageBodyOneProd, []), \
                                    ProdSearchTest(SAMPLE_POPULATED_PAGE, False, populatedOrSkeletonProductTestMessageBodyTwoProd, []), \
                                    ProdSearchTest(SAMPLE_POPULATED_PAGE, False, populatedOrSkeletonProductTestMessageBodyThreeProd, []), \
                                    ProdSearchTest(SAMPLE_EMPTY_PAGE, True, populatedOrSkeletonProductTestMessageBodyThreeProd, []) \
                                   )

curProductNextResourceThreeSkeleton = (
                                       ProdSearchTest(SAMPLE_SKELETON_PAGE, False, [], populatedOrSkeletonProductTestMessageBodyOneProd  ), \
                                       ProdSearchTest(SAMPLE_SKELETON_PAGE, False, [], populatedOrSkeletonProductTestMessageBodyTwoProd  ), \
                                       ProdSearchTest(SAMPLE_SKELETON_PAGE, False, [], populatedOrSkeletonProductTestMessageBodyThreeProd), \
                                       ProdSearchTest(SAMPLE_EMPTY_PAGE, True, [], populatedOrSkeletonProductTestMessageBodyThreeProd) \
                                      )

#TODO: Test with 
#TODO: three valid, three skeleton
#TODO: four interchanging valid and skeleton
#TODO: no valid and no skeleton

#TODO: Test skeleton processing function

#TODO: Make seperate module
LogUnitTest = -1
LogError = 1
LogWarning = 2
LogInfo = 3
LogVerbose = 4

LOG_LEVEL = LogVerbose

def logMessage(msg, level=LogInfo):
    if(level <= LOG_LEVEL):
        print msg

def logUTMessage(msg):
    logMessage(msg, LogUnitTest)

def validate(testName, actual, expected):
    if actual != expected:
        logUTMessage('FAIL - ' + testName + ': Expected ' + str(expected) + ', got: ' + str(actual))
    else:
        logUTMessage('PASS - ' + testName + ': Expected and actual results match: ' + str(actual))

def validateNotEquals(testName, actual, expected):
    if actual == expected:
        logUTMessage('FAIL - ' + testName + ': Expected ' + str(expected) + ', got(not equal): ' + str(actual))
    else:
        logUTMessage('PASS - ' + testName + ': Expected and actual results do NOT match: ' + str(actual))

def openOrCreateFile(name, mode):
    retFile = None
    try:
        retFile = open(name, mode)
    except IOError:
        if mode == 'r':
            retFile = open(name, 'w')
            retFile.close()
            retFile = open(name, 'r')

    return retFile

def getSoupFromFile(fileName):
    try:
        testPage = open(fileName, 'r')
    except IOError:
        return None
    
    html = testPage.read()
    testPage.close()
    return BeautifulSoup(html, 'html.parser')

def testFindHeader(name):
    for key, value in findHeaderTests.iteritems():
        logUTMessage('------------------------------------------')
        logUTMessage('Testing: ' + key)
        soup = getSoupFromFile(key)
        result = findHeader(soup)
        validate(name, result, value)

def testIsEmpty(name):
    for key, value in isEmptyTests.iteritems():
        logUTMessage('------------------------------------------')
        logUTMessage('Testing: ' + key)
        soup = getSoupFromFile(key)
        header = findHeader(soup)
        result = isEmpty(header)
        validate(name, result, value)

#TODO: Update when db changes from file to real db
def restoreTestDbProduct(productNum):
    #Put original value back
    updateDbToNextProdNum(str(int(productNum) - 1))

def testGetNextProdNum(name):
    global CUR_TEST_PROD_NUM_RESOURCE
    for key, value in nextProdNumTests.iteritems():
        CUR_TEST_PROD_NUM_RESOURCE = key
        logUTMessage('------------------------------------------')
        logUTMessage('Testing: ' + key)
        result = getNextProdNum()
        validate(name, result, value)

def testUpdateNextProdNum(name):
    logUTMessage('------------------------------------------')
    prevProd = getNextProdNum()
    expected = str(int(prevProd) + 1)
    updateDbToNextProdNum(prevProd)
    actual = getNextProdNum()
    validate(name, expected, actual)
    restoreTestDbProduct(prevProd)

def testIsValidProduct(name):
    for key, value in isValidProductTests.iteritems():
        logUTMessage('------------------------------------------')
        logUTMessage('Testing: ' + key)
        soup = getSoupFromFile(key)
        actual = isValidProduct(soup)
        validate(name, value, actual)

def testCheckForSkeleton(name):
    for key, value in isSkeletonTests.iteritems():
        logUTMessage('------------------------------------------')
        logUTMessage('Testing: ' + key)
        soup = getSoupFromFile(key)
        actual = isSkeleton(soup)
        validate(name, value, actual)

def testOpenSkeletonFirstRunWithNoFile(name):
    global TEST_SKELETON_PROD_NUMS_FILE_NAME
    TEST_SKELETON_PROD_NUMS_FILE_NAME = TEST_SKELETON_FIRSTRUN_RESOURCE
    temp = getSkeletonResource('r')
    validateNotEquals(name, temp, None)
    if temp is not None:
        temp.close()
        os.remove(TEST_SKELETON_PROD_NUMS_FILE_NAME)

def testReadSkeletonFirstRunWithNoFile(name):
    global TEST_SKELETON_PROD_NUMS_FILE_NAME
    TEST_SKELETON_PROD_NUMS_FILE_NAME = TEST_SKELETON_FIRSTRUN_RESOURCE
    validate(name, getSkeletonProducts(), [])
    os.remove(TEST_SKELETON_PROD_NUMS_FILE_NAME)

def testAddSkeletonProdNum(name):
    global TEST_SKELETON_PROD_NUMS_FILE_NAME
    TEST_SKELETON_PROD_NUMS_FILE_NAME = TEST_SKELETON_WRITE_RESOURCE
    for key, value in addSkeletonProdNumTests.iteritems():
        logUTMessage('------------------------------------------')
        logUTMessage('Testing: ' + key)
        #Reset test file
        temp = getSkeletonResource('w')
        temp.close()
        for prodNum in key.split(','):
            addSkeletonProdNum(prodNum)

        validate(name, getSkeletonProducts(), value)

def testRemoveSkeletonProdNum(name):
    global TEST_SKELETON_PROD_NUMS_FILE_NAME
    TEST_SKELETON_PROD_NUMS_FILE_NAME = TEST_SKELETON_REMOVE_RESOURCE
    for testIdx in range(0, NUM_SKELETON_TESTS):
        for key, value in removeSkeletonProdNumTestsValues[testIdx].iteritems():
            logUTMessage('------------------------------------------')
            logUTMessage('Testing: ' + removeSkeletonProdNumTestNames[testIdx] + ', removing: ' + key)
            #Load initial values
            temp = getSkeletonResource('w')
            temp.close()
            for prodNum in removeSkeletonProdNumTestsInits[testIdx]:
                addSkeletonProdNum(prodNum)

            removeSkeletonProduct(key)

            validate(name, getSkeletonProducts(), value)

def initCurProdTest():
    global CUR_TEST_PROD_NUM_RESOURCE
    global TEST_SKELETON_PROD_NUMS_FILE_NAME
    CUR_TEST_PROD_NUM_RESOURCE = TEST_CURPROD_PROC_RESOURCE
    TEST_SKELETON_PROD_NUMS_FILE_NAME = TEST_CURPROD_PROC_SKEL_RESOURCE


def runCurProdTest(name, curTestData):
    global CHECK_NEW_PROD_TEST_CUR_RESOURCE
    actualProducts = []
    actualSkeletons = []
    for curTest in curTestData:
        copyProdNumTestResource(TEST_CURPROD_PROC_RESOURCE_INITIAL)
        copySkeletonTestResource(TEST_CURPROD_PROC_SKEL_RESOURCE_INITIAL)
        CHECK_NEW_PROD_TEST_CUR_RESOURCE = curTest.mPage
        actualSrchDone = processCurProduct(actualProducts, actualSkeletons)
        validate(name, actualSrchDone , curTest.mSearchDone)
        validate(name, actualProducts , curTest.mProductReturn)
        validate(name, actualSkeletons, curTest.mSkeletonReturn)


def testprocessCurProductOneValid(name):
    initCurProdTest()
    runCurProdTest(name, curProductNextResourceOneValid)

def testprocessCurProductOneSkeleton(name):
    initCurProdTest()
    runCurProdTest(name, curProductNextResourceOneSkeleton)

def testprocessCurProductOneValidOneSkeleton(name):
    initCurProdTest()
    runCurProdTest(name, curProductNextResourceOneValidOneSkeleton)

def testprocessCurProductOneSkeletonOneValid(name):
    initCurProdTest()
    runCurProdTest(name, curProductNextResourceOneSkeletonOneValid)

def testprocessCurProductThreeValid(name):
    initCurProdTest()
    runCurProdTest(name, curProductNextResourceThreeValid)

def testprocessCurProductThreeSkeleton(name):
    initCurProdTest()
    runCurProdTest(name, curProductNextResourceThreeSkeleton)

unitTestFuncs = (testFindHeader, \
                 testIsEmpty, \
                 testGetNextProdNum, \
                 testUpdateNextProdNum, \
                 testOpenSkeletonFirstRunWithNoFile, \
                 testReadSkeletonFirstRunWithNoFile, \
                 testIsValidProduct, \
                 testCheckForSkeleton, \
                 testAddSkeletonProdNum, \
                 testRemoveSkeletonProdNum, \
                 testprocessCurProductOneValid, \
                 testprocessCurProductOneSkeleton, 
                 testprocessCurProductOneValidOneSkeleton, \
                 testprocessCurProductOneSkeletonOneValid, \
                 testprocessCurProductThreeValid,
                 testprocessCurProductThreeSkeleton \
                )

#===============Module functional code=========================================

#Adds product to skeleton db
#TODO: Update when using real db
def addSkeletonProdNum(prodNum):
    skeletonDb = getSkeletonResource('r')
    prodExists = False
    for skeletonNum in skeletonDb:
        actualNum = skeletonNum.replace(END_LINE, '')
        if prodNum == actualNum:
            prodExists = True
            break

    skeletonDb.close()
    if prodExists is False:
        skeletonDb = getSkeletonResource('a')
        skeletonDb.write(prodNum + END_LINE)
        skeletonDb.close()

#Returns list of skeleton products in DB
#TODO: Test me
#TODO: Update when using real db
def getSkeletonProducts():
    skeletonDb = getSkeletonResource('r')
    prodNums = []
    for line in skeletonDb:
        prodNums.append(line.rstrip(END_LINE))

    return prodNums

#Removes product number from skeleton db
#TODO: Update when using real db
def removeSkeletonProduct(prodNum):
    skeletonDb = getSkeletonResource('r')
    tempDb = open(SCRATCH_FILE, 'w')

    for skeletonNum in skeletonDb:
        #Raw line in the file has the end line marker
        actualNum = skeletonNum.replace(END_LINE, '')
        if prodNum != actualNum:
            tempDb.write(skeletonNum)

    tempDb.close()
    skeletonDb.close()
    replaceSkeletonResource(SCRATCH_FILE)
    

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
def getProductResource(mode):
    if not unitTesting:
        return open(PROD_NUM_FILE_NAME, mode)
    else:
        return open(CUR_TEST_PROD_NUM_RESOURCE, mode)

#Helper function, not unit tested
def copyProdNumTestResource(src):
    shutil.copy(src, CUR_TEST_PROD_NUM_RESOURCE)

#Helper function, not unit tested
def copySkeletonTestResource(src):
    shutil.copy(src, TEST_SKELETON_PROD_NUMS_FILE_NAME)

#Helper function, not unit tested
def replaceSkeletonResource(src):
    if not unitTesting:
        shutil.move(src, SKELETON_PROD_NUMS_FILE_NAME)
    else:
        shutil.move(src, TEST_SKELETON_PROD_NUMS_FILE_NAME)

#Helper function, not unit tested
def getSkeletonResource(mode):
    if not unitTesting:
        return openOrCreateFile(SKELETON_PROD_NUMS_FILE_NAME, mode)
    else:
        return openOrCreateFile(TEST_SKELETON_PROD_NUMS_FILE_NAME, mode)

#Gets the next product number to check
#TODO: Update to use cloud DB
def getNextProdNum():
    prodNumFile = getProductResource('r')
    nextProdNum = prodNumFile.readline().rstrip()
    prodNumFile.close()
    logMessage('Next product number: ' + nextProdNum)
    return nextProdNum

#Updates the data storage for the next product number to check
#on the next run
#TODO: Update to use cloud DB
def updateDbToNextProdNum(lastProdNum):
    nextProdNum = str(int(lastProdNum) + 1)
    logMessage('Updating db with next prodnum: ' + nextProdNum)
    prodNumFile = getProductResource('w')
    prodNumFile.write(nextProdNum)
    prodNumFile.close()

def getProdSoup(nextProdNum):
    soup = None
    if not unitTesting:
        url = VIEW_URL_PREFIX + nextProdNum
        logMessage('Checking for product at URL: ' + url)
        soup = getProductPageSoup(url)
    else:
        soup = getSoupFromFile(CHECK_NEW_PROD_TEST_CUR_RESOURCE)

    return soup

#Checks for the existance of the next product from data
#storage
def isValidProduct(soup):
    if soup is not None:
        content = findHeader(soup)
        return (isEmpty(content) is False)
    else:
        logMessage('ERROR: soup was None.  Issue with url')

    return False

#TODO test me
def getProductData(prodNum, content):
    returnData = []
    dloadUrl = DLOAD_URL_PREFIX + prodNum
    returnData.append(content)
    returnData.append(dloadUrl)
    returnData.append('\r\n')
    return returnData

#TODO test me
def isSeqEntry(line):
    content = str(line).split(B_BEGIN_TAG)
    try:
        content = content[1].split(B_END_TAG)
    except IndexError:
        return False
    data = content[0].lstrip()
    return content[0].lstrip() == SEQ_ENTRY

#Skeleton checklists have a table with bold headers, followed by page data.
#Real checklist have simple table entrties after the bolded headers.  This
#function checks if the passed entry is a simple table entry starting with
#the '<td>' tag, or a complext page entry '<td ....... >'. Although this
#function is a simple one liner, it is left as a seperate function in the
#event more complexe processing is needed later on
#TODO test me
def isSimpleTableData(entry):
    return TD_BEGIN_TAG in str(entry)

#Sends notification of products through notification service
def notifiyRecipients(products, subject, message):
    prodList = "\r\n".join(products)
    if not unitTesting:
        logMessage('Notifying recipients of new products: ' + prodList)
        sendNotificationMail(subject, message + prodList)
    else:
        logMessage('notifiyRecipients, Notifying recipients of new products: ' + prodList, LogUnitTest)
                                                          
#Checks if a non-empty checkist is a skeleton or not      
def isSkeleton(soup):
    nextLine = None
    seqFnd = False
    for cell in soup.find_all(TABLE_CELL_TAG):
        if seqFnd is True:
            nextLine = cell
            break

        seqFnd = isSeqEntry(cell)

    return (isSimpleTableData(nextLine) is False)

def processCurProduct(products, skeletonProducts):
    curProdNum = getNextProdNum()
    logMessage('Checking for existence of product number: ' + curProdNum, LogUnitTest)
    soup = getProdSoup(curProdNum)
    prodSrchDone = not isValidProduct(soup)
    if not prodSrchDone:
        updateDbToNextProdNum(curProdNum)
        prodData = getProductData(curProdNum, findHeader(soup))
        if isSkeleton(soup):
            logMessage('Skeleton list found at: ' + curProdNum, LogUnitTest)
            addSkeletonProdNum(curProdNum)
            skeletonProducts.extend(prodData)
        else:
            products.extend(prodData)

    return prodSrchDone
 
def processSkeletonProducts(products):
    #Check if pending skeleton lists are updated to full products
    for curSkeleton in getSkeletonProducts():
        soup = getProdSoup(curSkeleton)
        if not isSkeleton(soup):
            logMessage('Old skeleton is now valid checklist: ' + curSkeleton, LogUnitTest)
            products.extend(getProductData(curSkeleton, findHeader(soup)))
            removeSkeletonProduct(curSkeleton)

#Checks for new products.
#  if new product found, updates next new product data base
#  if new product is skeleton, add to skeleton db and add data to skeleton mail data
#  else if new product is full, adds data to mailed
#  else if not new product do not update dbs
#
#If skeleton DB has products, check if those products are still skeletons
#  if skeleton, do nothing
#  else if not skeleton, add to product data to be mailed and remove from product db
def checkForPaniniUpdates():
    products = []
    skeletonProducts = []
    prodSrchDone = False
    #Check for new product checklists
    prodSrchDone = processCurProduct(products, skeletonProducts)
    while not prodSrchDone:
        prodSrchDone = processCurProduct(products, skeletonProducts)

    processSkeletonProducts(products)

    if(len(products) > 0):
        notifiyRecipients(products, NEW_PROD_SUBJECT_LINE, NEW_PROD_MESSAGE)

    if(len(skeletonProducts) > 0):
        notifiyRecipients(skeletonProducts, SKELETON_PROD_SUBJECT_LINE, SKELTON_PROD_MESSAGE)


def unitTest():
    global unitTesting
    global LOG_LEVEL
    unitTesting = True
    LOG_LEVEL = LogUnitTest
    for testFunc in unitTestFuncs:
        logUTMessage('Running test: ' + testFunc.__name__)
        testFunc(testFunc.__name__)
        logUTMessage('*********************************************')

if __name__ == "__main__":
    unitTest()
