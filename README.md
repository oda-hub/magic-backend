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
1) Anaconda
    * `conda config --add channels conda-forge`
    * `conda install --file requirements.txt`
    
2) PIP
    * `pip install -r requirements.txt`

Testing 
-------
cd to the `magic-backend` directory 

A) For local development  

1) run the app: `python micro_app.py`
2) browse this url to get api doc `http://localhost:5000/`
3) open the `magic-test.ipynb` notebook

B) For  deployment: 
1) `python micro_app.py -port YOUR_PORT_NUMBER`
