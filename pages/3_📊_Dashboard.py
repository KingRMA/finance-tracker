import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import db

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

db.init_db()

st.title("Dashboard")

# --- summary metrics ---
all_tx = db.list_transactions()
today = datetime.now()

total_all = db.get_total_spend_all_time()
total_month = db.get_total_spend_month(today.year, today.month)

prev = (today.replace(day=1) - timedelta(days=1))
total_prev_month = db.get_total_spend_month(prev.year, prev.month)

month_delta = total_month - total_prev_month if total_prev_month else None

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("All-Time Spending", f"${total_all:,.2f}")
with col2:
    st.metric(
        "This Month",
        f"${total_month:,.2f}",
        delta=f"${month_delta:+,.2f}" if month_delta is not None else None,
        delta_color="inverse",
    )
with col3:
    st.metric("Total Transactions", len(all_tx))

st.divider()

if not all_tx:
    st.info("No transactions yet. Add one to see your dashboard.")
    st.stop()

# --- build a dataframe once, reuse everywhere ---
df = pd.DataFrame(all_tx)
df["amount"] = df["amount"].astype(float)
df["date"] = pd.to_datetime(df["date"])
df["month"] = df["date"].dt.to_period("M")

# --- category donut chart ---
st.subheader("Spending by Category")

cat_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
pie_fig = go.Figure(
    data=[
        go.Pie(
            labels=cat_totals.index.tolist(),
            values=cat_totals.values.tolist(),
            hole=0.4,
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<extra></extra>",
        )
    ]
)
pie_fig.update_layout(height=400, margin=dict(t=20, b=20))
st.plotly_chart(pie_fig, use_container_width=True)

# --- monthly trend line ---
st.subheader("Monthly Spending Trend")

monthly = df.groupby("month")["amount"].sum().sort_index()
month_labels = [str(m) for m in monthly.index]
month_values = monthly.values.tolist()

trend_fig = go.Figure()
trend_fig.add_trace(
    go.Scatter(
        x=month_labels,
        y=month_values,
        mode="lines+markers",
        name="Monthly Total",
        line=dict(width=3),
        marker=dict(size=8),
    )
)
trend_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Total Spent ($)",
    hovermode="x unified",
    height=380,
    margin=dict(t=20, b=20),
)
st.plotly_chart(trend_fig, use_container_width=True)

# --- stacked bar chart: monthly by category ---
st.subheader("Monthly Spending by Category")

pivot = df.pivot_table(index="month", columns="category", values="amount", aggfunc="sum", fill_value=0)
pivot = pivot.sort_index()
pivot_labels = [str(m) for m in pivot.index]

stack_fig = go.Figure()
for cat in pivot.columns:
    stack_fig.add_trace(
        go.Bar(
            x=pivot_labels,
            y=pivot[cat].values.tolist(),
            name=cat,
            hovertemplate="<b>%{x}</b><br>" + cat + ": $%{y:,.2f}<extra></extra>",
        )
    )
stack_fig.update_layout(
    barmode="stack",
    xaxis_title="Month",
    yaxis_title="Amount ($)",
    hovermode="x unified",
    height=420,
    margin=dict(t=20, b=20),
)
st.plotly_chart(stack_fig, use_container_width=True)

# --- daily spending with forecast + confidence band ---
st.subheader("Daily Spending Forecast")

forecast_days = st.slider("Forecast days ahead", min_value=1, max_value=30, value=7)

daily = df.groupby(df["date"].dt.date)["amount"].sum().sort_index()
dates = list(daily.index)
amounts = daily.values.astype(float)

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=dates,
        y=amounts.tolist(),
        mode="lines+markers",
        name="Actual",
        line=dict(color="#1f77b4", width=3),
        marker=dict(size=6),
    )
)

if len(amounts) >= 2:
    x_idx = np.arange(len(amounts), dtype=float)
    coeffs = np.polyfit(x_idx, amounts, 1)
    residual_std = float(np.std(amounts - np.polyval(coeffs, x_idx)))

    future_idx = np.arange(len(amounts), len(amounts) + forecast_days, dtype=float)
    forecast_vals = np.polyval(coeffs, future_idx)
    forecast_vals = np.maximum(forecast_vals, 0.0)

    last_date = dates[-1]
    future_dates = [last_date + timedelta(days=i + 1) for i in range(forecast_days)]

    distance = np.arange(1, forecast_days + 1, dtype=float)
    band = residual_std * np.sqrt(distance)
    upper = np.maximum(forecast_vals + band, 0.0)
    lower = np.maximum(forecast_vals - band, 0.0)

    connect_dates = [last_date] + future_dates
    connect_forecast = [float(amounts[-1])] + forecast_vals.tolist()
    connect_upper = [float(amounts[-1])] + upper.tolist()
    connect_lower = [float(amounts[-1])] + lower.tolist()

    fig.add_trace(
        go.Scatter(
            x=connect_dates,
            y=connect_upper,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=connect_dates,
            y=connect_lower,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(255, 127, 14, 0.2)",
            name="Confidence Band",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=connect_dates,
            y=connect_forecast,
            mode="lines+markers",
            name="Forecast",
            line=dict(color="#ff7f0e", width=3, dash="dash"),
            marker=dict(size=6),
        )
    )

    predicted_total = float(np.sum(forecast_vals))
    st.metric(
        f"Projected Spending (next {forecast_days} days)",
        f"${predicted_total:,.2f}",
    )
else:
    st.info("Need at least 2 days of data for a forecast.")

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Amount ($)",
    hovermode="x unified",
    height=420,
    margin=dict(t=20, b=20),
)
st.plotly_chart(fig, use_container_width=True)
