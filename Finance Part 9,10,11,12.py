import numpy as np
import pandas as pd
import pickle
from collections import Counter
from sklearn import svm,neighbors
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier,RandomForestClassifier

def process_data_for_labels(ticker):
    hm_days=7
    df=pd.read_csv("sp500_joined_closes.csv",index_col=0)
    tickers=df.columns.values.tolist()
    df.fillna(0,inplace=True)
    for i in range(1,hm_days+1):
        df["{}_{}d".format(ticker,i)]=((df[ticker].shift(-i)-df[ticker])/df[ticker])
    return tickers,df

def buy_sell_hold(*args):
    print(args)
    cols=[c for c in args]
#    print(cols)
    requirement=0.02
    for col in cols:
        if col>requirement:
            return 1
        if col<-requirement:
            return -1
    return 0

def extract_featuredatasets(ticker):
    tickers,df=process_data_for_labels(ticker)
    
    
    df["{}_target".format(ticker)]=list(map(buy_sell_hold,
       df["{}_1d".format(ticker)],
       df["{}_2d".format(ticker)],
       df["{}_3d".format(ticker)],
       df["{}_4d".format(ticker)],
       df["{}_5d".format(ticker)],
       df["{}_6d".format(ticker)],
       df["{}_7d".format(ticker)]))
    
    vals=df["{}_target".format(ticker)].values.tolist()
    str_vals=[str(i) for i in vals]
    print("Data Spread:",Counter(str_vals))
    df.fillna(0,inplace=True)
    df=df.replace([np.inf,-np.inf],np.nan)
    df.dropna(inplace=True)


    df_vals=df[[ticker for ticker in tickers]].pct_change()
    df_vals=df.replace([np.inf,-np.inf],0)
    df_vals.fillna(0,inplace=True)
    print(df_vals.head())
    X=df_vals.values
    y= df["{}_target".format(ticker)].values
    print(df["{}_target".format(ticker)])
    return X,y,df

def do_ml(ticker):
    X,y,df=extract_featuredatasets(ticker)
    
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.25)
    
    
    #clf=neighbors.KNeighborsClassifier()
    clf=VotingClassifier([('lsvc',svm.LinearSVC()),
                          ('knn',neighbors.KNeighborsClassifier()),
                          ('rfor',RandomForestClassifier())])
    clf.fit(X_train,y_train)
    confidence=clf.score(X_test,y_test)
    predictions=clf.predict(X_test)
    print('Predicted spread',Counter(predictions))
    print("Confidence",confidence)
    return confidence
do_ml("BAC")

    