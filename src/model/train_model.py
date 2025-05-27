import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt

def load_data(path="src/model/training_data.npz"):
    data = np.load(os.path.join(os.path.dirname(__file__), "training_data.npz"))
    keyword_vecs = data["keyword_vecs"]
    article_vecs = data["article_vecs"]
    avg_citations = data["avg_citations"]
    avg_pub_years = data["avg_pub_years"]
    targets = data["opportunity_scores"]
    X = np.hstack([keyword_vecs, article_vecs, avg_citations, avg_pub_years])
    y = targets
    return X, y

def train_and_evaluate(X, y, model_path="trained_model.joblib"):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("Model training complete.")

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")

    joblib.dump(model, os.path.join(os.path.dirname(__file__), "trained_model.joblib"))
    print("Model saved to src/model/trained_model.joblib")

    # Visualization
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, alpha=0.6, color='blue')
    plt.plot([0, 1], [0, 1], color='red', linestyle='--')
    plt.xlabel("True Opportunity Scores")
    plt.ylabel("Predicted Opportunity Scores")
    plt.title("Model Predictions vs. Actual Scores")
    plt.grid(True)
    plt.tight_layout()
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), "predictions_vs_actual.png"))
    print("Plot saved to src/model/predictions_vs_actual.png")

def main():
    X, y = load_data()
    train_and_evaluate(X, y)

if __name__ == "__main__":
    main()
