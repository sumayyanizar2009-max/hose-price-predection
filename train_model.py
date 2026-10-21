import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Load the dataset
data = pd.read_csv("house_data.csv")

# Select input features and target
X = data[["area", "bedrooms", "bathrooms"]]
y = data["price"]

# Train the model
model = LinearRegression()
model.fit(X, y)

# Save the trained model
with open("house_price_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model trained successfully!")