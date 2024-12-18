import requests
import pandas as pd
import time


def get_econ_data(census_api_key, unique_places, years):
    results = []
    count = 1
    for index, row in unique_places.iterrows():
        print(f"{count} for {len(unique_places)}")
        count += 1
        place_fips = row['place_fips']
        for year in years:
            base_url = f"https://api.census.gov/data/{year}/acs/acs5"

            # Set up parameters
            params = {
                'get': 'NAME,B23025_003E,B23025_005E',
                'for': f'place:{place_fips}',
                'in': f'state:42', #PA fip
                'key': census_api_key
            }

            response = requests.get(base_url, params=params)
            result = {
                    'place_fips': place_fips,
                    'year': year,
                    'name': None,
                    'employed': None,
                    'unemployed': None
                }
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    values = data[1]
                    result['name'] = values[0]
                    result['employed'] = values[1]
                    result['unemployed'] = values[2]
                else:
                    print(f"Data's too short: {data}")
            else:
                print(f"Error for {place_fips}: {response.status_code}")
            results.append(result)

    econ_data = pd.DataFrame(results)
    return econ_data

def get_pa_crime_data(fbi_api_key):

    # Base URL from the documentation
    base_url = 'https://api.usa.gov/crime/fbi/cde'

    # Headers with API key
    params = {
        'from': '01-2015',
        'to': '01-2023',
        'API_KEY': fbi_api_key
    }

    # Get both violent and property crime data
    violent_url = f'{base_url}/summarized/state/PA/violent-crime'
    property_url = f'{base_url}/summarized/state/PA/property-crime'
    
    violent_response = requests.get(violent_url, params=params)
    property_response = requests.get(property_url, params=params)
    
    # Extract data
    violent_data = violent_response.json()['offenses']['rates']['Pennsylvania']
    property_data = property_response.json()['offenses']['rates']['Pennsylvania']

    # Create DataFrames
    df_violent = pd.DataFrame(list(violent_data.items()), columns=['date', 'violent_crime'])
    df_property = pd.DataFrame(list(property_data.items()), columns=['date', 'property_crime'])

    # Convert dates and sort
    df_violent['date'] = pd.to_datetime(df_violent['date'], format='%m-%Y')
    df_property['date'] = pd.to_datetime(df_property['date'], format='%m-%Y')

    # Merge the two DataFrames
    df_pa_crime = pd.merge(df_violent, df_property, on='date')
    df_pa_crime.sort_values('date', inplace=True)
    
    return df_pa_crime