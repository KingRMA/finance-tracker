# Ramy's Finance Tracker

A Streamlit web app for tracking personal spending, with AI-powered insights and data-driven forecasting.

## Features

- **Add transactions** with description, amount, category, and date
- **Search, filter, and sort** your transaction history
- **Edit and delete** entries via modal dialogs
- **AI spending insight** — after adding a transaction, Groq (LLaMA 3.1) analyzes it against your 30-day history and returns a risk level, reason, and suggested action
- **Dashboard** — category donut chart, monthly trend line, stacked monthly breakdown by category, and a daily spending forecast with confidence band
- **Load dummy data** — one-click button to populate 100 realistic transactions for demo purposes
- Input validation (positive amounts, non-empty descriptions, no future dates)

## Tech Stack

| Layer          | Choice                                |
|----------------|---------------------------------------|
| Frontend       | Streamlit                             |
| Language       | Python 3.10+                          |
| Database       | SQLite (zero config, file-based)      |
| AI             | Groq Cloud API (LLaMA 3.1-8B)        |
| Charts         | Plotly                                |
| Data wrangling | pandas, numpy                         |
| Forecasting    | scikit-learn (LinearRegression)       |

## Project Structure

```
Home.py                        # Landing page
db.py                          # Database CRUD, validation, dummy data
ai.py                          # Groq API call for spending insights
pages/
  1_➕_Add_Transaction.py       # Transaction input form + AI insight + demo data button
  2_📋_Transactions.py         # Searchable, filterable transaction list with edit/delete
  3_📊_Dashboard.py            # Charts, trends, and forecast with confidence band
requirements.txt
.streamlit/
  secrets.toml.example         # Template for user secrets
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AI (optional)

Copy the example secrets file:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Add your Groq API key to `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

The app works without this — AI insights will be unavailable but everything else functions normally. Get a free key at [console.groq.com](https://console.groq.com).

### 3. Run

```bash
streamlit run Home.py
```

The SQLite database (`finance_tracker.db`) is created automatically on first run. No database server needed.

### 4. Load demo data (optional)

Click the **"Load Dummy Data"** button on the Add Transaction page to instantly populate 100 realistic transactions spanning the last 5 months. This fills the dashboard with charts immediately.

## AI Usage

The AI feature uses Groq's free API tier with the LLaMA 3.1-8B model. When a transaction is added, the app sends the transaction details along with a 30-day spending summary to the model. It returns:

- **Insight** — a 1-2 sentence assessment
- **Risk level** — high / medium / low, displayed with color coding
- **Reason** — why the risk level was assigned
- **Suggested action** — a concrete next step

The AI call is cached for one hour to avoid redundant API calls. If the API is unreachable, the transaction still saves and the UI shows a graceful fallback message.

## Data Science Features

The dashboard includes four visualizations built with Plotly and scikit-learn:

1. **Category donut chart** — total spending per category across all time
2. **Monthly trend line** — total spending per month to spot seasonal patterns
3. **Stacked bar chart** — monthly spending broken down by category to see where money goes over time
4. **Daily forecast with confidence band** — linear regression projection (sklearn `LinearRegression`), with a widening confidence interval (±1 SD scaled by `sqrt(distance)`) to communicate uncertainty honestly

The forecast model fits on daily spend totals and projects forward by a user-configurable number of days. The confidence band widens for dates further in the future, reflecting that predictions become less certain over time.
