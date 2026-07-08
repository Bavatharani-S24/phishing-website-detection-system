import pickle
import numpy as np

# Load trained model
model = pickle.load(open("models/phishing_model.pkl", "rb"))

print("Model expects features:", model.n_features_in_)


def predict_url(features):
    try:
        # convert to numpy
        features = np.array(features)

        # reshape
        features = features.reshape(1, -1)

        # check feature length
        if features.shape[1] != model.n_features_in_:
            print("Feature mismatch! Expected:", model.n_features_in_)
            print("Got:", features.shape[1])
            return 0.0

        # get probability
        prob = model.predict_proba(features)[0][1]

        # ensure between 0 and 1
        prob = float(np.clip(prob, 0, 1))

        return prob

    except Exception as e:
        print("Prediction error:", e)
        return 0.0

