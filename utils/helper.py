import time
import random

id_counter = 0

def generate_unique_id():
    global id_counter
    # Get the current timestamp in milliseconds
    timestamp = int(time.time() * 1000)
    
    # Increment the counter (resets every millisecond)
    id_counter += 1
    if id_counter > 9999:  # Limit to 4 digits for simplicity
        id_counter = 0
    
    # Generate a random 5-digit number
    random_number = random.randint(10000, 99999)
    
    # Combine timestamp, counter, and random number
    unique_id = f"{timestamp}{id_counter:04}{random_number}"
    return int(unique_id)