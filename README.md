## FEC Donor Data Analysis

This repo contains the code necessary to scrape, analyze, and predict campaign donations. 

Setup instructions:
To run this code, you will need to 
1) pull this repo to your local machine
2) create a file called ".env"
3) request APIs to access the following government websites:
- FEC API: https://api.open.fec.gov/developers/
- FBI API: https://api.data.gov/signup/
- Census API: https://api.census.gov/data/key_signup.html
4) Store the requested APIs in the .env file in the following format:
CENSUS_API_KEY=your_census_api_key
FBI_API_KEY=your_fbi_api_key
FEC_API_KEY=your_fec_api_key

Here's a walkthrough of all the different files:
- exec.ipynb contains all the data cleaning, analysis, visualizations, and training
- get_city_data.py contains functions to pull city-level data using the census and fbi apis
- get_fec_data.py contains functions to pull FEC data