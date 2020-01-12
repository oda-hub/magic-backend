MAGIC backend API Documentation
==========================================
*API for MAGIC backend*

What's the license?
-------------------

magic-backend is distributed under the terms of The MIT License.

Who's responsible?
-------------------
Andrea Tramacere

ISDC Data Centre for Astrophysics, Astronomy Department of the University of Geneva, Chemin d'Ecogia 16, CH-1290 Versoix, Switzerland


Installation
------------
Clone the repository `git clone https://github.com/andreatramacere/magic-backend`

cd to the `magic-backend` directory 

* using Anaconda
     * create a virtual environment (not necessary, but suggested): 
 
       `conda create --name magic-backend python=3.7 ipython jupyter`
    
       `conda activate magic-backend`

     * `conda install -c conda-forge --file   requirements.txt`
    
* or using PIP
     * create a virtual environment (not necessary, but suggested, https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
      
     * `pip install -r requirements.txt`
     
       OR if you are using system python (deprecated)
     
     * `sudo pip install -r requirements.txt`

* `python setup.py install`

Testing 
-------
- cd to the `test_examples` directory 

-  run the app: `run_magic_back_end.py`
 
1) with the notebook
    
    * browse this url to get api doc `http://localhost:5001/`
        * check the backend API doc
    
    * open the `magic-test.ipynb` notebook
    
2) with the frontend

  * browse this url `http://localhost:5001/index`
   