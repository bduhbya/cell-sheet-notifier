#! /usr/bin/python

from bs4 import BeautifulSoup
import urllib2

CHECKLIST_HEADER_TAG = 'h1'
H1_BEGIN_TAG = '<h1>'
H1_END_TAG = '</h1>'
EMPTY_PRODUCT = 'Checklist'
URL_PREFIX = 'http://www.paniniamerica.net/dspFullChecklistbyID.cfm?prod='
TEST_GOOD_PROD_NUM = '477'
TEST_BAD_PROD_NUM = '500'
TEST_GOOD_PROD = URL_PREFIX + TEST_GOOD_PROD_NUM
TEST_BAD_PROD = URL_PREFIX + TEST_BAD_PROD_NUM

def findHeader(soup):
    for header in soup.find_all(CHECKLIST_HEADER_TAG):
        content = str(header).split(H1_BEGIN_TAG)
        content = content[1].split(H1_END_TAG)
        return content[0].lstrip()

def isEmpty(headerContent):
    print('Found header data: ' + str(headerContent))
    return headerContent == EMPTY_PRODUCT

def validate(actual, expected):
    if actual != expected:
        print 'FAIL: Expected ' + str(expected) + ', got: ' + str(actual)
    else:
        print 'PASS: Product does not exist: ' + str(actual)


def unitTest():
    response = urllib2.urlopen(TEST_GOOD_PROD)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    content = findHeader(soup)
    print 'Validating product num: ' + TEST_GOOD_PROD_NUM
    validate(isEmpty(content), False)

    response = urllib2.urlopen(TEST_BAD_PROD)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    content = findHeader(soup)
    print 'Validating product num: ' + TEST_BAD_PROD_NUM
    validate(isEmpty(content), True)

if __name__ == "__main__":
    unitTest()
