# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 23:10:07 2019

@author: MMOHTASHIM
"""
import numpy as np
import bs4 as bs
import datetime as dt
import os
import pandas as pd
import pickle
import requests
import pandas_datareader.data as web
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.pyplot import style
import seaborn as sns
style.use('ggplot')
def save_sp500_tickers():
    resp=requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup=bs.BeautifulSoup(resp.text,'lxml')
    table=soup.find('table',{'class':'wikitable sortable'})
    tickers=[]
    for row in table.findAll('tr')[1:]:
        ticker=row.findAll('td')[1].text
        tickers.append(ticker)
    with open("sp500ticker.pickle","wb") as f:
        pickle.dump(tickers,f)
    return tickers

def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers=save_sp500_tickers()
    else:
         with open("sp500ticker.pickle","rb") as f:
             tickers=pickle.load(f)
             print(len(tickers))
    
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')
    start=dt.datetime(2000,1,1)
    end=dt.datetime(2017,12,31)
    
    for ticker in tqdm(tickers[85:]):
        try:
            if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
                df=web.DataReader(ticker,"yahoo",start,end)
                df.to_csv('stock_dfs/{}.csv'.format(ticker))
            else:
                print("Already have {}".format(ticker))
        except KeyError:
            print("Something is Missing")
def compile_data():
    with open("sp500ticker.pickle","rb") as f:
        tickers=pickle.load(f)
    main_df=pd.DataFrame()
    
    for count,ticker in enumerate(tickers):
        try:
            df=pd.read_csv('stock_dfs/{}.csv'.format(ticker))
            df.set_index("Date",inplace=True)
            
            df.rename(columns={"Adj Close":ticker},inplace=True)
            df.drop(["Open","High","Low","Close","Volume"],1,inplace=True)
            
            if main_df.empty:
                main_df=df
            else:
                main_df=main_df.join(df,how="outer") 
            if count%10==0:
                print(count)
        except FileNotFoundError:
            print("No file Found.....Moving Ahead")
    print(main_df.head())
    main_df.to_csv("sp500_joined_closes.csv")
def visualize_data():
    df=pd.read_csv("sp500_joined_closes.csv")
#    df["APPL"].plot()
#    plt.show()
    df_corr=df.corr()
    
    data=df_corr.values

    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    
    heatmap=ax.pcolor(data,cmap=plt.cm.RdYlGn)
    fig.colorbar(heatmap)
    ax.set_xticks(np.arange(data.shape[0])+0.5,minor=False)
    ax.set_yticks(np.arange(data.shape[1])+0.5,minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    
    
    column_labels=df_corr.columns
    row_labels=df_corr.index
    ax.set_xticklabels(column_labels)
    ax.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap.set_clim(-1,1)
    plt.tight_layout()
    plt.show()
    plt.pause(5)
    plt.close()
    sns.heatmap(data,cmap="RdYlGn",xticklabels=df_corr.index,yticklabels=df_corr.index)
visualize_data()