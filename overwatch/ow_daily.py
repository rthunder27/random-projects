
"""
Script for capturing daily SR of squad.
HTML for each player is downloaded.
SR is extracted, saved in a csv
Then all the stats are extracted, and put into a flat data structure, and appended to the running csv. 

The actual parsing of the html using xpath is very, very slow. Must be a way to fix that.

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
from lxml import etree

squad=['Rthunder27','BIGoleICEBERG','Seraph341','LaCroixDaddy','YAS RIHANNA','star4ker','ULove2SeeIt7915']
log_path='C:/Users/matth/Documents/Overwatch/daily_logs/'
html_path='C:/Users/matth/Documents/Overwatch/html_files/'


today=  date.today()
daily_log_name=f'{today.year}_{today.month}_{today.day}_daily_sr_log.csv'

#player_info={"gamertag":gamer_tag}


squad_df=pd.DataFrame(columns=['games_won','Tank SR','Damage SR','Support SR','scrape_time'],index=squad)
for gamer_tag in squad:
    if gamer_tag=='YAS RIHANNA':gamer_tag_x='LaCroix%20Bebe' #Because this player changed their gamer tag, easier to alias the new one to the old name
    else: gamer_tag_x=gamer_tag
    base_url='https://playoverwatch.com/en-us/career/xbl/'+gamer_tag_x
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
hero_name_dict={
    
    'Biotic Grenade Kills':'Ana',
    'Coach Gun Kills - Avg per 10 Min':'Ashe', #using the avg avoids the issue with kill/kills
    'Dynamite Kills - Avg per 10 Min':'Ashe',
    'Bob Kills - Avg per 10 Min': 'Ashe',
    'Immortality Field Deaths Prevented':'Baptiste',
    'Recon Kills':'Bastion',
    'Sentry Kills - Avg per 10 Min':'Bastion',
    'Armor Provided':'Brigette',
    'Mech Deaths':'D.Va',
    'Meteor Strike Kills - Avg per 10 Min':'Doomfist',
    #Echo
    'Sticky Bombs Kills - Avg per 10 Min':'Echo',
    'Focusing Beam Kills - Avg per 10 Min':'Echo',
    'Damage Reflected':'Genji',
    'Storm Arrow Kills':'Hanzo',
    'RIP-Tire Kills':'Junkrat',
    'Concussion Mine Kills - Avg per 10 Min':'Junkrat',
    'Sound Barriers Provided':'Lucio',
    'Deadeye Kill':'McGree',#Find a different one?
    'Fan the Hammer Kills - Avg per 10 Min':'McGree',
    'Enemies Frozen':'Mei',
    'Players Resurrected':'Mercy',
    'Coalescence Healing':'Moira',
    'Supercharger Assists':'Orisa',
    'Barrage Kills':'Pharah',
    'Rocket Direct Hits - Avg per 10 Min':'Pharah',
    'Death Blossom Kills':'Reaper',
    'Rocket Hammer Melee Accuracy':'Reinhart',
    'Enemies Hooked':'Roadhog',
    'Accretion Kills':'Sigma',
    'Helix Rocket Kills':'Soldier: 76',
    'Enemies Hacked':'Sombra',
    'Players Teleported':'Symmetra',
    'Overload Kills':'Torbjorn',
    'Pulse Bomb Kills':'Tracer',
    'Venom Mine Kills - Avg per 10 Min':'Widowmaker',
    'Tesla Cannon Accuracy':'Winston',
    'Grappling Claw Kills':'Wrecking Ball',
    'Average Energy':'Zarya',
    'Transcendence Healing':'Zenyatta'
    }
def convert(value):
    try:c_val=np.float(value)
    except:
        if value[-1]=='%':
            c_val=float(value[:-1])
        else:
            c_val=0
            for i,val in enumerate(reversed(value.split(':'))):
                c_val+=60**i*np.int(val)
    return c_val
#iterate through tables
def multiindex_pivot(df, columns=None, values=None):
    #https://github.com/pandas-dev/pandas/issues/23955
    names = list(df.index.names)
    df = df.reset_index()
    list_index = df[names].values
    tuples_index = [tuple(i) for i in list_index] # hashable
    df = df.assign(tuples_index=tuples_index)
    df = df.pivot(index="tuples_index", columns=columns, values=values)
    tuples_index = df.index  # reduced
    index = pd.MultiIndex.from_tuples(tuples_index, names=names)
    df.index = index
    return df
def get_structured_data(html_file):
    """
    Pass in html file, opened file, or file location? 
    Return all stats by hero, plus remainder (stats for whom a hero could not be matched)
    To do: Improve hero matching, use the fact that they're alphabetical, so one hero gaps could be uniquely matched
    Is xpath slow? 
    

    """
    with open(html_file, encoding="utf8") as f:
        data=f.read()
    dom = etree.HTML(data)    
    

    
    t0=time.time()
    data_dict={}
    for hero in range(2,len(hero_name_dict)+3):#Could tie this loop size to length of hero_name_dict
            data_dict[hero]={}
            for table in range(1,12):
                try:
                    t_name=dom.xpath(f'//*[@id="competitive"]/section[2]/div/div[{hero}]/div[{table}]/div/table/thead/tr/th/h5/text()')[0]
                    data_dict[hero][t_name]={} #Consider flattening this a bit, get rid of the table name from the data structure
                    #row=1
                    for row in range(1,30):
                        try:
                            label=dom.xpath(f'//*[@id="competitive"]/section[2]/div/div[{hero}]/div[{table}]/div/table/tbody/tr[{row}]/td[1]/text()')[0]

                            val=dom.xpath(f'//*[@id="competitive"]/section[2]/div/div[{hero}]/div[{table}]/div/table/tbody/tr[{row}]/td[2]/text()')[0]
                            data_dict[hero][t_name][label]=val
                            #row+=1
                        except:
                            break
                    #table+=1
                except:
                    break
            if len(data_dict[hero])==0:data_dict.pop(hero)
    print(time.time()-t0)
    renamed_data_dict={}
    renamed_data_dict['All Heroes']=data_dict.pop(2)
    for i in range(3,36):
        for k in hero_name_dict:
            try: 
                if k in data_dict[i]['Hero Specific'].keys():
                    renamed_data_dict[hero_name_dict[k]]=data_dict.pop(i)
                    break
            except:break
    return renamed_data_dict,data_dict
sr_cols=['Tank SR','Damage SR','Support SR','SR std','average SR']
full_dict={}
def one_day_update(date):
    squad_hero_stats={}

    daily_log_name=f'{date}_daily_sr_log.csv'
    log_df=pd.read_csv(log_path+daily_log_name,index_col='Unnamed: 0')

        #drop dupes?
    log_df['SR std']=log_df[['Tank SR','Damage SR','Support SR']].std(axis=1) 
    log_df['average SR']=log_df[['Tank SR','Damage SR','Support SR']].mean(axis=1) 
    for gamer_tag in squad:
        html_file=html_path+f'{date}_{gamer_tag}.html'
        squad_hero_stats[gamer_tag],remainder=get_structured_data(html_file)
        print(f'{date} {gamer_tag} parsed')
        squad_hero_stats[gamer_tag]['All Heroes']['SR']={}
        for col in sr_cols:
            squad_hero_stats[gamer_tag]['All Heroes']['SR'][col]=log_df.loc[gamer_tag,col]     
                


    full_dict[date]=squad_hero_stats
    #dict_level_labels=['date','player','hero','table','stat','value']
    data=[]
    second_dict={}
    #second_df=pd.DataFrame()
    #over-writing "date" a second time
    second_dict[date]={}
    for player in full_dict[date].keys():
        second_dict[date][player]={}
        for hero in full_dict[date][player].keys():
            second_dict[date][player][hero]={}
            for table in full_dict[date][player][hero].keys():
                second_dict[date][player][hero][table]={}
                for stat in full_dict[date][player][hero][table].keys():
                    data.append([date,player,hero,table,stat,convert(full_dict[date][player][hero][table][stat])])
                    second_dict[date][player][hero][table][stat]=convert(full_dict[date][player][hero][table][stat])
                    #second_df[(date,player,hero,table),stat]=convert(full_dict[date][player][hero][table][stat])
    ow_df=pd.DataFrame(data=data,columns=['date','player','hero','table','stat','value'])    

    df2=ow_df.set_index(['date','player','hero'])

    pivoted_ow_df= multiindex_pivot(df2, columns='stat', values='value')
    return pivoted_ow_df


pivoted_ow_df=pd.read_csv(log_path+'full_comp_stats_running.csv',index_col=('date','player','hero'))

date_set={x[0] for x in pivoted_ow_df.index}
date=f'{today.year}_{today.month}_{today.day}'
new=one_day_update(date)
if date in date_set:print(f"{date} already in record file")
else:pivoted_ow_df=pivoted_ow_df.append(new)
#dropping one off columns. Mostly from how the html page names things differently for ones (kill vs kills)
pivoted_ow_df=pivoted_ow_df.drop(axis=1,columns=pivoted_ow_df.columns[[ x for x in pivoted_ow_df.max()==1]].values)
pivoted_ow_df.to_csv(log_path+'full_comp_stats_running.csv')