from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

def classify(df):
    df = df.query('Label == "S" or Label == "D" or Label == "A"')

    X = df[["Peak Level", "Dynamic Range", "RMS Level", "RMS Variance"]].values
    y = df["Label"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, )


data = pd.read_csv(open("data.csv", "r"),
                   sep = ',', 
                   names=["Start", "End", "Peak Level", "Dynamic Range", "RMS Level", "RMS Variance", "Label"],
                   index_col=False)
classify(data)