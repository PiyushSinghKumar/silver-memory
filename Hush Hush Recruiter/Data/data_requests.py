import requests
import csv

# Codeforce active users data fetching from API
url = 'https://codeforces.com/api/user.ratedList?activeOnly=true'

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
response = requests.request("GET", url, headers=headers, data=[])
myJson = response.json()
myData = []
csvHeaderColumnNames = ['Handle', 'Contribution', 'Rank',
                        'Rating', 'MaxRank', 'MaxRating', 'RegistrationTimeInSeconds', 'FriendOfCount']

for x in myJson['result']:
    myColumns = [x['handle'],
                 x['contribution'], x['rank'], x['rating'], x['maxRank'], x['maxRating'], x['registrationTimeSeconds'],
                 x['friendOfCount']]
    myData.append(myColumns)

with open('./codeforce_data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    writer.writerow(csvHeaderColumnNames)
    writer.writerows(myData)

print('data fetched and added into csv file')
