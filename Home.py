import streamlit as st

st.set_page_config(
    page_title="Ramy's Finance Tracker",
    page_icon="💰",
    layout="wide",
)

st.title("Ramy's Finance Tracker")
st.caption("Track spending, review your transactions, and spot trends in one simple place.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("➕ Add Transaction")
    st.write("Log new expenses with a clean form and instant AI insight.")

with col2:
    st.subheader("📋 Transactions")
    st.write("Search, sort, edit, and delete your records from one table.")

with col3:
    st.subheader("📊 Dashboard")
    st.write("Spending trends, category breakdowns, and forecasted totals.")

st.divider()

st.subheader("Get started")
st.write(
    "Use the **sidebar** to navigate between pages. "
    "Add a transaction, review your entries, then check the dashboard for trends and forecasts."
)
