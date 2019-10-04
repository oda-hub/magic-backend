MAGIC backend API
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
-------------------
1) Anaconda
    * `conda config --add channels conda-forge`
    * `conda install --file requirements.txt`
    * `python setup.py install`
    
2) PIP
    * `pip install -r requirements.txt`
    * `python setup.py install`

Documentation
-------------------
A) For local development  set the `PORT` in the config.py to '5000'

1) run the app: `python micro_app.py`
2) browse this url to get api doc `http://localhost:5000/`
3) open the `magic-test.ipynb` notebook

B) For  deployment: 
1) set the `PORT` in the config.py to the valued used on that machine
