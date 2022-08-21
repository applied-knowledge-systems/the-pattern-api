import requests
from datetime import datetime
import time

import os 

github_token = os.getenv('GITHUB_TOKEN')
headers = {"Authorization": 'token ' + github_token}


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

query = """
{
  viewer {
    sponsorshipsAsSponsor(first: 100) {
      nodes {
        sponsorable {
          ... on User {
            id
            email
            url
          }
          ... on Organization {
            id
            email
            name
            url
          }
        }
        tier {
          id
          name
          monthlyPriceInDollars
          monthlyPriceInCents
        }
      }
    }
  }
}
"""
response = run_query(query)
print(response)
