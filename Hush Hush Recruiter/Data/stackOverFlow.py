import requests, time
import pandas as pd

def extractStackOverFlowData():
    Record_list = []
    for i in range(1,27):
        url = f"https://api.stackexchange.com/2.3/users?page={i}&pagesize=100&order=desc&sort=reputation&site=stackoverflow"
        response = requests.get(url,params={'key':'m5eBEgjL*RkxfjAgi5KbWQ(('})
        print(response.status_code)
        Record_list = Record_list+response.json()["items"]
        time.sleep(2)
    
    df = pd.DataFrame(data=Record_list)
    df.to_excel(f'dict{i}.xlsx')


if __name__ == '__main__':
    extractStackOverFlowData()