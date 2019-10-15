
from __future__ import absolute_import, division, print_function

from builtins import (bytes, str, open, super, range,
                      zip, round, input, int, pow, object, map, zip)


__author__ = "Andrea Tramacere"

import requests
#import ast
import json
#import random
#import string
#import time
#import os
import inspect
import sys
from astropy.io import ascii
#import base64

from collections import OrderedDict


from itertools import cycle

class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        try:
            ln = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            ln = inspect.currentframe().f_back.f_lineno
        self.args = "{0.__name__} (line {1}): {2}".format(type(self), ln, msg),
        sys.exit(self)


class APIError(NoTraceBackWithLineNumber):
    pass


class RemoteException(NoTraceBackWithLineNumber):

    def __init__(self, message='Remote analysis exception', debug_message=''):
        super(RemoteException, self).__init__(message)
        self.message=message
        self.debug_message=debug_message


def safe_run(func):

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
           message =  'the remote server response is not valid\n'
           message += 'possible causes: \n'
           message += '- connection error\n'
           message += '- wrong credentials\n'
           message += '- error on the remote server\n'
           message += '\n exception message: '
           message += '%s'%e
           raise RemoteException(message=message)

    return func_wrapper


class MagicClientAPI(object):
    def __init__(self,host='0.0.0.0',port=None,cookies=None,protocol='http'):

        self.host=host
        self.port=port
        self.cookies=cookies


        if self.host.startswith('htt'):
            self.url=host
        else:
            if protocol=='http':
                self.url= "http://%s"%(host)
            elif protocol=='https':
                self.url = "https://%s" % (host)
            else:
                raise  RuntimeError('protocol must be either http or https')

        if port is not None:
            self.url += ":%d" % (port)

        self._progress_iter = cycle(['|', '/', '-', '\\'])

    #@classmethod
    def build_from_envs(cls):
        pass
        #cookies_path = os.environ.get('ODA_API_TOKEN')
        #cookies = dict(_oauth2_proxy=open(cookies_path).read().strip())
        #host_url = os.environ.get('DISP_URL')
        #return cls(host=host_url, instrument='mock', cookies=cookies, protocol='http')



    #@safe_run
    def request(self,product='catalog',api='api/v1.0/magic',params=None,url=None):
        if url is None:
            url=self.url
        s = '%s/%s/%s' % (url, api, product)

        print('request',s,params)
        res = requests.get(s, params=params)
        #print(res.json())
        if 'error_message' in res.json():
            raise APIError('error on remote server: %s' % res.json()['error_message'])

        return res

    #@safe_run
    def get_catalog(self):
        res = self.request(product='catalog')
        #cat_rec = json.loads(res.json(), object_pairs_hook=OrderedDict)
        #print(json.dumps(cat_rec, indent=4))
        return res.json()

    #@safe_run
    def get_targets(self):
        res = self.request(product='targets')
        #targets = json.loads(res.json(), object_pairs_hook=OrderedDict)
        # print(json.dumps(cat_rec, indent=4))

        return res.json()

   # @safe_run
    def get_table_data(self,file_name):
        res = self.request(product='data',params = dict(file_name=file_name))
        _o_dict = json.loads(res.json())
        t_rec = ascii.read(_o_dict['astropy_table']['ascii'])
        return t_rec

    #@safe_run
    def search_by_name(self, target_name):
        res = self.request(product='search-by-name', params=dict(target_name=target_name))
        #targets = json.loads(res.json())
        return res.json()



