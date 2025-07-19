import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from src.data_loader import load_steam_data

# Load the Steam data
steam_df = load_steam_data()

def hybrid_recommend(game_name, n=10, alpha=0.5):
    """
    Recommends games using a hybrid of content and collaborative filtering.
    alpha: weight for content-based (0.0 to 1.0)
    """
    # Check if game exists in the dataset
    if game_name not in steam_df["name"].values:
        return []
    
    # Set the model path correctly
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Models")) 
    
    # Load the similarity matrices as Pickle files
    content_sim = pd.read_pickle(os.path.join(model_path, "content_similarity_df.pkl"))
    collab_sim = pd.read_pickle(os.path.join(model_path, "collab_similarity_df.pkl"))

    # Get similarity scores from both systems
    content_scores = content_sim[game_name] if game_name in content_sim.columns else pd.Series()
    collab_scores = collab_sim[game_name] if game_name in collab_sim.columns else pd.Series()

    # Combine similarity scores with weighting
    hybrid_scores = alpha * content_scores.add((1 - alpha) * collab_scores, fill_value=0)

    # Remove the selected game itself from recommendations
    hybrid_scores = hybrid_scores.drop(game_name, errors='ignore')

    # Get top N games based on similarity scores
    # Convert hybrid_scores to numeric, forcing errors to NaN
    hybrid_scores = pd.to_numeric(hybrid_scores, errors='coerce')

    # Drop NaN values that might have been introduced during conversion
    hybrid_scores = hybrid_scores.dropna()

    # Get the top N indices after cleaning
    top_indices = hybrid_scores.nlargest(n).index

    # Get recommended game details
    recommended_games = steam_df[steam_df["name"].isin(top_indices)]
    results = []
    for _, row in recommended_games.iterrows():
        results.append({
            "name": row["name"],
            "genres": row["genres"],
            "positive_ratings": row["positive_ratings"],
            "negative_ratings": row["negative_ratings"],
            "average_rating": f"{row['positive_ratings'] / (row['positive_ratings'] + row['negative_ratings']):.2f}",
            "average_playtime": f"{row['average_playtime']} mins",
            "price": f"${row['price']:.2f}" if row["price"] > 0 else "Free",
            "image_url": row.get("image_url", "https://via.placeholder.com/300"),  # Use a default placeholder if image is missing
            "store_url": row.get("store_url", "#")  # Use a default if store URL is missing
        })

    return results