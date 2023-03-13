import pandas as pd
from sklearn.model_selection import train_test_split

def get_test_train_split(file_path,
                            target,
                            unchanged_cols = False,
                            normalised_cols = False,
                            z_normalised_cols = False,
                            hot_enc_list = False,
                            cat_type = None,
                            categories = False,
                            balance_data = True,
                            random_seed = 0,
                            test_size = 0.3):
    '''
    takes the filepath of a .csv cleaned dataset and returns the training and testing data as pandas dataframes, split out by X and Y
    file_path: str - the filepath of the processed .csv file
    target: str - the name of the target column
    unchanged_cols: list[str]
    normalised_cols: list[str] - list of column names that should be normalised
    z_normalised_cols: list[str] - list of column names that should be z-normalised
    hot_enc_list: list[str] - list of column names that should be one hot encoded
    categories: dict - dependent on cat_type should be in {category:value...} form (abs) or {category:[relative function, value]...} form (rel)
    cat_type: str - must be 'abs' or 'rel'
    balance_data: bool - indicates whether data should be balanced
    random_seed: int
    test_size: float - must be between 0 and 1
    '''
    
    df = data_prep(file_path, target, unchanged_cols, normalised_cols, z_normalised_cols, hot_enc_list, cat_type, categories)

    features = list(df.columns)
    features.pop(list(df.columns).index(target))

    cat_list = []
    for item in categories:
        cat_list.append(item)

    if balance_data:
        df = balance_df(df, target, cat_list, random_seed)

    return train_split(df, features, target, test_size, random_seed)



def data_prep(file_path,
              target,
              unchanged_cols = False,
              normalised_cols = False,
              z_normalised_cols = False,
              hot_enc_list = False,
              cat_type = None, #can be 'rel' (relative categories) or 'abs' (absolute values)
              categories = False #dictionary with either {'category':value...} for abs or {'category':[function,value]...} for rel
              ):
    '''
    takes the filepath of a .csv cleaned dataset and returns a pandas dataframe with the data normalised, categorised and one hot encoded.
    file_path: str - the filepath of the processed .csv file
    target: str - the name of the target column
    unchanged_cols: list[str]
    normalised_cols: list[str] - list of column names that should be normalised
    z_normalised_cols: list[str] - list of column names that should be z-normalised
    hot_enc_list: list[str] - list of column names that should be one hot encoded
    categories: dict - dependent on cat_type should be in {category:value...} form (abs) or {category:[relative function, value]...} form (rel)
    cat_type: str - must be 'abs' or 'rel'
    '''
    
    df = pd.read_csv(rf'{file_path}')

    all_cols = ['Symbol', 'Date', 'Negative', 'Positive', 'Uncertainty', 'Litigious', 'Constraining', 'Modal'
            , 'word_sum', 'perc_Negative', 'perc_Positive', 'perc_Uncertainty', 'perc_Litigious', 'perc_Constraining'
            , 'perc_Modal', 'sentiment_score', 'sentiment1', 'sentiment2', 'volume'
            , '1daily_return', '2daily_return', '3daily_return', '5daily_return', '10daily_return']

    all_cols.pop(all_cols.index(target))

    if unchanged_cols:
        for col in unchanged_cols:
            all_cols.pop(all_cols.index(col))

    if normalised_cols:
        def norm(s):
            new_s = (s - s.min())/(s.max() - s.min())
            return new_s
        
        for col in normalised_cols:
            df[col] = norm(df[col])
            all_cols.pop(all_cols.index(col))

    if z_normalised_cols:    
        def z_norm(s):
            new_s = (s - s.mean()/s.std())
            return new_s
        
        for col in z_normalised_cols:
            df[col] = z_norm(df[col])
            all_cols.pop(all_cols.index(col))

    if hot_enc_list:
        for col in hot_enc_list:
            df = pd.get_dummies(df, columns = [col])
            all_cols.pop(all_cols.index(col))

    if categories:
        if cat_type == None:
            raise Exception('no categorisation type specified')
        
        if cat_type == 'rel':
            def cat_func(s):
                for cat in categories:
                    if categories[cat][0]=='less':
                        if s < categories[cat][1]:
                            return cat
                    elif categories[cat][0]=='lessequal':
                        if s <= categories[cat][1]:
                            return cat
                    elif categories[cat][0]=='greater':
                        if s > categories[cat][1]:
                            return cat
                    elif categories[cat][0]=='greaterequal':
                        if s >= categories[cat][1]:
                            return cat
                    elif categories[cat][0]=='equal':
                        if s == categories[cat][1]:
                            return cat
                    elif categories[cat][0]=='other':
                        return cat
                    else:
                        return None

        elif cat_type == 'abs':
            def cat_func(s):
                for cat in categories:
                    if s == cat:
                        return categories[s]
                    
        df[target] = df[target].apply(cat_func)

    df= df.drop(columns = all_cols)

    return df

def balance_df(df, 
               col_name, #column name to balance for
               col_vals, #list of potential values in target column
               random_seed = 0
               ):
    '''
    takes a pandas dataframe and returns the balanced dataframe.
    df: pd.DataFrame()
    col_name: str - the column to balance for
    col_vals: list of potential values in target column
    random_seed: int
    '''

    dfs = []
    for val in col_vals:
        mask = df[col_name]==val
        dfs.append(df[mask])
    
    n_dfs = []
    for frame in dfs:
        n_dfs.append(frame.shape[0])
    
    min_rows = min(n_dfs)
    index = n_dfs.index(min_rows)
    
    for i in range(len(n_dfs)):
        if i == index:
            continue
        dfs[i] = dfs[i].sample(min_rows, random_state=random_seed)

    out_df = pd.DataFrame()
    for frame in dfs:
        out_df = pd.concat([out_df,frame])
    
    return out_df

def train_split(df, features, target, test_size=0.3, random_state=0):
    '''
    takes a pandas dataframe and returns the the training and testing data as pandas dataframes, split out by X and Y.
    df: pd.DataFrame()
    features: list[str] - list of all columns being included in the X dataframes
    target: str - column in the y dataframes
    test_size: float =0.3, 
    random_state: int =0
    '''

    df_train, df_test = train_test_split(df, test_size = test_size,  random_state = random_state)

    X_train = df_train[features]
    y_train = df_train[target]

    X_test = df_test[features]
    y_test = df_test[target]

    return X_train, y_train, X_test, y_test