
import random
from datetime import date, timedelta
import sqlite3
import streamlit as st

CATEGORIES = [
    "Food",
    "Transport",
    "Housing",
    "Entertainment",
    "Shopping",
    "Health",
    "Utilities",
    "Other",
]

_ALLOWED_SORT_COLUMNS = {"date", "amount", "category"}
_ALLOWED_SORT_DIRECTIONS = {"asc", "desc"}

DB_PATH = "finance_tracker.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@st.cache_resource
def get_connection():
    return _get_conn()


def _execute(sql, params=None):
    conn = get_connection()
    cur = conn.execute(sql, params or ())
    conn.commit()
    return cur


def _query(sql, params=None):
    conn = get_connection()
    cur = conn.execute(sql, params or ())
    return [dict(row) for row in cur.fetchall()]


def init_db():
    _execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _validate_transaction(amount, description, category, tx_date):
    if amount is None or float(amount) <= 0:
        raise ValueError("Amount must be greater than 0.")

    if not description or not description.strip():
        raise ValueError("Description is required.")

    if category not in CATEGORIES:
        raise ValueError("Category is invalid.")

    if tx_date > date.today().isoformat():
        raise ValueError("Date cannot be in the future.")


def add_transaction(amount, description, category, tx_date):
    _validate_transaction(amount, description, category, tx_date)
    cur = _execute(
        "INSERT INTO transactions (amount, description, category, date) VALUES (?, ?, ?, ?)",
        (float(amount), description.strip(), category, tx_date),
    )
    return cur.lastrowid


def get_transaction(transaction_id):
    rows = _query(
        "SELECT id, amount, description, category, date, created_at FROM transactions WHERE id = ?",
        (int(transaction_id),),
    )
    return rows[0] if rows else None


def list_transactions(
    start_date=None,
    end_date=None,
    category=None,
    search=None,
    sort_by="date",
    sort_direction="desc",
):
    sort_by = sort_by if sort_by in _ALLOWED_SORT_COLUMNS else "date"
    sort_direction = sort_direction.lower()
    if sort_direction not in _ALLOWED_SORT_DIRECTIONS:
        sort_direction = "desc"

    query = "SELECT id, amount, description, category, date, created_at FROM transactions WHERE 1=1"
    params = []

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    if category:
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND LOWER(description) LIKE ?"
        params.append(f"%{search.strip().lower()}%")

    query += f" ORDER BY {sort_by} {sort_direction}, id DESC"

    return _query(query, params)


def update_transaction(transaction_id, amount, description, category, tx_date):
    _validate_transaction(amount, description, category, tx_date)
    cur = _execute(
        "UPDATE transactions SET amount = ?, description = ?, category = ?, date = ? WHERE id = ?",
        (float(amount), description.strip(), category, tx_date, int(transaction_id)),
    )
    return cur.rowcount > 0


def delete_transaction(transaction_id):
    cur = _execute(
        "DELETE FROM transactions WHERE id = ?",
        (int(transaction_id),),
    )
    return cur.rowcount > 0


def get_total_spend_all_time():
    rows = _query("SELECT COALESCE(SUM(amount), 0) AS total FROM transactions")
    return float(rows[0]["total"])


def get_total_spend_month(year, month):
    ym = f"{year:04d}-{month:02d}"
    rows = _query(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE strftime('%Y-%m', date) = ?",
        (ym,),
    )
    return float(rows[0]["total"])


