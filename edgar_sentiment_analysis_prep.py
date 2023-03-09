# Part 5. Sentiment Analysis Prep

# initial imports
import pandas as pd
import numpy as np
import datetime as dt
import sklearn
from sklearn.model_selection import train_test_split
# project specific imports
import ref_data as rf
import edgar_downloader as ed
import edgar_cleaner as ec
import edgar_sentiment_wordcount as esw


# suggestions/change log
# add a argument to full_train_dataset() specifying file paths
# suggestion: create a new folder at the start and delete it at the end

def full_train_dataset(): # input_min_date = None, input_max_date = None
    '''
    Creates a csv to specified file path
    '''

    tickers_sp100 = rf.get_sp100()
    #ed.download_files_10k(‘AAPL’, ‘C:/10k_filings_raw’)
    ed.full_download(tickers_sp100, 'C:/10k_filings_raw', 'gregsmith@kubrickgroup.com', report = '10-K') #min_date = input_min_date, max_date = input_max_date,

    ec.write_clean_html_text_files('C:/10k_filings_raw', 'C:/10k_filings_clean')
    
    #df_returns = rf.get_yahoo_data(input_min_date, input_max_date, tickers_sp100, 'daily')
    df_returns = rf.get_yahoo_data('2000-01-01', '2020-08-01', tickers_sp100, 'daily') # Need to decide dates as I have to pass a date here
    df_returns.to_csv('C:/stock_returns_daily.csv', index=False)
    sentiment_dict = rf.get_sentiment_word_dict()

    esw.write_document_sentiments('C:/10k_filings_clean', 'C:/sentiment_factors.csv')

    # Load Data
    stock_returns_daily_df = pd.read_csv('C:/stock_returns_daily.csv')                         # Load in stock return data
    sentiment_factors_df = pd.read_csv('C:/sentiment_factors.csv')                             # Load in sentiment word count data
    #stock_returns_daily_df = pd.read_csv('C:/EDGAR/example_shares_output2.csv')   
    #sentiment_factors_df = pd.read_csv('C:/EDGAR/example_sentiment_analysis.csv')  
    
    # Processing and Feature Engineering
    full_stock_returns_daily_df = stock_returns_prep(stock_returns_daily_df)
    full_sentiment_factors_df = sentiment_factors_prep(sentiment_factors_df)
    
    # Combine Datasets
    full_combined_df = pd.merge(full_stock_returns_daily_df, full_sentiment_factors_df, on = ['Date', 'ticker'], how = 'left')

    full_combined_df.to_csv('C:/EDGAR/full_dataset.csv', index = False)              # Will need to decide a better place for this

def get_train_dataset(input_stock_data, input_sentiment_data, output_file):
    
    return combined_df.to_csv(output_file, index = False)              # Will need to decide a better place for this

# Feature Engineering

def stock_returns_prep(df): 
    
    new_df = df.drop(['high', 'low', 'price'], axis = 1)                       # Remove unnessary columns # sample_stock_returns_daily_df
    new_df.rename(columns={"date": "Date"}, inplace= True)                              # Change date column name for later merge

    return new_df

def sentiment_factors_prep(df):  
    new_df = df.drop(['ReportType'], axis = 1)                                # Remove unnessary columns
    new_df.rename(columns={"FilingDate": "Date"}, inplace= True)                        # Change date column name for later merge
    new_df['word_sum'] = new_df.sum(axis = 1)                                           # Calculate total number of categorised words from the report

    # Normalise wordcounts as a % of sum of word counts or report word count? 
    new_df['perc_Negative'] = new_df.apply(lambda row: row['Negative'] / row['word_sum'], axis = 1)
    new_df['perc_Positive'] = new_df.apply(lambda row: row['Positive'] / row['word_sum'], axis = 1)
    new_df['perc_Uncertainty'] = new_df.apply(lambda row: row['Uncertainty'] / row['word_sum'], axis = 1)
    new_df['perc_Litigious'] = new_df.apply(lambda row: row['Litigious'] / row['word_sum'], axis = 1)
    new_df['perc_Constraining'] = new_df.apply(lambda row: row['Constraining'] / row['word_sum'], axis = 1)
    new_df['perc_Superfluous'] = new_df.apply(lambda row: row['Superfluous'] / row['word_sum'], axis = 1)
    new_df['perc_Interesting'] = new_df.apply(lambda row: row['Interesting'] / row['word_sum'], axis = 1)
    new_df['perc_Modal'] = new_df.apply(lambda row: row['Modal'] / row['word_sum'], axis = 1)
    #Sentiment Scores
    new_df['sentiment_score'] = new_df.apply(lambda row: round((row['Positive'] - row['Negative']) / (row['Positive'] + row['Negative']), 2), axis = 1)  
    # Using Positive and Negative Word Count – With Normalization for Calculating Sentiment Score
    new_df['sentiment1'] = new_df.apply(lambda row: round((row['Positive'] - row['Negative']) / row['word_sum'], 2), axis = 1)       # Calculate a Sentiment score using positive & negative word counts 
    # Using Positive and Negative Word Counts – With Semi Normalization to calculate Sentiment Score
    new_df['sentiment2'] = new_df.apply(lambda row: round(row['Positive'] / (row['Negative']+1), 2), axis = 1)
    # round(df['pos_count'] / (df['neg_count']+1), 2)

    # Drop unnessary columns, raw word category counts
    #new_df.drop(['Negative', 'Positive', 'Uncertainty', 'Litigious', 'Constraining', 'Superfluous', 'Interesting', 'Modal'], axis = 1, inplace = True)

    return new_df

def get_test_train_csv(input_file, features, target):

    dataset_df = pd.read_csv(input_file) 
    df_train, df_test = train_test_split(dataset_df, test_size=0.3, random_state=0) 

    X_train = df_train[features]                                # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_train = df_train[target]                                  # NB -- we use lower case 'y' because it is a vactor (math term for series)

    X_test = df_test[features]                                  # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_test = df_test[target]                                    # NB -- we use lower case 'y' because it is a vactor (math term for series)
    
    return X_train, y_train, X_test, y_test

def get_test_train_df(dataset_df, features, target):
    
    df_train, df_test = train_test_split(dataset_df, test_size=0.3, random_state=0) 

    X_train = df_train[features]                                # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_train = df_train[target]                                  # NB -- we use lower case 'y' because it is a vactor (math term for series)

    X_test = df_test[features]                                  # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_test = df_test[target]                                    # NB -- we use lower case 'y' because it is a vactor (math term for series)
    
    return X_train, y_train, X_test, y_test


# #########################################################################################################
# # Options for features and targets for models      
# all_features = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 'Constraining', 'Superfluous', 'Interesting', 'Modal',
#                 'perc_Negative', 'perc_Positive', 'perc_Uncertainty', 'perc_Litigious', 'perc_Constraining', 'perc_Superfluous', 'perc_Interesting', 'perc_Modal',
#                 'sentiment_score', 'sentiment1','sentiment2']
# all_sentiment_features = ['Negative', 'Positive', 'Uncertainty', 'Litigious', 'Constraining', 'Superfluous', 'Interesting', 'Modal']
# neg_pos_features = ['Negative', 'Positive']
# neg_feature = ['Negative']
# #########################################################################################################

# full_train_dataset()

# full_dataset_df = pd.read_csv('C:/EDGAR/full_dataset.csv') 

# neg_pos_features = ['Negative', 'Positive']
# one_day_target = ['1daily return']
# get_test_train(neg_pos_features, features, one_day_target)
