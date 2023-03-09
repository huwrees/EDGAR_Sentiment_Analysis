#LINEAR REGRESSION MODEL

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score

def create_linear_regression(X_train, y_train, X_test, y_test):
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test,y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f'MSE (test): {mse:.4f}')
    print(f'RMSE (test): {mse**0.5:.4f}')
    print(f'MAE (test): {mae:.4f}')
    print(f'R-squared is: {r2}')
    
    plt.figure(figsize= (10,10))
    plt.scatter(y_test, y_pred, color = '#66CD00')
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    plt.title('Actual vs Predicted')

    x = np.linspace(0,3500, 100)
    y = x
    plt.plot(x,y, color = '#808A87', linestyle = '--')
    plt.show()