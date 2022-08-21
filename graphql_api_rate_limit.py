import requests
from datetime import datetime
import time

import os 

github_token = os.getenv('GITHUB_TOKEN')

real_requests_post = requests.post
def wrap_requests_post(*args, **kwargs):
    if not 'headers' in kwargs:
        kwargs['headers'] = {}
    kwargs['headers']['Authorization'] = 'token ' + github_token
    response = real_requests_post(*args, **kwargs)
    if 'x-ratelimit-used' in response.headers._store:
        print("ratelimit status: used %s of %s. next reset in %s minutes" % (
            response.headers['X-RateLimit-Used'],
            response.headers['X-RateLimit-Limit'],
            datetime.utcfromtimestamp(int(response.headers['X-RateLimit-Reset']) - time.time()).strftime('%M:%S')
        ))
    return response
requests.post = wrap_requests_post

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
response = requests.post('https://api.github.com/graphql', json={'query': query})
data = response.json()
print(response._content)

# Find who user is sponsoring
# query {
#   user(login: "cheshire137") {
#     sponsoring(first: 10) {
#       totalCount
#       nodes {
#         ... on User { login }
#         ... on Organization { login }
#       }
#     }
#   }
# }