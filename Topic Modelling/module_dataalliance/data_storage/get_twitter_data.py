# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3.9.13 ('dataalliance')
#     language: python
#     name: python3
# ---

# %%
import requests
import time
from datetime import datetime, timedelta
from decouple import config
from iteration_utilities import unique_everseen
from tqdm import tqdm

# %%
from utils import create_collection, insert_records


# %%
# api functions
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    API_BEARER = config('TWITTER_BEARER')

    r.headers["Authorization"] = f"Bearer {API_BEARER}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


# %%
def date_range(start, end):
    start = datetime.fromisoformat(start[:-1]).astimezone()
    end = datetime.fromisoformat(end[:-1]).astimezone()

    delta = end - start  # as timedelta
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return days


# %%
def date_to_twitter_format(date: datetime):
    """Converts datetime object into a date string
    in the format that the twitter API accepts"""
    date = datetime.strftime(date, '%y/%m/%d %H:%M:%S')
    date = date.replace(' ', 'T')
    date = date.replace('/', '-')
    date = '20'+date+'.000Z'

    return date


# %%
def get_twitter_data(requests_per_day: int=1, start_date=None, end_date=None):
    """ 
    Makes the number of requests_per_day for each
    day in the dates between start_date and end_date.
    If no dates are selected it will make x requests for the default
    end date. 
    The requests are for the twitter search all endpoint 
    with a query to get covid related tweets.
    Returns a dictionary with the _id and text of the tweet.

    Parameters:
     - requests (default 1): number of requests per each day between
     start_date and end_date. Each request will bring 500 tweets.

      - end_date (defaults to now-30s): select the end date 
      of the tweets to retrieve. 
      Format should be: '2022-02-01T00:00:00.000Z'

      - start_date (optional). 
      Format should be: '2022-02-01T00:00:00.000Z'

    Twitter API limits:
     - recent endpoint: 100 results per request
     - full archive endpoint: 500 results per request
     - other limitations:
        - 10 million tweets per month
        - 50 requests per 15 min
    """

    # parameters
    url = "https://api.twitter.com/2/tweets/search/all"
    results_per_request = 500
    covid_query = '''
        (#covid-19 OR #covid19 OR #covid OR #corona OR #coronavirus OR #postcovid 
        OR #postcovidera OR #postcovid19 OR #postcorona OR #afterlockdown OR #backtonormal
        OR #postcovidtravel OR #travelagain OR #postlockdown OR #flattenthecurve 
        OR #covidiots OR #socialdistancing OR covid19 OR covid OR corona 
        OR coronavirus OR covid-19 OR postcovid OR postcovid19 OR postcorona 
        OR postcoronaera)
        -is:retweet -is:nullcast -is:reply lang:en
    ''' 
    params = {'query': covid_query,
              'start_time': start_date,
              'max_results': results_per_request,
              'tweet.fields': 'created_at'}

    # list all the days between start and end dates
    dates = date_range(start_date, end_date)

    # convert list into twitter format
    dates = [date_to_twitter_format(date) for date in dates]

    # initialize list
    records = []

    # pagination
    for day in tqdm(dates):
        # reset token
        params['next_token'] = None

        for i in range(requests_per_day):
            try:
                # insert end date
                params['end_time'] = day

                # make request
                response = requests.get(url, auth=bearer_oauth, params=params)
                if response.status_code != 200:
                    raise Exception(response.status_code, response.text)

                # save response
                json_response = response.json()

                # retrieve token for pagination
                try:
                    token = json_response['meta']['next_token']
                    params['next_token'] = token
                except:
                    pass
                
                records.append(json_response['data'])
                time.sleep(20)

            except:
                pass


    # flatten the list
    results = [item for sublist in records for item in sublist]

    # substitute id for _id for mongodb insert reasons
    for tweet in results:
        try:
            tweet['_id'] = tweet.pop('id')
        except:
            pass

    return results


# %%
# create mongodb collection
collection = create_collection('covid-19_final')

# Parameters
start = '2022-04-01T00:00:00.000Z'
end = '2022-09-24T00:00:00.000Z'

# %%
if __name__ == "__main__":    
    # save the tweets 
    tweets = get_twitter_data(requests_per_day=2, start_date=start, end_date=end)

    # delete duplicates
    all_tweets = list(unique_everseen(tweets))

    # store results in mongodb
    docs = insert_records(all_tweets, collection)

    # print message
    print(f'{docs} docs inserted')
