# Part 5. Sentiment Analysis Prep

# initial imports
import pandas as pd
import os
import shutil
from sklearn.model_selection import train_test_split
# project module imports
import ref_data as rf
import edgar_downloader as ed
import edgar_cleaner as ec
import edgar_sentiment_wordcount as esw


def full_train_dataset(dataset_name: str,
                       ticker_list: list[str], 
                       dest_folder: str = r'C:\EDGAR',
                       min_date: str = '2013-02-20', 
                       max_date: str = '2023-02-20', 
                       user_email: str = 'gregsmith@kubrickgroup.com'):
    '''
    ***IMPORTANT*** The dest_folder, if specified, must in in a raw string format eg... r'C:\EDGAR'.
    Creates a .csv file containing sentiment word counts of 10-k Financial Reports combined with short-term share price movements.
    The file has a specified name (dataset_name) and is saved to a specified folder (dest_folder or defaulting to C:\EDGAR).
    You can specify the companies that you want to analyse using the ticker_list input. Input as a list of strings, 
    where the strings are upper case ticker symbols.
    Additionally, you can specify the date range for the reports and stock data, user_email to access the .... .
    '''
    
    if not os.path.exists(dest_folder):
        try:
            os.makedirs(dest_folder)
        except OSError:
            print ("Creation of the directory %s failed" % dest_folder)
        else:
            print ("Successfully created the directory %s " % dest_folder)
    else:
        print('Directory already exists')
    
    # Create 10k_filings_raw folder
    raw_10k_filings_path = rf'{dest_folder}\10k_filings_raw'
    clean_10k_filings_path = rf'{dest_folder}\10k_filings_clean'
    try:
        os.makedirs(raw_10k_filings_path)
    except OSError:
        print ("Creation of the directory %s failed" % raw_10k_filings_path)


    ed.full_download(ticker_list, raw_10k_filings_path, user_email, min_date = min_date, max_date = max_date)

    ec.write_clean_html_text_files(raw_10k_filings_path, clean_10k_filings_path)
    # Delete 10_filings_raw folder
    shutil.rmtree(raw_10k_filings_path)

    df_returns = rf.get_yahoo_data(min_date, max_date, ticker_list)
    df_returns.to_csv(rf'{dest_folder}\stock_returns.csv', index=False)
    
    esw.write_document_sentiments(clean_10k_filings_path, rf'{dest_folder}\sentiment_factors.csv')
    # Delete 10_filings_clean folder
    shutil.rmtree(clean_10k_filings_path)

    # Load Data
    stock_returns_df = pd.read_csv(rf'{dest_folder}\stock_returns.csv')                         # Load in stock return data
    sentiment_factors_df = pd.read_csv(rf'{dest_folder}\sentiment_factors.csv')                 # Load in sentiment word count data
    
    # Delete unnessary .csv files
    if os.path.exists(rf'{dest_folder}\stock_returns.csv'):
        os.remove(rf'{dest_folder}\stock_returns.csv')
    else:
        print("The file, stock_returns.csv, does not exist")

    if os.path.exists(rf'{dest_folder}\sentiment_factors.csv'):
        os.remove(rf'{dest_folder}\sentiment_factors.csv')
    else:
        print("The file, sentiment_factors.csv, does not exist")

    # Processing and Feature Engineering
    stock_returns_df = stock_returns_prep(stock_returns_df)
    sentiment_factors_df = sentiment_factors_prep(sentiment_factors_df)
    
    # Combine Datasets
    combined_df = pd.merge(sentiment_factors_df, stock_returns_df, on = ['Date', 'Symbol'], how = 'left')
    # Clean Combined Dataset
    combined_df.drop_duplicates(inplace = True)
    combined_df.dropna(inplace = True)
    
    # Save Combined Dataset to .csv file
    combined_df.to_csv(rf'{dest_folder}\{dataset_name}.csv', index = False)              
         

# Feature Engineering

def stock_returns_prep(df): 
    '''
    Function that takes a dataframe and outputs a 'clean' dataframe. 
    Ready for it to be combined with another relevant datafram 'sentiment_factors;
    Formatting column names and dropping unneeded columns.
    df: DataFrame for the function to act upon 
    '''
    new_df = df.drop(['High', 'Low', 'Close'], axis = 1)                       # Remove unnessary columns # sample_stock_returns_daily_df
    new_df.rename(columns={"date": "Date"}, inplace= True)                     # Change date column name for later merge

    return new_df

