#! /usr/bin/python
from bs4 import BeautifulSoup
import urllib2

GOOD_TEST_URL = 'http://www.google.com'
BAD_TEST_URL = 'http://www.google-not-real-jo-mamm.com'

def getProductPageSoup(url):
    try:
        response = urllib2.urlopen(url)
    except (urllib2.URLError, ValueError):
        return None

    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def unitTest():
    soup = getProductPageSoup(GOOD_TEST_URL)
    if soup is not None:
        print 'PASS: soup is not None'
    else:
        print 'FAIL: soup expected to be not None'

    soup = getProductPageSoup(BAD_TEST_URL)
    if soup is None:
        print 'PASS: soup is None'
    else:
        print 'FAIL: soup expected to be None'

if __name__ == "__main__":
    unitTest()
