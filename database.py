# database.py

import pandas as pd
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the database in memory
_database = None

def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Helper function to clean and preprocess the DataFrame."""
    logger.info("Starting data cleaning process...")
    
    # Convert columns to string type to safely use .str methods
    df['rate'] = df['rate'].astype(str)
    df['approx_cost(for two people)'] = df['approx_cost(for two people)'].astype(str)

    # Clean the 'rate' column (e.g., '4.1/5' -> 4.1)
    df['rate'] = pd.to_numeric(df['rate'].str.split('/').str[0], errors='coerce')
    df['rate'] = df['rate'].fillna(0) # Fill non-rated restaurants with 0

    # Clean 'approx_cost(for two people)'
    df['approx_cost(for two people)'] = pd.to_numeric(df['approx_cost(for two people)'].str.replace(',', ''), errors='coerce')
    df['approx_cost(for two people)'] = df['approx_cost(for two people)'].fillna(0)

    # Convert 'seating_capacity' to numeric
    df['seating_capacity'] = pd.to_numeric(df['seating_capacity'], errors='coerce')
    df['seating_capacity'] = df['seating_capacity'].fillna(2) # Assume a default of 2 if missing

    # Safely evaluate string representations of lists
    for col in ['available_time_slots', 'table_type']:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else [])

    logger.info("Data cleaning complete.")
    return df

def load_restaurant_database(file_path: str = 'data/zomato.csv') -> pd.DataFrame:
    """
    Loads the restaurant data from a CSV file into a pandas DataFrame.
    Applies cleaning and preprocessing steps.
    Caches the DataFrame in memory to avoid reloading.
    """
    global _database
    if _database is not None:
        return _database

    try:
        logger.info(f"Loading database from {file_path}...")
        df = pd.read_csv(file_path, encoding='utf-8')
        _database = _clean_data(df)
        logger.info("Database loaded and cached successfully.")
        return _database
    except FileNotFoundError:
        logger.error(f"Error: The file {file_path} was not found.")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading the database: {e}")
        return pd.DataFrame()

