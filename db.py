
from datetime import date

import streamlit as st
from sqlalchemy import text

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


@st.cache_resource
def get_connection():
	return st.connection("mysql", type="sql")


def _query_df(sql, params=None):
	return get_connection().query(sql, params=params or {}, ttl=0)


def _execute(sql, params=None):
	conn = get_connection()
	with conn.session as session:
		result = session.execute(text(sql), params or {})
		session.commit()
		return result


def init_db():
	create_table_sql = """
	CREATE TABLE IF NOT EXISTS transactions (
		id INT AUTO_INCREMENT PRIMARY KEY,
		amount DECIMAL(10, 2) NOT NULL,
		description TEXT NOT NULL,
		category VARCHAR(50) NOT NULL,
		date DATE NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)
	"""
	_execute(create_table_sql)


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
	result = _execute(
		"""
		INSERT INTO transactions (amount, description, category, date)
		VALUES (:amount, :description, :category, :tx_date)
		""",
		{
			"amount": float(amount),
			"description": description.strip(),
			"category": category,
			"tx_date": tx_date,
		},
	)
	return int(result.lastrowid)


def get_transaction(transaction_id):
	transaction_id = int(transaction_id)
	result = _query_df(
		"""
		SELECT id, amount, description, category, date, created_at
		FROM transactions
		WHERE id = :transaction_id
		""",
		{"transaction_id": transaction_id},
	)

	if result.empty:
		return None
	return result.iloc[0].to_dict()


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

	query = """
		SELECT id, amount, description, category, date, created_at
		FROM transactions
		WHERE 1=1
	"""
	params = {}

	if start_date:
		query += " AND date >= :start_date"
		params["start_date"] = start_date

	if end_date:
		query += " AND date <= :end_date"
		params["end_date"] = end_date

	if category:
		query += " AND category = :category"
		params["category"] = category

	if search:
		query += " AND LOWER(description) LIKE :search"
		params["search"] = f"%{search.strip().lower()}%"

	query += f" ORDER BY {sort_by} {sort_direction}, id DESC"

	df = _query_df(query, params)
	if "date" in df.columns:
		df["date"] = df["date"].astype(str).str[:10]
	return df.to_dict("records")


def update_transaction(
	transaction_id,
	amount,
	description,
	category,
	tx_date,
):
	_validate_transaction(amount, description, category, tx_date)
	result = _execute(
		"""
		UPDATE transactions
		SET amount = :amount,
			description = :description,
			category = :category,
			date = :tx_date
		WHERE id = :transaction_id
		""",
		{
			"amount": float(amount),
			"description": description.strip(),
			"category": category,
			"tx_date": tx_date,
			"transaction_id": int(transaction_id),
		},
	)
	return result.rowcount > 0


def delete_transaction(transaction_id):
	result = _execute(
		"DELETE FROM transactions WHERE id = :transaction_id",
		{"transaction_id": int(transaction_id)},
	)
	return result.rowcount > 0


def get_total_spend_all_time():
	result = _query_df("SELECT COALESCE(SUM(amount), 0) AS total FROM transactions")
	if result.empty:
		return 0.0
	return float(result.iloc[0]["total"])


def get_total_spend_month(year, month):
	ym = f"{year:04d}-{month:02d}"
	result = _query_df(
		"""
		SELECT COALESCE(SUM(amount), 0) AS total
		FROM transactions
		WHERE DATE_FORMAT(date, '%Y-%m') = :ym
		""",
		{"ym": ym},
	)
	if result.empty:
		return 0.0
	return float(result.iloc[0]["total"])
