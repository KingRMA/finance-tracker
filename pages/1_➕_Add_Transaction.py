import streamlit as st
from datetime import date as date_type
import ai
import db

st.set_page_config(page_title="Add Transaction", page_icon="➕", layout="wide")

db.init_db()

st.title("Add Transaction")

with st.form("transaction_form"):
    description = st.text_input("Description", placeholder="e.g., Grocery shopping")
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
    category = st.selectbox("Category", db.CATEGORIES)
    transaction_date = st.date_input("Date", value=date_type.today())
    submitted = st.form_submit_button("Add Transaction")

if submitted:
    try:
        date_str = transaction_date.isoformat()
        tx_id = db.add_transaction(amount, description, category, date_str)

        st.success(f"Transaction added (ID: {tx_id})")
        st.write(f"**{description}** | ${amount:.2f} | {category} | {transaction_date}")

        with st.spinner("Getting AI insight..."):
            insight = ai.get_spending_insight(amount, description, category, date_str)

        risk = insight.get("risk_level", "unknown")
        msg = insight.get("insight", "")
        if risk == "high":
            st.error(msg)
        elif risk == "medium":
            st.warning(msg)
        else:
            st.info(msg)

        if insight.get("reason"):
            st.caption(f"**Why:** {insight['reason']}")
        if insight.get("suggested_action"):
            st.caption(f"**Suggested:** {insight['suggested_action']}")

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Database error: {e}")
