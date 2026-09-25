failed_attempts = 0


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

    total_units = 0
    deliveries_processed = 0
    failed_attempts = 0

    print("SMART DELIVERY AUDITOR")
    print("Type 'quit' to exit\n")

    while True:
        value = get_valid_input()

        if value == "quit":
            break

        if value < 0:
            print("Invalid input. Please enter a positive number.")
            failed_attempts += 1
            continue

        total_units = process_delivery(total_units, value)
        deliveries_processed += 1
        tax = calculate_tax(value)

        print(f"Added delivery: {value}")
        print(f"Current total: {total_units}")
        print(f"Tax for this delivery: ${tax:.2f}")
        print(f"Deliveries processed: {deliveries_processed}\n")

    generate_report(total_units, failed_attempts)


if __name__ == "__main__":
    main()

