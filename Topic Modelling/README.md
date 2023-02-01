# Introduction 
This study compares social media with traditional media sources using topic modelling and sentiment analysis of data relating to the Covid-19 pandemic in a post-pandemic period, from the 1st of April 2022 to the 24th of September 2022. The idea behind the study was to better understand the effects Covid-19 had on social media and traditional media and if those effects where still present in a post-pandemic period. The pandemic brought great changes to people's daily lives and that was reflected on how they consumed news. It was therefore important to measure the discrepancy between both sources by analyzing what was being discussed and the respective sentiment towards a particular topic in each source.

# Getting Started
1.	Installation process

Clone the repository:
```
git clone repo
```
Run install.sh
```
sh install.sh
```

2.	Software dependencies

Need python version >=3.7, <3.11

3.	API references

API's used:
- Twitter API &rarr; endpoint used: https://api.twitter.com/2/tweets/search/all
- The New York Times API &rarr; endpoint used: https://api.nytimes.com/svc/search/v2/articlesearch
- The Guardian API &rarr; enpoint used: https://content.guardianapis.com/search

# Build and test
With our code you will be able to run everything and download the data according to our parameters, but you will have to create a MongoDB database and change the parameters accordingly. The same goes for the API credentials.

If you want to avoid this and are interested in having access to our database please contact a member of our group.

# Folder structure
The initial folder is just installation and requirements files. In **module_dataalliance** you will find the code for the project. This file is divided into 4 sections, 3 folders and python files. 

- The python scripts are regarding the topic models performed on both data sources, the naming convention being *"DataSource_Model.py"*. There you can also find a *results.py* file with our findings and visuals created.

- The **data_storage** folder contains code relating to retrieving and storing data from the respective API's and also cleaning the data. This folders serves as the entry point to fetch the data, with the *"retrive_data_functions.py"* being called through all the scripts in the main folder to get the data as a dataframe. Inside this folder there are 2 other folders:
    - **data** where the final data sources were saved as a parquet file. Also a csv of webscrapted data from The Harvard School of Public Health can be found in this folder.
    - **utils** contains functions we used to store data into Mongodb.

- The **images** folder was used to store images such as wordclouds or histograms. It also contains some txt files were we stored the conclusions of the EDA's performed.

- The **notebooks** folder is where we stored our jupyter notebooks, the original notebooks that were then converted into the code saved as python scripts. These notebooks do not play a role in the functioning of the module and can be ignored, they are just there as a reminder of the work done and how we had to adapt different code from different people and come together in a nice module. The notebooks also include code that was already ranned, as jupyter notebooks save the outputs, so they can be a good entry point to see some of our functions in action and what was done. Still, it should be said that not all of our notebooks were included in this folder and that these do not represent the final version of our results or scripts. Also, there was no naming convention here, everything was left to its original status.