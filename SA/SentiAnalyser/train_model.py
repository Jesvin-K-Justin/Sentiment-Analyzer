# train_model.py
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler  # Import StandardScaler for data scaling
import joblib

# Load data
train_data = pd.read_csv('D:\\Anaconda\\labeled_data.csv')
train_data.dropna(subset=['tweet'], inplace=True)

# Separate features (X) and target (y)
X_train = train_data['tweet']
y_train = train_data['hate_speech']

# Train the model
model = make_pipeline(CountVectorizer(stop_words='english'), LogisticRegression(max_iter=1000))  # Increase max_iter
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'trained_model.pkl')
