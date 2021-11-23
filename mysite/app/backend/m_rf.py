
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import metrics
from sklearn.ensemble import RandomForestRegressor

import m__

if __name__ == '__main__':
    df = m__.get_data()
    X_train, X_test, y_train, y_test = m__.get_feature_x_target_y()

    """RandomForest Repressor"""
    # Fit the model
    model = RandomForestRegressor(n_estimators=1000, max_depth=2, bootstrap=False, min_samples_leaf=1) \
        .fit(X_train, y_train.ravel())

    # Make some predictions
    y_pred = model.predict(X_test)

    # Evaluating the model
    print('Root Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred, squared=False))
    print('R-squared :', metrics.r2_score(y_test, y_pred))
    print('Accuracy:', model.score(X_test, y_test))

    # Recover the original prices instead of the scaled version
    predicted_prices = y_pred.reshape(-1, 1)
    real_prices = y_test.reshape(-1, 1)

    # Create a DataFrame of Real and Predicted values
    stocks = pd.DataFrame({
        "Real": real_prices.ravel(),
        "Predicted": predicted_prices.ravel()
    }, index=df.index[-len(real_prices):])
    # print(stocks)

    # Plot the real vs predicted values as a line chart
    stocks.plot()
    plt.show()
