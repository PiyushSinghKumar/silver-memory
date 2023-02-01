import pandas as pd
from sklearn import preprocessing

def hushHush():
    userdata = pd.read_csv("./Data/Final_Data.csv")
    userdata['Email'] = "abc@def.com"
    Data = userdata.copy()
    Data['Tags'] = Data['Tags'].str.upper()
    try:
        Choice = (input("Please input the skill you want to get recommendations: ")).upper()

        if len(Choice) > 1:
            Choice = Choice+">"
        else:
            Choice = "<"
            #print(Choice)

        Data=Data[Data['Tags'].str.contains(Choice)]

        Data['Rank'] = Data['Rank'].map({'newbie':0,'pupil':1,'specialist':2,'master':3,'candidate master':4,'expert':5,'international master':6,'grandmaster':7,'international grandmaster':8,'legendary grandmaster':9})
        Data['MaxRank'] = Data['MaxRank'].map({'newbie':0,'pupil':1,'specialist':2,'master':3,'candidate master':4,'expert':5,'international master':6,'grandmaster':7,'international grandmaster':8,'legendary grandmaster':9})

        df_scale = Data[['followers', 'following', 'commits', 'public_repos', 'Rating', 'MaxRating',  'FriendOfCount', 'Reputation', 'Views', 'UpVotes', 'DownVotes', 'NumAnswers', 'NumAccepted', 'AcceptedPercent', 'Time_active_in_days','RegistrationTimeInSeconds','Rank','MaxRank']]
        
        scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
        names = df_scale.columns
        fit = scaler.fit_transform(df_scale)
        scaled_df = pd.DataFrame(fit, columns=names)
        scaled_df['RegistrationTimeInSeconds'] = 1 - scaled_df['RegistrationTimeInSeconds']
    
        #Claculating median
        scaled_df['median']=scaled_df.median(axis=1)

        Remaining_Column = ['username', 'company','hirable','Location', 'Tags','created_at', 'updated_at','Email']

        Data = Data[Remaining_Column].join(scaled_df)
        recommender(Data)
    except:
        print("Sorry this skill is not available, please choose another skill")
        hushHush()
    
    return Email


def recommender(Data):
    try:
        Recommend = Data.nlargest(int(input("Enter number of users to be recommended: ")),'median')
        global Email
        Email = Recommend['Email']
        #Recommend[['username','Email']].to_csv("Recommended People.csv",index=None)
    except: 
        print("Please give a  proper Recommender input")
        recommender(Data)
    return Email

#hushHush()