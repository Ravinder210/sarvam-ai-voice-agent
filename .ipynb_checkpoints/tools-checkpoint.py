from database import load_restaurant_database
import pandas as pd
from typing import List, Dict, Optional, Any
import re

DB = load_restaurant_database()

def _find_restaurant(name: str) -> Optional[pd.Series]:
    """A private helper to find a single restaurant with a flexible, case-insensitive search."""
    results = DB[DB['name'].str.contains(name, case=False, na=False)]
    if not results.empty:
        return results.iloc[0]
    return None

def _parse_time(time_str: str) -> Optional[str]:
    """
    A simple validation function. It assumes the LLM has already parsed the time
    into HH:MM format and just confirms the format is correct.
    """
    # Regex to validate if the input is in HH:MM format.
    if isinstance(time_str, str) and re.match(r'^\d{2}:\d{2}$', time_str):
        return time_str
    # If the LLM failed to provide the correct format, this will return None.
    return None

# --- NEW TOOL ---
def list_known_locations() -> List[str]:
    """
    Returns a list of all unique, known restaurant locations in the database.
    Use this tool when the user asks for available locations or when a search for a specific location fails.
    """
    if DB.empty:
        return ["Database is not available."]
    return sorted(DB['location'].unique().tolist())

def search_restaurants(cuisine: Optional[str] = None, location: Optional[str] = None, cost: Optional[str] = None, rating: Optional[float] = None, dish: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Searches for restaurants based on specified criteria like cuisine, location, cost, and rating.
    """
    if DB.empty: return [{"error": "Database is not available."}]
    results = DB.copy()
    if location:
        # Improve search by checking if the input is a substring of any known location
        known_locations = DB['location'].unique()
        matched_loc = [loc for loc in known_locations if location.lower() in loc.lower()]
        if not matched_loc:
            return [] # Return empty list if no location matches
        results = results[results['location'].str.contains(matched_loc[0], case=False, na=False)]
    if cuisine: results = results[results['cuisines'].str.contains(cuisine, case=False, na=False)]
    if dish: results = results[results['dish_liked'].str.contains(dish, case=False, na=False)]
    if rating: results = results[results['rate'] >= float(rating)]
    if cost:
        cost_map = {'cheap': 500, 'moderate': 1500}
        if cost in cost_map: results = results[results['approx_cost(for two people)'] <= cost_map[cost]]
        elif cost == 'expensive': results = results[results['approx_cost(for two people)'] > 1500]
    output_cols = ['name', 'location', 'cuisines', 'rate', 'approx_cost(for two people)']
    return results[output_cols].head(5).to_dict('records')

def check_availability(restaurant_name: str, party_size: int, time: str) -> Dict[str, Any]:
    """
    Checks if a specific restaurant has a table available for a given party size and time.
    """
    try:
        party_size = int(party_size)
        if party_size < 1:
            return {'status': 'Failed', 'reason': 'Party size must be a positive number (e.g., 1, 2, 3).'}
    except (ValueError, TypeError):
        return {'status': 'Failed', 'reason': 'Invalid party size. Please provide a number.'}

    # The LLM is now responsible for parsing. We just validate the format it provides.
    parsed_time = _parse_time(time)
    if parsed_time is None:
        # This error now tells us the LLM failed its instruction.
        return {'status': 'Failed', 'reason': f"The time '{time}' was not provided in the required HH:MM format."}

    info = _find_restaurant(restaurant_name)
    if info is None: return {'status': 'Not Available', 'reason': f"I couldn't find a restaurant with the name '{restaurant_name}'."}
    
    if info['book_table'].lower() in ['no', 'false']: return {'status': 'Not Available', 'reason': 'This restaurant does not accept table reservations.'}
    if party_size > info['seating_capacity']: return {'status': 'Not Available', 'reason': f"The party size of {party_size} exceeds the restaurant's capacity of {int(info['seating_capacity'])}."}
    if parsed_time not in info['available_time_slots']: return {'status': 'Not Available', 'reason': f"The requested time '{time}' is not an available slot. Available slots are: {info['available_time_slots']}"}
    
    return {'status': 'Available'}
def create_reservation(restaurant_name: str, party_size: int, time: str, customer_name: str) -> Dict[str, Any]:
    """
    Creates a mock reservation and returns structured details for state management.
    """
    availability_check = check_availability(restaurant_name, party_size, time)
    if availability_check.get('status') != 'Available':
        return {'status': 'Failed', 'reason': availability_check.get('reason', 'Unknown availability issue.')}
    booking_details = {"restaurant_name": restaurant_name, "party_size": party_size, "time": time, "customer_name": customer_name}
    confirmation_message = (f"Success! Reservation confirmed for {customer_name} at {restaurant_name} for a party of {party_size} at {time}.")
    return {'status': 'Success', 'message': confirmation_message, 'booking_details': booking_details}

# ... (cancel_reservation and check_table_type remain the same, they are already robust) ...
def cancel_reservation(customer_name: str, restaurant_name: str) -> Dict[str, str]:
    """Cancels a reservation for a user at a specific restaurant."""
    return {'status': 'Success', 'message': f'Your reservation for {customer_name} at {restaurant_name} has been successfully cancelled.'}

def check_table_type(restaurant_name: str, party_size: int) -> Dict[str, Any]:
    """Checks if a restaurant has specific types of tables, like large family tables."""
    info = _find_restaurant(restaurant_name)
    if info is None: return {'status': 'Not Found', 'message': f"I couldn't find a restaurant with the name '{restaurant_name}'."}
    party_size = int(party_size)
    available_tables = info.get('table_type', [])
    for table in available_tables:
        parts = table.split('-')
        if len(parts) > 0 and parts[0].isdigit():
            if int(parts[0]) >= party_size:
                return {'status': 'Available', 'message': f"Yes, {restaurant_name} has large tables available, such as '{table}'."}
    return {'status': 'Not Available', 'message': f"I couldn't find any specific large tables for {party_size} people listed for {restaurant_name}. Their maximum capacity is {int(info['seating_capacity'])}."}