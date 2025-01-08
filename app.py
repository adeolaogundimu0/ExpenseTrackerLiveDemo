from flask import Flask, render_template, request, redirect, url_for, session
from expense import Expense
import calendar
import datetime

ExpenseApp = Flask(__name__)
ExpenseApp.secret_key = "your_secret_key"  # Needed for session management


# File to store expenses
EXPENSE_FILE = "expenses.csv"

# Routes
@ExpenseApp.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Ensure budget is not negative
        budget = float(request.form["budget"])
        if budget < 0:
            return render_template("home.html", error="❌ Budget cannot be negative.")
        session["budget"] = budget
        return redirect(url_for("add_expense"))
    return render_template("home.html")


@ExpenseApp.route("/add", methods=["GET", "POST"])
def add_expense():
    if "budget" not in session:
        return redirect(url_for("home"))  # Ensure budget is set before adding expenses

    if request.method == "POST":
        # Get form data
        name = request.form["name"].strip().title()
        amount = float(request.form["amount"])
        category = request.form["category"]

        # Save expense to file
        expense = Expense(name=name, category=category, amount=amount)
        save_expense_to_file(expense, EXPENSE_FILE)

        return redirect(url_for("summary"))
    return render_template("add_expense.html")


@ExpenseApp.route("/summary")
def summary():
    if "budget" not in session:
        return redirect(url_for("home"))  # Ensure budget is set before viewing summary

    budget = session["budget"]
    expenses, summary_data = summarize_expense(EXPENSE_FILE, budget)
    return render_template("summary.html", expenses=expenses, summary=summary_data)


# Helper Functions
def save_expense_to_file(expense, expense_file_path):
    with open(expense_file_path, "a", encoding="utf-8") as f:
        f.write(f"{expense.name},{expense.amount},{expense.category}\n")


def summarize_expense(expense_file_path, budget):
    expenses = []
    with open(expense_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            name, amount, category = line.strip().split(",")
            expenses.append(Expense(name=name, category=category, amount=float(amount)))

    # Calculate totals
    amount_by_category = {}
    for expense in expenses:
        amount_by_category[expense.category] = amount_by_category.get(expense.category, 0) + expense.amount

    total_spent = sum(expense.amount for expense in expenses)
    remaining_budget = budget - total_spent

    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    remaining_days = days_in_month - now.day
    daily_budget = round(remaining_budget / remaining_days,2) if remaining_days > 0 else 0.00

    summary_data = {
        "by_category": amount_by_category,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget,
        "daily_budget": daily_budget,
    }

    return expenses, summary_data
def clear_expenses_file():
    with open("expenses.csv", "w", encoding="utf-8") as f:
        pass


if __name__ == "__main__":
    clear_expenses_file()

    ExpenseApp.run(debug=True)
