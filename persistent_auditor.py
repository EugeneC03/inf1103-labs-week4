failed_attempts = 0

def load_inventory():
    """Load total and transaction history from inventory.txt"""
    try:
        with open("inventory.txt", "r") as file:
            lines = file.readlines()  # Returns list of lines
            
            if len(lines) >= 2:
                # First line: total (strip whitespace/newline)
                total = int(lines.strip())  # ✅ FIXED - use lines
                
                # Second line: transaction history (strip whitespace/newline)
                history_str = lines.strip()  # ✅ FIXED - use lines
                
                if history_str:
                    # Split comma-separated values into integers
                    history = [int(x.strip()) for x in history_str.split(",")]
                else:
                    history = []
                
                return total, history
            else:
                # File exists but doesn't have enough lines
                return 0, []
                
    except FileNotFoundError:
        # File doesn't exist yet - start fresh
        print("No previous inventory found. Starting fresh.")
        return 0, []
        
    except ValueError as e:
        # Invalid data format in file
        print(f"Error parsing inventory file: {e}")
        return 0, []
        
    except Exception as e:
        # Any other error
        print(f"Error loading inventory: {e}")
        return 0, []

def save_inventory(total_units, transaction_history):
    """Save total and transaction history to inventory.txt"""
    try:
        with open("inventory.txt", "w") as file:
            file.write(f"{total_units}\n")
            file.write(",".join(map(str, transaction_history)) + "\n")
        print("Inventory saved successfully to inventory.txt")
    except Exception as e:
        print(f"Error saving inventory: {e}")

def get_valid_input():
    global failed_attempts

    while True:
        user_input = input("Enter delivery amount: ").strip()

        if user_input.lower() == "quit":
            return "quit"

        if user_input.isdigit():
            return int(user_input)

        failed_attempts += 1
        print("Invalid input. Please enter a valid integer or 'quit'.")

def process_delivery(current_total, amount):
    return current_total + amount

def calculate_tax(amount):
    return amount * 0.10

def generate_report(total_units, failed_count):
    print("\n" + "=" * 40)
    print("Total Deliveries Processed:", total_units)
    print("Number of Failed/Rejected Entries:", failed_count)
    print("=" * 40)

def main():
    global failed_attempts

    # Load previous inventory data
    total_units, transaction_history = load_inventory()

    # Initialize counters
    deliveries_processed = len(transaction_history) 
    failed_attempts = 0  # ✅ ADDED - initialize here too
    
    print("SMART DELIVERY AUDITOR")
    print("Type 'quit' to exit\n")
    
    if total_units > 0:
        print(f"Loaded previous total: {total_units}")
        print(f"Previous transactions: {transaction_history}\n")

    while True:
        value = get_valid_input()

        if value == "quit":
            save_inventory(total_units, transaction_history)  # ✅ ADDED
            break

        if value < 0:
            print("Invalid input. Please enter a positive number.")
            failed_attempts += 1
            continue

        total_units = process_delivery(total_units, value)
        transaction_history.append(value)  # ✅ ADDED - THIS IS KEY FOR STEP 2!
        deliveries_processed += 1
        tax = calculate_tax(value)

        print(f"Added delivery: {value}")
        print(f"Current total: {total_units}")
        print(f"Tax for this delivery: \${tax:.2f}")
        print(f"Deliveries processed: {deliveries_processed}")
        print(f"Transaction history: {transaction_history}\n")  # ✅ Show history for debugging

    generate_report(total_units, failed_attempts)

if __name__ == "__main__":
    main()