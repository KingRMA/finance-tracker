import streamlit as st
from datetime import date as date_type, timedelta
import db

st.set_page_config(page_title="Transactions", page_icon="📋", layout="wide")

db.init_db()

st.title("Transactions")

with st.sidebar:
    st.header("Filters")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date_type.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", value=date_type.today())

    category_filter = st.multiselect("Category", db.CATEGORIES, default=db.CATEGORIES)
    search_text = st.text_input("Search description", placeholder="e.g., pizza, uber")
    sort_by = st.selectbox("Sort by", ["date", "amount", "category"])
    sort_dir = st.radio("Direction", ["desc", "asc"])

all_rows = db.list_transactions(
    start_date=start_date.isoformat(),
    end_date=end_date.isoformat(),
    search=search_text if search_text else None,
    sort_by=sort_by,
    sort_direction=sort_dir,
)

if category_filter and set(category_filter) != set(db.CATEGORIES):
    allowed = set(category_filter)
    all_rows = [tx for tx in all_rows if tx["category"] in allowed]

st.subheader(f"{len(all_rows)} Transaction(s)")


@st.dialog("Confirm Delete", width="small")
def confirm_delete_dialog(tx_to_delete):
    st.write(f"Delete **{tx_to_delete['description']}**?")
    st.write(f"${tx_to_delete['amount']:.2f} | {tx_to_delete['category']}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes, delete", use_container_width=True):
            db.delete_transaction(st.session_state.delete_id)
            st.session_state.delete_id = None
            st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.delete_id = None
            st.rerun()


@st.dialog("Edit Transaction", width="large")
def edit_transaction_dialog(tx_to_edit):
    with st.form(f"edit_form_{tx_to_edit['id']}"):
        new_description = st.text_input("Description", value=tx_to_edit["description"])
        new_amount = st.number_input(
            "Amount ($)", value=float(tx_to_edit["amount"]), step=0.01, min_value=0.01
        )
        new_category = st.selectbox(
            "Category", db.CATEGORIES, index=db.CATEGORIES.index(tx_to_edit["category"])
        )
        new_date = st.date_input("Date", value=date_type.fromisoformat(str(tx_to_edit["date"])[:10]))

        if st.form_submit_button("Save"):
            try:
                success = db.update_transaction(
                    st.session_state.editing_id,
                    new_amount,
                    new_description,
                    new_category,
                    new_date.isoformat(),
                )
                if success:
                    st.session_state.editing_id = None
                    st.rerun()
                else:
                    st.error("Failed to update.")
            except ValueError as e:
                st.error(str(e))


st.divider()

if all_rows:
    for row in all_rows:
        col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 2])

        with col1:
            st.write(f"#{row['id']}")
        with col2:
            st.write(row["description"][:40])
        with col3:
            st.write(f"${row['amount']:.2f}")
        with col4:
            st.write(row["category"])
        with col5:
            st.write(row["date"])
        with col6:
            c_edit, c_del = st.columns(2)
            with c_edit:
                if st.button("Edit", key=f"edit_{row['id']}"):
                    st.session_state.editing_id = row["id"]
            with c_del:
                if st.button("Delete", key=f"del_{row['id']}"):
                    st.session_state.delete_id = row["id"]

    if "delete_id" in st.session_state and st.session_state.delete_id:
        tx = next((t for t in all_rows if t["id"] == st.session_state.delete_id), None)
        if tx:
            confirm_delete_dialog(tx)

    if "editing_id" in st.session_state and st.session_state.editing_id:
        tx = next((t for t in all_rows if t["id"] == st.session_state.editing_id), None)
        if tx:
            edit_transaction_dialog(tx)
else:
    st.info("No transactions found. Adjust your filters or add one first.")