def sentiment_factors_prep(df):  
    '''
    Function to clean and feature engineer the 'sentiment factors' dataframe.
    Formatting column names, Dropping uneeded columns and normalisiing data and creature new features for later modelling.
    df: DataFrame for the function to act upon 
    '''

    new_df = df.drop(['ReportType'], axis = 1)                                # Remove unnessary columns
    new_df.rename(columns={"FilingDate": "Date"}, inplace= True)              # Change date column name for later merge
    new_df['word_sum'] = new_df.sum(axis = 1, numeric_only=True)              # Calculate total number of categorised words from the report

    # Normalise wordcounts as a % of sum of word counts or report word count? 
    new_df['perc_Negative'] = new_df.apply(lambda row: row['Negative'] / row['word_sum'], axis = 1)
    new_df['perc_Positive'] = new_df.apply(lambda row: row['Positive'] / row['word_sum'], axis = 1)
    new_df['perc_Uncertainty'] = new_df.apply(lambda row: row['Uncertainty'] / row['word_sum'], axis = 1)
    new_df['perc_Litigious'] = new_df.apply(lambda row: row['Litigious'] / row['word_sum'], axis = 1)
    new_df['perc_Constraining'] = new_df.apply(lambda row: row['Constraining'] / row['word_sum'], axis = 1)
    new_df['perc_Modal'] = new_df.apply(lambda row: row['Modal'] / row['word_sum'], axis = 1)
    #Sentiment Scores
    new_df['sentiment_score'] = new_df.apply(lambda row: round((row['Positive'] - row['Negative']) / (row['Positive'] + row['Negative']), 2), axis = 1)  
    # Using Positive and Negative Word Count – With Normalization for Calculating Sentiment Score
    new_df['sentiment1'] = new_df.apply(lambda row: round((row['Positive'] - row['Negative']) / row['word_sum'], 2), axis = 1)       # Calculate a Sentiment score using positive & negative word counts 
    # Using Positive and Negative Word Counts – With Semi Normalization to calculate Sentiment Score
    new_df['sentiment2'] = new_df.apply(lambda row: round(row['Positive'] / (row['Negative']+1), 2), axis = 1)

    return new_df

def get_test_train_csv(input_file, features, target, test_size=0.3, random_state=0):
    '''
    Takes and input file (.csv) and specified values for features, the target and optionally the test/train split ratio and random state.
    Returns 4 datasets ready for modelling, in the following order; X_train, y_train, X_test, y_test
    input_file: str, full file path in a raw string format r'...'
    features: list of strings of column names to be inputted into the model as features
    target: str of the target column name
    test_size: float, optional input of the test/train split ratio
    random_state: optional input to call specific random state generations
    '''
    dataset_df = pd.read_csv(input_file) 
    df_train, df_test = train_test_split(dataset_df, test_size, random_state) 

    X_train = df_train[features]                                # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_train = df_train[target]                                  # NB -- we use lower case 'y' because it is a vactor (math term for series)

    X_test = df_test[features]                                  # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_test = df_test[target]                                    # NB -- we use lower case 'y' because it is a vactor (math term for series)
    
    return X_train, y_train, X_test, y_test

def get_test_train_df(dataset_df, features, target, test_size=0.3, random_state=0):
    '''
    Takes and input DataFrame and specified values for features, the target and optionally the test/train split ratio and random state.
    Returns 4 datasets ready for modelling, in the following order; X_train, y_train, X_test, y_test
    input_file: str, full file path in a raw string format r'...'
    features: list of strings of column names to be inputted into the model as features
    target: str of the target column name
    test_size: float, optional input of the test/train split ratio
    random_state: optional input to call specific random state generations
    '''
    
    df_train, df_test = train_test_split(dataset_df, test_size, random_state) 

    X_train = df_train[features]                                # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_train = df_train[target]                                  # NB -- we use lower case 'y' because it is a vactor (math term for series)

    X_test = df_test[features]                                  # NB -- we use upper case 'X' because it is a matrix (math term for df)
    y_test = df_test[target]                                    # NB -- we use lower case 'y' because it is a vactor (math term for series)
    
    return X_train, y_train, X_test, y_test
