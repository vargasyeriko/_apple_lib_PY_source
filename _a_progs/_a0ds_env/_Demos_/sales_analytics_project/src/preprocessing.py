
# ---------------------------------------------------------
# PREPROCESSING
# encode categoricals + split features/target
# ---------------------------------------------------------

import pandas as pd

def prep_features_target(df, target="purchase"):

    # separate X and y
    X = df.drop(columns=[target])
    y = df[target]

    # encode categorical variables
    X = pd.get_dummies(X, drop_first=True)

    print("\nFEATURE MATRIX:", X.shape)
    print("TARGET:", y.shape)

    return X, y
