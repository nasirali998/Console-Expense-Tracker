"""
Personal Expense Tracker System (Console-Based)
-------------------------------------------------
A simple, menu-driven Python application to record, manage and analyze
personal expenses. Data is stored permanently in a CSV file so records
survive between program runs.

Run with:  python expense_tracker.py
"""

import csv
import os
from datetime import datetime

DATA_FILE = "expenses.csv"
FIELDNAMES = ["id", "date", "category", "description", "amount"]


# --------------------------------------------------------------------------
# File handling helpers
# --------------------------------------------------------------------------
def initialize_file():
    """Create the CSV file with headers if it does not already exist."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def read_all_expenses():
    """Return a list of all expense records (each record is a dict)."""
    initialize_file()
    with open(DATA_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_all_expenses(expenses):
    """Overwrite the CSV file with the given list of expense records."""
    with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


def get_next_id(expenses):
    """Generate the next unique integer id for a new expense."""
    if not expenses:
        return 1
    return max(int(e["id"]) for e in expenses) + 1


# --------------------------------------------------------------------------
# Input validation helpers
# --------------------------------------------------------------------------
def input_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def input_date(prompt, allow_blank_for_today=True):
    while True:
        value = input(prompt).strip()
        if not value and allow_blank_for_today:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")


def input_amount(prompt):
    while True:
        value = input(prompt).strip()
        try:
            amount = float(value)
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")


def input_choice(prompt, valid_choices):
    while True:
        value = input(prompt).strip()
        if value in valid_choices:
            return value
        print(f"Invalid choice. Please select one of: {', '.join(valid_choices)}")


# --------------------------------------------------------------------------
# Core feature functions
# --------------------------------------------------------------------------
def add_expense():
    print("\n--- Add New Expense ---")
    expenses = read_all_expenses()
    new_id = get_next_id(expenses)

    date = input_date("Enter date (YYYY-MM-DD) [blank = today]: ")
    category = input_nonempty("Enter category (e.g. Food, Travel, Bills): ")
    description = input("Enter description (optional): ").strip()
    amount = input_amount("Enter amount: ")

    record = {
        "id": str(new_id),
        "date": date,
        "category": category,
        "description": description,
        "amount": f"{amount:.2f}",
    }

    expenses.append(record)
    write_all_expenses(expenses)
    print(f"Expense added successfully with ID {new_id}.")


def view_all_expenses():
    print("\n--- All Expenses ---")
    expenses = read_all_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return
    print_expense_table(expenses)
    total = sum(float(e["amount"]) for e in expenses)
    print(f"\nTotal Expenses: {total:.2f}")


def print_expense_table(expenses):
    header = f"{'ID':<5}{'Date':<12}{'Category':<15}{'Description':<25}{'Amount':>10}"
    print(header)
    print("-" * len(header))
    for e in expenses:
        desc = e["description"][:24]
        print(f"{e['id']:<5}{e['date']:<12}{e['category']:<15}{desc:<25}{float(e['amount']):>10.2f}")


def search_expenses():
    print("\n--- Search Expenses ---")
    print("Search by: 1) ID  2) Category  3) Date  4) Description keyword")
    choice = input_choice("Select an option (1-4): ", ["1", "2", "3", "4"])
    expenses = read_all_expenses()
    results = []

    if choice == "1":
        search_id = input_nonempty("Enter ID to search: ")
        results = [e for e in expenses if e["id"] == search_id]
    elif choice == "2":
        category = input_nonempty("Enter category to search: ").lower()
        results = [e for e in expenses if e["category"].lower() == category]
    elif choice == "3":
        date = input_date("Enter date to search (YYYY-MM-DD): ", allow_blank_for_today=False)
        results = [e for e in expenses if e["date"] == date]
    elif choice == "4":
        keyword = input_nonempty("Enter keyword to search in description: ").lower()
        results = [e for e in expenses if keyword in e["description"].lower()]

    if not results:
        print("No matching expenses found.")
    else:
        print_expense_table(results)


def find_expense_by_id(expenses, expense_id):
    for e in expenses:
        if e["id"] == expense_id:
            return e
    return None


def update_expense():
    print("\n--- Update Expense ---")
    expenses = read_all_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    expense_id = input_nonempty("Enter the ID of the expense to update: ")
    record = find_expense_by_id(expenses, expense_id)

    if not record:
        print("Expense ID not found.")
        return

    print("Leave a field blank to keep its current value.")
    print(f"Current values -> Date: {record['date']}, Category: {record['category']}, "
          f"Description: {record['description']}, Amount: {record['amount']}")

    new_date = input("New date (YYYY-MM-DD): ").strip()
    if new_date:
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            record["date"] = new_date
        except ValueError:
            print("Invalid date format. Date not updated.")

    new_category = input("New category: ").strip()
    if new_category:
        record["category"] = new_category

    new_description = input("New description: ").strip()
    if new_description:
        record["description"] = new_description

    new_amount = input("New amount: ").strip()
    if new_amount:
        try:
            amount_value = float(new_amount)
            if amount_value > 0:
                record["amount"] = f"{amount_value:.2f}"
            else:
                print("Amount must be greater than zero. Amount not updated.")
        except ValueError:
            print("Invalid amount. Amount not updated.")

    write_all_expenses(expenses)
    print("Expense updated successfully.")


def delete_expense():
    print("\n--- Delete Expense ---")
    expenses = read_all_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    expense_id = input_nonempty("Enter the ID of the expense to delete: ")
    record = find_expense_by_id(expenses, expense_id)

    if not record:
        print("Expense ID not found.")
        return

    confirm = input_choice(
        f"Are you sure you want to delete expense ID {expense_id}? (y/n): ", ["y", "n"]
    )
    if confirm == "y":
        expenses = [e for e in expenses if e["id"] != expense_id]
        write_all_expenses(expenses)
        print("Expense deleted successfully.")
    else:
        print("Deletion cancelled.")


def daily_report():
    print("\n--- Daily Expense Report ---")
    date = input_date("Enter date (YYYY-MM-DD) [blank = today]: ")
    expenses = read_all_expenses()
    day_expenses = [e for e in expenses if e["date"] == date]

    if not day_expenses:
        print(f"No expenses found for {date}.")
        return

    print_expense_table(day_expenses)
    total = sum(float(e["amount"]) for e in day_expenses)
    print(f"\nTotal for {date}: {total:.2f}")


def monthly_report():
    print("\n--- Monthly Expense Report ---")
    month = input_nonempty("Enter month and year (YYYY-MM): ")
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid format. Please use YYYY-MM.")
        return

    expenses = read_all_expenses()
    month_expenses = [e for e in expenses if e["date"].startswith(month)]

    if not month_expenses:
        print(f"No expenses found for {month}.")
        return

    print_expense_table(month_expenses)
    total = sum(float(e["amount"]) for e in month_expenses)
    print(f"\nTotal for {month}: {total:.2f}")


def category_report():
    print("\n--- Category-wise Expense Report ---")
    expenses = read_all_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    totals = {}
    for e in expenses:
        cat = e["category"]
        totals[cat] = totals.get(cat, 0) + float(e["amount"])

    print(f"{'Category':<20}{'Total Amount':>15}")
    print("-" * 35)
    for cat, amount in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat:<20}{amount:>15.2f}")

    grand_total = sum(totals.values())
    print(f"\nGrand Total: {grand_total:.2f}")


def total_expense_summary():
    print("\n--- Total Expense Summary ---")
    expenses = read_all_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    total = sum(float(e["amount"]) for e in expenses)
    count = len(expenses)
    average = total / count if count else 0

    print(f"Total Number of Expenses: {count}")
    print(f"Total Amount Spent: {total:.2f}")
    print(f"Average Expense Amount: {average:.2f}")


def highest_lowest_expense():
    print("\n--- Highest and Lowest Expense ---")
    expenses = read_all_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    highest = max(expenses, key=lambda e: float(e["amount"]))
    lowest = min(expenses, key=lambda e: float(e["amount"]))

    print("Highest Expense:")
    print_expense_table([highest])
    print("\nLowest Expense:")
    print_expense_table([lowest])


# --------------------------------------------------------------------------
# Menu and main loop
# --------------------------------------------------------------------------
MENU_TEXT = """
==============================================
       PERSONAL EXPENSE TRACKER SYSTEM
==============================================
 1. Add Expense
 2. View All Expenses
 3. Search Expense
 4. Update Expense
 5. Delete Expense
 6. Daily Expense Report
 7. Monthly Expense Report
 8. Category-wise Expense Report
 9. Total Expense Summary
10. Highest and Lowest Expense
11. Exit
==============================================
"""


def main():
    initialize_file()
    actions = {
        "1": add_expense,
        "2": view_all_expenses,
        "3": search_expenses,
        "4": update_expense,
        "5": delete_expense,
        "6": daily_report,
        "7": monthly_report,
        "8": category_report,
        "9": total_expense_summary,
        "10": highest_lowest_expense,
    }

    while True:
        print(MENU_TEXT)
        choice = input("Enter your choice (1-11): ").strip()

        if choice == "11":
            print("Thank you for using the Personal Expense Tracker System. Goodbye!")
            break

        action = actions.get(choice)
        if action:
            try:
                action()
            except Exception as error:
                print(f"An unexpected error occurred: {error}")
        else:
            print("Invalid choice. Please enter a number between 1 and 11.")


if __name__ == "__main__":
    main()