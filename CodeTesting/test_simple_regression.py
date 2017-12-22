import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor as gauss
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import mean_squared_error, explained_variance_score, mean_squared_log_error, r2_score, \
    label_ranking_loss, log_loss, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

l_r = LogisticRegression()
clf = RandomForestClassifier(n_estimators=10)

data = pd.read_csv('flood_data.csv', delimiter=';', na_values='     ')

numeric_params = ['WindSpeed', 'Temp', 'Sunshine', 'Precipitation', 'SeaLevelPressure', 'Humidity',
                  'Evapotranspiration', 'WaterLevel']

data = data.dropna()

X = data[numeric_params]
y = data['Flood']
skf = StratifiedKFold(n_splits=10)

model = l_r # select model you desire here

for train, test in skf.split(X, y): # still casting as a regression problem to learn probabilities. it makes more sense as a classification problem though
    model = model.fit(np.float32(X.iloc[train].values), np.float32(y.iloc[train].values))
    y_pred = model.predict_proba(X.iloc[test])

    print(log_loss(y.iloc[test].values, y_pred))