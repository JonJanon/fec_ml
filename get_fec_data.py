import requests
import pandas as pd
import time
from typing import List, Dict
import backoff

class FECDataFetcher:
    def __init__(self, api_key: str, base_url: str, election_years:list, state:str):
        self.base_url = base_url
        self.session = requests.Session()

        self.candidate_params = {
            'api_key': api_key,
            'state': state,
            'election_year': election_years,
            'per_page': 100,
            'office': ['H']
        }

    def get_candidate_ids(self):
        candidate_details = []
        candidate_ids = []
        response = requests.get(f"{self.base_url}candidates/search/", params=self.candidate_params)
        data = response.json()
        results = data.get('results', [])
        for candidate in results:
            committee_id = None

            if candidate['principal_committees']:
                committee_id = candidate['principal_committees'][0]['committee_id']
                candidate_details.append({
                    'candidate_id': candidate['candidate_id'],
                    'incumbent_challenge': candidate['incumbent_challenge_full'],
                    'name': candidate['name'],
                    'party': candidate['party'],
                    'committee_id': committee_id
                    })
                candidate_ids.append(candidate['candidate_id'])
        return candidate_details

    @backoff.on_exception(backoff.expo, 
                         (requests.exceptions.RequestException, ValueError),
                         max_tries=5)
    def fetch_page(self, params: Dict, page: int) -> Dict:
        """Fetch a single page with exponential backoff retry"""
        params['page'] = page
        response = self.session.get(
            f"{self.base_url}schedules/schedule_a/",
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_donations(self, committee_ids: List[str], page_limit: int):
        results = []
        params = {
            'api_key': self.candidate_params['api_key'],
            'contributor_state': self.candidate_params['state'],
            'per_page': 100,
            'two_year_transaction_period': self.candidate_params['election_year']
        }

        for committee_id_group in committee_ids:
            params['committee_id'] = committee_id_group
            page = 1
            while True:
                print(f"Querying donor data for: {committee_id_group}")
                print(f'Params: {params}')
                try: 
                    data = self.fetch_page(params, page)
                    results.extend(data['results'])

                    if page >= data['pagination']['pages'] or page >= page_limit:
                        break
                    page += 1
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error fetching committee {committee_id_group}, page {page}: {e}")
                    break
            time.sleep(1)

        return pd.DataFrame(results)
