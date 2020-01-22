import sys
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def classify(df):
    print(df)
    df = df.query('Label in ["H","S"]')
    print(df)

    X = df[["Peak Level", "Dynamic Range", "RMS Level", "RMS Variance"]].values
    y = df["Label"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, train_size=0.75)

    lr = LogisticRegression()
    lr.fit(X_train, y_train)

    score = lr.score(X_test, y_test)
    print(score)

# sys.argv[1] - .csv file with all required data (export from librosaScript)
data = data = pd.read_csv(open(sys.argv[1], "r"),
                   sep = ',', 
                   names=["Start", "End", "Peak Level", "Dynamic Range", "RMS Level", "RMS Variance", "Label"])
classify(data)