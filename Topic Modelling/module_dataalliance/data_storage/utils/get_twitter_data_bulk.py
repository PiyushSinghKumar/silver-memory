import argparse
import logging
import os
import requests
# import requests_cache
import time
from decouple import config
from iteration_utilities import unique_everseen
from tqdm import tqdm

from utils import create_collection, insert_records

# logger for the cron job
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'cron_log.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


def do_logging(message):
    logger.info(f'Data successfully fetched with the following parameters: {message}')


# api functions
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    API_BEARER = config('TWITTER_BEARER')

    r.headers["Authorization"] = f"Bearer {API_BEARER}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def get_twitter_data_bulk(minutes: int=1, end=None):
    """ 
    Makes the request to the twitter search all endpoint 
    with a query to get covid related tweets.
    Returns a dictionary with the _id and text of the tweet.

    Parameters:
     - minutes (default 1): select how long you want the 
     function to run. Each minute will translate
     into 3 requests, each of it brings 500 tweets.

      - end (defaults to now-30s): select the end date 
      of the tweets to retrieve.

    Twitter API limits:
     - recent endpoint: 100 results per request
     - full archive endpoint: 500 results per request
     - other limitations:
        - 10 million tweets per month
        - 50 requests per 15 min
    """

    # parameters
    url = "https://api.twitter.com/2/tweets/search/all"
    results_per_request = 500 # The max for the search all endpoint
    start = '2022-02-01T00:00:00.000Z' # Retrieve data from February until now
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
              'start_time': start,
              'end_time': end,
              'max_results': results_per_request,
              'tweet.fields': 'created_at'}

    # convert minutes into number of requests
    i = minutes * 3

    # create cache
    #requests_cache.install_cache(cache_name='twitter_cache', backend='sqlite',
    #                            expire_after=900)

    # initialize list
    records = []

    # pagination
    for i in tqdm(range(i)):
        try:
            # make request
            response = requests.get(url, auth=bearer_oauth, params=params)
            if response.status_code != 200:
                raise Exception(response.status_code, response.text)
            #if response.from_cache:
            #    print("Response from cache!\n")
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


# create mongodb collection
collection = create_collection('covid-19_final')

# select number of minutes
parser = argparse.ArgumentParser(description='''Number of minutes to run the program and
                                                optionally a date of the tweets to fetch''')
parser.add_argument('integer', metavar='N', type=int, 
                    help='an integer for the minutes to run the program')
parser.add_argument('date', metavar='N', type=str, 
                    help='a string with the date of the tweets to search')
args = parser.parse_args()


if __name__ == "__main__":    
    # save the tweets 
    tweets = get_twitter_data(minutes=args.integer, end=args.date)

    # delete duplicates
    all_tweets = list(unique_everseen(tweets))

    # store results in mongodb
    docs = insert_records(all_tweets, collection)

    # print message
    do_logging(f'{args.integer} and {args.date}, {docs} docs inserted')
