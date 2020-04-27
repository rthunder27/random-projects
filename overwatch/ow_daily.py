
"""
Script for capturing daily SR of squad.
"""

#Todo
#Make squad members a user input (config file?)
# Multiple platforms, not just the hardcoded xbl
#Make OPP, fold into larger OW library
import requests
from scrapy.selector import Selector
import pandas as pd
import time
from datetime import date
import os
import numpy as np
squad=['Rthunder27','BIGoleICEBERG','Seraph341','LaCroixDaddy','YAS RIHANNA','star4ker','ULove2SeeIt7915']
log_path='C:/Users/matth/Documents/Overwatch/daily_logs/'
html_path='C:/Users/matth/Documents/Overwatch/html_files/'


today=  date.today()
daily_log_name=f'{today.year}_{today.month}_{today.day}_daily_sr_log.csv'

#player_info={"gamertag":gamer_tag}


squad_df=pd.DataFrame(columns=['games_won','Tank SR','Damage SR','Support SR','scrape_time'],index=squad)
for gamer_tag in squad:
    base_url='https://playoverwatch.com/en-us/career/xbl/'+gamer_tag
    res=requests.get(
        base_url,
    )
    HTML =res.content
    for i in range(1,4):
        try:
            role=Selector(text=HTML).xpath(f'//*[@id="overview-section"]/div/div[2]/div/div/div[2]/div/div[3]/div[{i}]/div[2]/div[1]').extract()[0].split('data-ow-tooltip-text="')[1].split()[0]

            SR=int(Selector(text=HTML).xpath(f'//*[@id="overview-section"]/div/div[2]/div/div/div[2]/div/div[3]/div[{i}]/div[2]/div[2]').extract()[0].split('<')[1].split('>')[1])
        
            if role and SR:squad_df.loc[gamer_tag,f'{role} SR']=SR
        except:pass
    squad_df.loc[gamer_tag,'games_won']=int(Selector(text=HTML).xpath('//*[@id="overview-section"]/div/div[2]/div/div/p/span').extract()[0].split('>')[1].split()[0])
    squad_df.loc[gamer_tag,'scrape_time']=time.ctime()
    filename=f'{html_path}{today.year}_{today.month}_{today.day}_{gamer_tag}.html'
    with open(filename, mode='wb') as localfile: 
        localfile.write(HTML)
    print(f"{gamer_tag}'s info downloaded")
#squad_df['average SR']=squad_df[['Tank SR','Damage SR','Support SR']].mean(axis=1)    





#check if that log_name already exists in directory. If so, open and compare.
if daily_log_name in [i.name for i in os.scandir(log_path)]:
    #Compare not working?
    # old_log=pd.read_csv(log_path+daily_log_name,) 
    # if np.array_equal(old_log[['games_won','Tank SR','Damage SR','Support SR']].fillna(0).values,
            #   squad_df[['games_won','Tank SR','Damage SR','Support SR']].fillna(0).values):
        print(f'Daily log {daily_log_name} already exists')
else:
    squad_df.to_csv(log_path+daily_log_name)
    print(f'Daily Log {daily_log_name} Created')