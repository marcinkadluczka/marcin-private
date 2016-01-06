__author__ = 'marcin, mike'
#-*- coding: utf-8 -*-
"""
  Crawling utils - wrapped fetching library (urllib2) with some useful utils
  to hide wiring stuff.
"""
import gzip
import time
import urllib2
import sys
import zlib

from random import randint
from StringIO import StringIO


class UrlFetcher:
  """
    Url fetching class.
  """
  default_header_dict = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_1) ' +
                    'AppleWebKit/533.02 ' +
                    "(KHTML, like Gecko) Chrome/25.0.%d.85 Safari/537." %
                        randint(1000, 2500),
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'gzip,deflate',
      'Accept-Language': 'en-US,en;q=0.8',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive'
  }
  
  def __init__(self, headers_dict = None, cookies_dict = None, timeout = 20,
               debug_level = 0):
    """
        Parameters:
      :param headers_dict: Non-default headers
      :param cookies_dict: cookies dictionary to be provided
      :param timeout: timeout - default 20s
      :param debug_level: debug level to show some verbose logs
      :return: content of the page otherwise (error) None
    """
    self.header_dict = self.default_header_dict if headers_dict is None \
                       else headers_dict
    self.cookies_dict = cookies_dict
    self.timeout = timeout
    self.opener = urllib2.build_opener()
    self._content = None
    self._status_code = None
    self._error = None
    self._debug_level = debug_level
    
  def fetchUrl(self, url):
    """
      Fetch a given url and return content
    """
    if self._debug_level > 0:
      print "fetchUrl fetching %s" % url
    try:
      req = urllib2.Request(url, headers = self.header_dict)
      self.start_time = time.time()
      response = self.opener.open(req, timeout = self.timeout)
      self.end_time = time.time()
      if (response.info().has_key('Content-Encoding') and 
          response.info().get('Content-Encoding') == 'gzip'):
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj = buf)
        self._content = f.read()
      else:
        self._content = response.read()
      self._status_code = 200
    except urllib2.HTTPError, e:
      self.end_time = time.time()
      if self._debug_level > 0:
        print("Got error code %s" % e.code)
      try:
        self._content = e.read()
        try:
          if e.info().getheader('Content-Encoding') == 'gzip':
            response = zlib.decompress(response, 16 + zlib.MAX_WBITS)
        except:
          pass
      except:
        self._content = None
    except Exception, e:
      print "fetchUrl got exception: %s" % str(e)
      self._status_code = 601
      self.end_time = time.time()
    if self._debug_level > 0:
     print "fetchUrl fetched %s in %5.3fs with %s" % \
         (url, self.end_time - self.start_time, self._status_code)
    return self._content
    
if __name__ == "__main__":
  sys.settrace
  
  test_url = 'https://www.linkedin.com/?trk=nav_logo'
  print "Testing crawling_utils.py"
  fetcher = UrlFetcher(debug_level = 1)
  # Test fetching url
  body = fetcher.fetchUrl(test_url)
  print "got page:\n%.1000s" % body