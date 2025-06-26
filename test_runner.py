# test_runner.py

import tools
import pandas as pd

# --- Test Parameters (CHANGE THESE TO MATCH YOUR CSV DATA) ---
test_location = "Indiranagar"
test_cuisine = "Mediterranean"
test_dish = "Dumplings"
test_restaurant_good = "Punjab Grill" # A restaurant that DOES exist and takes bookings
test_restaurant_no_booking = "some_restaurant_that_doesnt_take_bookings" # Find one in your CSV
test_restaurant_bad = "Non Existent Restaurant"

def run_tests():
    """Runs a series of tests on our tool functions."""
    
    print("--- 1. Testing Database Loading ---")
    if tools.DB.empty:
        print("🔴 FAILED: The database DataFrame is empty. Check database.py and your CSV file path.")
        return
    else:
        print(f"✅ PASSED: Database loaded successfully with {len(tools.DB)} records.")
        # print("Sample of loaded data:")
        # print(tools.DB.head(2))


    print("\n--- 2. Testing search_restaurants() ---")
    
    # Test 2a: Search by location
    print(f"\nSearching for restaurants in '{test_location}'...")
    results_loc = tools.search_restaurants(location=test_location)
    print(f"Found {len(results_loc)} results.")
    print(results_loc)
    assert len(results_loc) > 0, "Test 2a FAILED: Expected to find restaurants by location."
    print("✅ PASSED: Search by location.")

    # Test 2b: Search by cuisine and location
    print(f"\nSearching for '{test_cuisine}' in '{test_location}'...")
    results_cuisine = tools.search_restaurants(cuisine=test_cuisine, location=test_location)
    print(f"Found {len(results_cuisine)} results.")
    print(results_cuisine)
    assert len(results_cuisine) > 0, "Test 2b FAILED: Expected to find restaurants by cuisine and location."
    print("✅ PASSED: Search by cuisine and location.")
    
    # Test 2c: Search for a specific dish
    print(f"\nSearching for a place that serves '{test_dish}'...")
    results_dish = tools.search_restaurants(dish=test_dish)
    print(f"Found {len(results_dish)} results.")
    print(results_dish)
    assert len(results_dish) > 0, "Test 2c FAILED: Expected to find restaurants by dish."
    print("✅ PASSED: Search by dish.")

    # Test 2d: Search that should yield no results
    print("\nSearching for 'Impossible Cuisine'...")
    results_none = tools.search_restaurants(cuisine="Impossible Cuisine")
    print(f"Found {len(results_none)} results.")
    assert len(results_none) == 0, "Test 2d FAILED: Expected zero results."
    print("✅ PASSED: Handled no-result search correctly.")


    print("\n--- 3. Testing check_availability() ---")
    
    # Test 3a: Successful check
    print(f"\nChecking availability for '{test_restaurant_good}' (Party: 2, Time: 19:00)...")
    avail_good = tools.check_availability(test_restaurant_good, 2, "19:00")
    print(avail_good)
    assert avail_good['status'] == 'Available', "Test 3a FAILED: Expected availability."
    print("✅ PASSED: Successful availability check.")

    # Test 3b: Restaurant not found
    print(f"\nChecking availability for '{test_restaurant_bad}'...")
    avail_bad = tools.check_availability(test_restaurant_bad, 2, "19:00")
    print(avail_bad)
    assert avail_bad['status'] == 'Not Available', "Test 3b FAILED: Expected 'Not Found' status."
    print("✅ PASSED: Handled non-existent restaurant.")

    # Test 3c: Party size too large
    print(f"\nChecking availability for '{test_restaurant_good}' (Party: 200, Time: 19:00)...")
    avail_party = tools.check_availability(test_restaurant_good, 200, "19:00")
    print(avail_party)
    assert 'exceeds the restaurant' in avail_party['reason'], "Test 3c FAILED: Expected party size error."
    print("✅ PASSED: Handled party size too large.")

    # Test 3d: Time slot not available
    print(f"\nChecking availability for '{test_restaurant_good}' (Party: 2, Time: 11:00)...")
    avail_time = tools.check_availability(test_restaurant_good, 2, "11:00")
    print(avail_time)
    assert 'not an available slot' in avail_time['reason'], "Test 3d FAILED: Expected time slot error."
    print("✅ PASSED: Handled unavailable time slot.")


    print("\n--- 4. Testing create_reservation() ---")

    # Test 4a: Successful reservation
    print(f"\nAttempting successful reservation for '{test_restaurant_good}'...")
    res_good = tools.create_reservation(test_restaurant_good, 2, "19:00", "John Doe")
    print(res_good)
    assert res_good['status'] == 'Success', "Test 4a FAILED: Expected successful reservation."
    print("✅ PASSED: Successful reservation creation.")

    # Test 4b: Failed reservation (due to time)
    print(f"\nAttempting failed reservation for '{test_restaurant_good}'...")
    res_bad = tools.create_reservation(test_restaurant_good, 2, "11:00", "Jane Doe")
    print(res_bad)
    assert res_bad['status'] == 'Failed', "Test 4b FAILED: Expected failed reservation."
    print("✅ PASSED: Handled failed reservation correctly.")

    print("\n\n🎉 ALL TESTS COMPLETED! 🎉")


if __name__ == "__main__":
    run_tests()