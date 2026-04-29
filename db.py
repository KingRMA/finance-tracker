
from datetime import date
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
