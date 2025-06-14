# Personalized Real Estate Agent Project
The `listings.html` file contains representative output for LLM personalized
real estate descriptions.

## Environment Set Up
```
python3 --version
Python 3.13.3

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Generate Home Listings
```
python homematch_listing_generator.py
python homematch_image_generator.py
```

## View Home Listings
```
python homematch_index_html.py; open index.html
```

## Run Jupyter Notebook
```
jupyter lab --browser=chrome homematch_notebook.ipynb
```