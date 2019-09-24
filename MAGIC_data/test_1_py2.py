
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from astropy.table import Table
import json
import  base64
import pickle
import requests
from astropy.io import ascii


res = requests.get('http://localhost:5000/api/v1.0/magic')
#print (res.json())
_o_dict = json.loads(res.json())
print(type(_o_dict))
t_rec = base64.b64decode(_o_dict['astropy_table']['binary'])
print(type(t_rec))
t_rec = pickle.loads(t_rec)
print(t_rec)
t_rec = ascii.read(_o_dict['astropy_table']['ascii'])
print(t_rec)
