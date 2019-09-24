from astropy.table import Table
import json
import  base64
import pickle
t=Table.read('data/19e/magic_19e_sed_fig3_mwl_target01.ecsv',format='ascii')
_binarys= pickle.dumps(t,protocol=2)
_o_dict={}
_o_dict['table']=_binarys
_o_dict=json.dumps(_o_dict)
_o_dict=json.loads(_o_dict)
t_rec=base64.b64decode(_o_dict['table'])
t_rec=pickle.loads(t_rec)
t_rec
