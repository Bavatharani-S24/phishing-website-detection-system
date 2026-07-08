import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# ---------------- LOAD DATA ---------------- #

phishing = pd.read_csv("phishing-urls.csv")
legit = pd.read_csv("legitimate-urls.csv")

# ---------------- COMBINE ---------------- #

df = pd.concat([phishing, legit], ignore_index=True)

# ---------------- CLEAN ---------------- #

df.columns = df.columns.str.strip()

# ---------------- TARGET ---------------- #

y = df["label"]

print("Label counts:")
print(y.value_counts())

# ---------------- FEATURES ---------------- #

X = df.drop(["label", "Domain"], axis=1)

# ensure numeric
X = X.apply(pd.to_numeric, errors="coerce")
X = X.fillna(0)

print("Total features:", X.shape[1])

# ---------------- TRAIN ---------------- #

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    random_state=42
)

model.fit(X_train, y_train)

# ---------------- EVALUATE ---------------- #

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", accuracy)

# ---------------- SAVE ---------------- #

pickle.dump(model, open("models/phishing_model.pkl", "wb"))

print("Model trained successfully")
print("Model expects features:", model.n_features_in_)