_DUMMY_EXPENSES = [
    ("Grocery run at Walmart", "Food", 45.23),
    ("Weekly groceries", "Food", 67.89),
    ("Milk and eggs", "Food", 8.50),
    ("Bread and butter", "Food", 6.20),
    ("Chicken and rice", "Food", 14.30),
    ("Fruits and vegetables", "Food", 22.10),
    ("Frozen pizza", "Food", 9.99),
    ("Snacks for movie night", "Food", 12.45),
    ("Coffee beans", "Food", 18.99),
    ("Lunch at Chipotle", "Food", 13.50),
    ("Dinner at Italian restaurant", "Food", 42.00),
    ("Sushi takeout", "Food", 28.75),
    ("McDonald's drive-through", "Food", 11.20),
    ("Thai food delivery", "Food", 24.50),
    ("Pizza delivery", "Food", 19.99),
    ("Starbucks latte", "Food", 6.75),
    ("Subway sandwich", "Food", 9.80),
    ("Ice cream", "Food", 5.50),
    ("Protein bars", "Food", 15.99),
    ("Energy drinks", "Food", 8.40),
    ("Pasta and sauce", "Food", 7.60),
    ("Cereal and oat milk", "Food", 11.30),
    ("Bagels and cream cheese", "Food", 8.90),
    ("Cooking oil and spices", "Food", 16.40),
    ("Canned goods restock", "Food", 21.00),
    ("Birthday cake", "Food", 35.00),
    ("BBQ supplies", "Food", 29.50),
    ("Smoothie ingredients", "Food", 18.20),
    ("Deli meat and cheese", "Food", 14.75),
    ("Bottled water case", "Food", 6.99),
    ("Uber to work", "Transport", 18.50),
    ("Uber to airport", "Transport", 35.00),
    ("Lyft to downtown", "Transport", 14.20),
    ("Gas station fill-up", "Transport", 52.30),
    ("Gas top-off", "Transport", 28.40),
    ("Monthly bus pass", "Transport", 65.00),
    ("Subway fare reload", "Transport", 40.00),
    ("Parking garage downtown", "Transport", 22.00),
    ("Parking meter", "Transport", 4.50),
    ("Oil change", "Transport", 45.00),
    ("Car wash", "Transport", 15.00),
    ("Tire rotation", "Transport", 30.00),
    ("Toll road fees", "Transport", 8.75),
    ("Lyft to friend's house", "Transport", 12.00),
    ("Uber Eats delivery fee", "Transport", 5.99),
    ("Bike tire repair", "Transport", 20.00),
    ("Train ticket", "Transport", 25.00),
    ("Airport parking", "Transport", 48.00),
    ("Car insurance monthly", "Transport", 120.00),
    ("Windshield wiper fluid", "Transport", 7.50),
    ("Rent payment", "Housing", 1200.00),
    ("Rent payment", "Housing", 1200.00),
    ("Rent payment", "Housing", 1200.00),
    ("Rent payment", "Housing", 1200.00),
    ("Rent payment", "Housing", 1200.00),
    ("Renters insurance", "Housing", 25.00),
    ("New bed sheets", "Housing", 45.00),
    ("Bathroom towels", "Housing", 30.00),
    ("Kitchen sponges and soap", "Housing", 8.50),
    ("Light bulbs", "Housing", 12.00),
    ("Air freshener", "Housing", 6.50),
    ("Shower curtain", "Housing", 18.00),
    ("Trash bags", "Housing", 9.99),
    ("Laundry detergent", "Housing", 14.50),
    ("Dish soap and hand soap", "Housing", 11.00),
    ("Vacuum cleaner bags", "Housing", 15.00),
    ("Door mat", "Housing", 20.00),
    ("Shelf organizer", "Housing", 25.00),
    ("Smoke detector batteries", "Housing", 8.00),
    ("Plunger", "Housing", 10.00),
    ("Netflix subscription", "Entertainment", 15.99),
    ("Spotify premium", "Entertainment", 10.99),
    ("Movie tickets", "Entertainment", 28.00),
    ("Concert tickets", "Entertainment", 75.00),
    ("Bowling night", "Entertainment", 22.00),
    ("Video game purchase", "Entertainment", 59.99),
    ("Board game", "Entertainment", 34.00),
    ("Streaming service annual", "Entertainment", 12.99),
    ("Escape room with friends", "Entertainment", 35.00),
    ("Mini golf", "Entertainment", 16.00),
    ("Arcade tokens", "Entertainment", 20.00),
    ("Museum admission", "Entertainment", 18.00),
    ("Zoo tickets", "Entertainment", 24.00),
    ("Book purchase", "Entertainment", 14.99),
    ("Magazine subscription", "Entertainment", 9.99),
    ("Comedy show tickets", "Entertainment", 40.00),
    ("Karaoke night", "Entertainment", 25.00),
    ("Puzzle set", "Entertainment", 19.00),
    ("Art supplies for hobby", "Entertainment", 32.00),
    ("Kindle book", "Entertainment", 11.99),
    ("New running shoes", "Shopping", 89.99),
    ("Winter jacket", "Shopping", 120.00),
    ("T-shirts pack", "Shopping", 35.00),
    ("Jeans", "Shopping", 55.00),
    ("Sunglasses", "Shopping", 25.00),
    ("Backpack", "Shopping", 45.00),
    ("Phone case", "Shopping", 15.00),
    ("USB-C cable", "Shopping", 12.00),
    ("Headphones", "Shopping", 49.99),
    ("Desk lamp", "Shopping", 28.00),
    ("Water bottle", "Shopping", 22.00),
    ("Wallet", "Shopping", 30.00),
    ("Belt", "Shopping", 20.00),
    ("Socks pack", "Shopping", 14.00),
    ("Underwear pack", "Shopping", 18.00),
    ("Face wash", "Shopping", 9.50),
    ("Shampoo and conditioner", "Shopping", 16.00),
    ("Deodorant", "Shopping", 7.50),
    ("Toothpaste and floss", "Shopping", 8.00),
    ("Razor blades", "Shopping", 22.00),
    ("Birthday gift for friend", "Shopping", 40.00),
    ("Gym membership monthly", "Health", 45.00),
    ("Gym membership monthly", "Health", 45.00),
    ("Gym membership monthly", "Health", 45.00),
    ("Gym membership monthly", "Health", 45.00),
    ("Doctor copay", "Health", 30.00),
    ("Dentist cleaning", "Health", 50.00),
    ("Prescription medication", "Health", 15.00),
    ("Vitamins and supplements", "Health", 28.00),
    ("Eye exam", "Health", 40.00),
    ("Contact lenses", "Health", 60.00),
    ("First aid kit restock", "Health", 18.00),
    ("Allergy medicine", "Health", 12.00),
    ("Sunscreen", "Health", 10.00),
    ("Pain relievers", "Health", 8.50),
    ("Cold medicine", "Health", 11.00),
    ("Bandages and antiseptic", "Health", 7.00),
    ("Protein powder", "Health", 35.00),
    ("Yoga mat", "Health", 25.00),
    ("Resistance bands", "Health", 15.00),
    ("Sports drink mix", "Health", 9.00),
    ("Electric bill", "Utilities", 85.00),
    ("Electric bill", "Utilities", 92.00),
    ("Electric bill", "Utilities", 78.00),
    ("Electric bill", "Utilities", 88.00),
    ("Water bill", "Utilities", 35.00),
    ("Water bill", "Utilities", 38.00),
    ("Water bill", "Utilities", 33.00),
    ("Internet bill", "Utilities", 60.00),
    ("Internet bill", "Utilities", 60.00),
    ("Internet bill", "Utilities", 60.00),
    ("Internet bill", "Utilities", 60.00),
    ("Phone bill", "Utilities", 45.00),
    ("Phone bill", "Utilities", 45.00),
    ("Phone bill", "Utilities", 45.00),
    ("Phone bill", "Utilities", 45.00),
    ("Gas bill", "Utilities", 40.00),
    ("Gas bill", "Utilities", 55.00),
    ("Gas bill", "Utilities", 35.00),
    ("Cloud storage subscription", "Utilities", 2.99),
    ("Domain name renewal", "Utilities", 12.00),
    ("ATM withdrawal", "Other", 60.00),
    ("ATM withdrawal", "Other", 40.00),
    ("Laundromat", "Other", 8.00),
    ("Dry cleaning", "Other", 25.00),
    ("Haircut", "Other", 30.00),
    ("Haircut", "Other", 30.00),
    ("Tip for barber", "Other", 5.00),
    ("Charity donation", "Other", 20.00),
    ("Late fee on credit card", "Other", 35.00),
    ("Postage stamps", "Other", 12.00),
    ("Shipping a package", "Other", 9.50),
    ("Key copy", "Other", 5.00),
    ("Pet food", "Other", 28.00),
    ("Pet treats", "Other", 8.00),
    ("Vet checkup", "Other", 65.00),
    ("Storage unit monthly", "Other", 50.00),
    ("Car registration renewal", "Other", 85.00),
    ("Passport photo", "Other", 15.00),
    ("Notary fee", "Other", 10.00),
    ("Locksmith", "Other", 75.00),
    ("Umbrella", "Other", 12.00),
]


def load_dummy_data(count=100):
    today = date.today()
    start = today - timedelta(days=150)
    days_range = (today - start).days
    sample = random.sample(_DUMMY_EXPENSES, min(count, len(_DUMMY_EXPENSES)))
    for desc, cat, amt in sample:
        rand_date = start + timedelta(days=random.randint(0, days_range))
        _execute(
            "INSERT INTO transactions (amount, description, category, date) VALUES (?, ?, ?, ?)",
            (amt, desc, cat, rand_date.isoformat()),
        )
