import json
import streamlit as st
from datetime import datetime, timedelta
import db


@st.cache_data(ttl=3600)
def get_spending_insight(amount, description, category, tx_date):
    try:
        from groq import Groq

        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        history = _get_history_summary()

        prompt = (
            f"You are a personal finance advisor. Analyze this transaction and provide insight.\n"
            f"Write in a direct, friendly tone using 'you' and 'your'. Keep it to 1-2 sentences.\n\n"
            f"Transaction: ${amount} for {description} ({category}) on {tx_date}\n\n"
            f"30-Day Context:\n"
            f"- Total spent: ${history['total']}\n"
            f"- Daily average: ${history['daily_avg']}\n"
            f"- Top categories: {history['categories']}\n\n"
            f"Respond in JSON with keys: insight, risk_level (high/medium/low), reason, suggested_action."
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a personal finance advisor. Respond only in valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=220,
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "insight": "AI insight unavailable right now.",
            "risk_level": "unknown",
            "reason": str(e),
            "suggested_action": "",
        }


def _get_history_summary():
    today = datetime.now().date()
    start = (today - timedelta(days=30)).isoformat()
    txs = db.list_transactions(start_date=start, end_date=today.isoformat())

    total = sum(float(t["amount"]) for t in txs)
    categories = {}
    for t in txs:
        categories[t["category"]] = categories.get(t["category"], 0) + float(t["amount"])

    return {
        "total": round(total, 2),
        "daily_avg": round(total / 30, 2),
        "categories": categories,
    }
