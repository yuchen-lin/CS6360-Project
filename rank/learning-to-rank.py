
#This file used the LambdaMART algorithm with the LightGBM model to perform learning-to-rank.

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split

# Assuming 'feature1' and 'feature2' are your actual feature and target variable names
InputData = pd.read_csv("dataset.csv")

# Split the data into training and validation sets
X_train, X_validation, Y_train, Y_validation = train_test_split(
    InputData.drop(["feature1", "feature2"], axis=1),
    InputData["feature2"],
    test_size=0.2,
    random_state=42
)

# query id
queryid_train = np.bincount(X_train["query_id"])[1:]
queryid_validation = np.bincount(X_validation["query_id"])[1:]


# Create an LGBMRanker model
model = lgb.LGBMRanker(
    objective="lambdarank",
    metric="ndcg",
    learning_rate=0.09,
    max_depth=-5,
    random_state=42
)

# Train the model
model.fit(
    X=X_train,
    y=Y_train,
    group=queryid_train ,
    eval_set=[(X_validation, Y_validation)],
    eval_group=[queryid_validation],
    eval_at=10,
    verbose=10
)

# NDCG calculation function
def ndcg(labels, predictions):
    # Use predicted scores directly from the 'predictions' argument
    pre_scores = np.asarray(predictions)
    labels = np.asarray(labels)
    
    # Check if the length is greater than 1 to avoid division by zero
    if len(labels) <= 1:
        return 0.0

    # Sort the predictions
    sorted = np.argsort(pre_scores)[::-1]

    # calculate DCG
    sorted_labels = labels[sorted]
    dcg = np.sum((2 ** sorted_labels - 1) / np.log2(np.arange(2, len(labels) + 2)))

    # calculate IDCG
    ideal_labels = np.sort(labels)[::-1]
    idcg = np.sum((2 ** ideal_labels - 1) / np.log2(np.arange(2, len(labels) + 2)))

    # Calculate NDCG
    # NDCG = DCG / IDCG
    ndcg = dcg / idcg if idcg != 0 else 0.0

    return ndcg


pred_validation = model.predict(X_validation)
score = ndcg(Y_validation, pred_validation)
print(f"NDCG Score: {score}")
