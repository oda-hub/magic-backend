
from __future__ import absolute_import, division, print_function

from builtins import (open, str, range,
                      object)

from astropy.table import Table
import json
import  base64
import pickle
import requests
from astropy.io import ascii



res = requests.get('http://localhost:32790/api/v1.0/magic/get-catalog')
cat_rec=json.loads(res.json())
print(cat_rec.keys())
print(cat_rec['File list MAGIC'])

res = requests.get('http://localhost:32790/api/v1.0/magic/get-data',params=dict(file_name='magic_19e_sed_fig3_nofit_target01.ecsv'))
_o_dict=json.loads(res.json())
t_rec = ascii.read(_o_dict['astropy_table']['ascii'])
print(t_rec)