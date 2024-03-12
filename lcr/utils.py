# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os
import requests
import sys

try:
    from urllib import urlretrieve
    from urllib2 import HTTPError
except ImportError:
    from urllib.request import urlretrieve
    from urllib.error import HTTPError

logger = logging.getLogger(__name__)

def download_urllib(url, path, header=None):
    check_dict = {'file_not_exist': False}
    def Schedule(a,b,c):
        '''
        a: the number downloaded of blocks
        b: the size of the block
        c: the size of the file
        '''
        if c == -1:
            #global file_not_exist
            check_dict['file_not_exist'] = True
            return

        per = 100.0 * a * b / c
        if per > 100 :
            per = 100
            sys.stdout.write("\r %.2f%%" % per)
            sys.stdout.flush()
            sys.stdout.write('\n')
        else:
            sys.stdout.write("\r %.2f%%" % per)
            sys.stdout.flush()
    try:
        if header is None or len(header) == 0:
            cmd_download = f"curl -L {url} -o {path}"
        else:
            cmd_download = f"curl -L --header '{header}' {url} -o {path}"
        #logger.debug("download command:%s" % cmd_download)
        ret = os.system(cmd_download)
        if ret != 0:
            logger.info("Failed to download file: %s" % url)
        #urlretrieve(url, path, Schedule)
        #if not check_dict['file_not_exist']:
        #    logger.info("File is found: %s" % url)
    except HTTPError as error:
        if error.code == 404:
            logger.info("File is found: %s" % url)
        else:
            raise error

    if not check_dict['file_not_exist']:
        logger.info("File is saved to %s" % path)
    return check_dict['file_not_exist']


def download_url_content(request_url):
    content = ""
    r = requests.get(request_url)
    if not r.ok and r.status_code == 404:
        logger.info("failed to get content because the url %s is not found" % request_url)
    elif not r.ok or r.status_code != 200:
        logger.info("Failed %s %s %s" % (r.url, r.reason, r.status_code))
    else:
        content = r.text
    return content
