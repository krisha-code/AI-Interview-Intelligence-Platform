import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import pickle

df = pd.read_csv(
    "datasets/raw/resumes/Resume.csv"
)

resume_embeddings = np.load(
    "models/resume_embeddings.npy"
)
x = resume_embeddings
y = df['Category']

print('resume_embeddings shape:', resume_embeddings.shape)
print('Category shape:', y.shape)

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)
print('Encoded Category shape:', y_encoded.shape)

# Train-test split
x_train,X_test,y_train,y_test = train_test_split(
    x, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print('Train set shape:', x_train.shape, y_train.shape)
print('Test set shape:', X_test.shape, y_test.shape)


from sklearn.linear_model import LogisticRegression
model = LogisticRegression (max_iter=1000)
random_state = 42

model.fit(x_train, y_train)
y_pred = model.predict(X_test)

from sklearn.metrics import accuracy_score, classification_report
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print("Classification Report:")
print(classification_report(y_test, y_pred))

from sklearn.ensemble import RandomForestClassifier
rf_model = RandomForestClassifier(
    n_estimators=100, random_state=random_state
)
rf_model.fit(x_train, y_train)
y_pred_rf = rf_model.predict(X_test)
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print(f"Random Forest Accuracy: {accuracy_rf:.4f}")
print("Random Forest Classification Report:")
print(classification_report(y_test, y_pred_rf))

from sklearn.svm import LinearSVC
svm_model = LinearSVC(random_state=42, max_iter=10000)
svm_model.fit(x_train, y_train)
y_pred_svm = svm_model.predict(X_test)
accuracy_svm = accuracy_score(y_test, y_pred_svm)
print(f"SVM Accuracy: {accuracy_svm:.4f}")
print("SVM Classification Report:")
print(classification_report(y_test, y_pred_svm))

from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    objective="multi:softmax",
    num_class=len(np.unique(y_encoded))
)
xgb_model.fit(x_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)
accuracy_xgb = accuracy_score(y_test, y_pred_xgb)
print(f"XGBoost Accuracy: {accuracy_xgb:.4f}")
print("XGBoost Classification Report:")
print(classification_report(y_test, y_pred_xgb))

# Save Best Model (SVM)

with open(
    "models/category_classifier.pkl",
    "wb"
) as f:
    pickle.dump(svm_model, f)

# Save Label Encoder

with open(
    "models/category_encoder.pkl",
    "wb"
) as f:
    pickle.dump(le, f)

with open(
    "models/category_classifier.pkl",
    "wb"
) as f:
    pickle.dump(svm_model, f)

with open(
    "models/category_encoder.pkl",
    "wb"
) as f:
    pickle.dump(le, f)

print("SVM model saved successfully")
print("Label Encoder saved successfully")