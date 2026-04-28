# Ramy's Finance Tracker

A Streamlit web app for tracking personal spending, with AI-powered insights and data-driven forecasting.

## Features

- **Add transactions** with description, amount, category, and date
- **Search, filter, and sort** your transaction history
- **Edit and delete** entries via modal dialogs
- **AI spending insight** — after adding a transaction, Groq (LLaMA 3.1) analyzes it against your 30-day history and returns a risk level, reason, and suggested action
- **Dashboard** — category donut chart, monthly trend line, stacked monthly breakdown by category, and a daily spending forecast with confidence band
- Input validation (positive amounts, non-empty descriptions, no future dates)

## Tech Stack

| Layer          | Choice                          |
|----------------|---------------------------------|
| Frontend       | Streamlit                       |
| Language       | Python 3.10+                    |
| Database       | MySQL via SQLAlchemy            |
| AI             | Groq Cloud API (LLaMA 3.1-8B)  |
| Charts         | Plotly                          |
| Data wrangling | pandas, numpy                   |

## Project Structure

```
Home.py                        # Landing page
db.py                          # Database connection, CRUD, validation
ai.py                          # Groq API call for spending insights
pages/
  1_➕_Add_Transaction.py       # Transaction input form + AI insight
  2_📋_Transactions.py         # Searchable, filterable transaction list
  3_📊_Dashboard.py            # Charts, trends, and forecast
requirements.txt
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure database

Create a MySQL database, then add connection details to `.streamlit/secrets.toml`:

```toml
[connections.mysql]
dialect = "mysql"
host = "localhost"
port = 3306
database = "finance_tracker"
username = "your_user"
password = "your_password"
```

### 3. Configure AI (optional)

Add your Groq API key to `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "gsk_..."
```

The app works without this — AI insights will show an error message and the rest of the app functions normally.

### 4. Run

```bash
streamlit run Home.py
```

## AI Usage

The AI feature uses Groq's free API tier with the LLaMA 3.1-8B model. When a transaction is added, the app sends the transaction details along with a 30-day spending summary to the model. It returns:

- **Insight** — a 1-2 sentence assessment
- **Risk level** — high / medium / low, displayed with color coding
- **Reason** — why the risk level was assigned
- **Suggested action** — a concrete next step

The AI call is cached for one hour to avoid redundant API calls. If the API is unreachable, the transaction still saves and the UI shows a graceful error.

## Data Science Features

The dashboard includes four visualizations built with Plotly and pandas:

1. **Category donut chart** — total spending per category across all time
2. **Monthly trend line** — total spending per month to spot seasonal patterns
3. **Stacked bar chart** — monthly spending broken down by category to see where money goes over time
4. **Daily forecast with confidence band** — linear trend projection using `numpy.polyfit`, with a widening confidence interval (±1 SD, scaled by prediction distance) to communicate uncertainty honestly

The forecast uses simple linear regression on daily spend totals. The confidence band widens for dates further in the future, reflecting that predictions become less certain over time.
