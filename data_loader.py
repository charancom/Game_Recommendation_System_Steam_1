import pandas as pd
import os

# Define the data paths
DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'DataSets', 'Raw')

# Load the main datasets
def load_steam_data():
    try:
        # Load the main game dataset
        steam_df = pd.read_csv(os.path.join(DATASETS_DIR, 'steam.csv'))

        # Extract release year
        steam_df['release_year'] = pd.to_datetime(steam_df['release_date']).dt.year

        # Calculate total ratings and positive rating percentage
        steam_df['total_ratings'] = steam_df['positive_ratings'] + steam_df['negative_ratings']
        steam_df['positive_percentage'] = steam_df['positive_ratings'] / steam_df['total_ratings']

        # Categorize average playtime
        bins = [0, 60, 500, 10000]
        labels = ['Short', 'Medium', 'Long']
        steam_df['playtime_category'] = pd.cut(steam_df['average_playtime'], bins=bins, labels=labels)

        # Categorize price
        bins = [-1, 0, 10, 100]
        labels = ['Free', 'Cheap', 'Expensive']
        steam_df['price_category'] = pd.cut(steam_df['price'], bins=bins, labels=labels)

        # Add image URL column if it exists
        if 'image_url' not in steam_df.columns:
            print("Warning: No 'image_url' column found in the data.")
            steam_df['image_url'] = "https://via.placeholder.com/300"

        return steam_df

    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Test the function
if __name__ == "__main__":
    steam_df = load_steam_data()
    if steam_df is not None:
        print(steam_df.head())
        print(steam_df[['name', 'release_year', 'total_ratings', 'positive_percentage', 'playtime_category', 'price_category', 'image_url']].head(10))
    else:
        print("Failed to load data.")
