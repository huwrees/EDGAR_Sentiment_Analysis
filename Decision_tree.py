#DECISION TREE

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

def create_decision_tree(X_train, y_train, X_test, y_test):
    
    dt = DecisionTreeRegressor()
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)

    tree.plot_tree(dt)
    plt.show()
    
    print('Accuracy of decision tree:', accuracy_score(y_test, y_pred))

def hyper_tuning(X_train, y_train, X_test, y_test, depth_list, sample_list):
    data = []
    for depth in depth_list:
        for sample in sample_list:
            inner_dict = {}
            inner_dict['depth'] = depth
            dt = DecisionTreeRegressor(max_depth = depth, min_samples_leaf = sample, random_state = 1)
            dt.fit(X_train, y_train)
            y_pred = dt.predict(X_test)
            
            #different measures to determine variance in model 
            mse = mean_squared_error(y_test, y_pred)
            rmse = mse**0.5
            mae = mean_absolute_error(y_test,y_pred)
            r2 = r2_score(y_test, y_pred)
            
            #adding measures to dictionary
            inner_dict['sample'] = sample
            inner_dict['mae'] = mae
            inner_dict['mse'] = mse
            inner_dict['rmse'] = rmse
            inner_dict['r2'] = r2
            data.append(inner_dict)
            
    #creating a dataframe with the information        
    summary_df = pd.DataFrame(data)
    summary_df.sort_values('rmse', inplace = True)
    
    return summary_df

depth_list = [input_list]
sample_list = [input_list]

hyper_tuning(X_train, y_train, X_test, y_test, depth_list, sample_list).head()

