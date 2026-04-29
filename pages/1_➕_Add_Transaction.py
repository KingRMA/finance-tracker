import random
import streamlit as st
from datetime import date as date_type, timedelta
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

st.divider()

DUMMY_EXPENSES = [
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

if st.button("Load Dummy Data (100 random entries)"):
    today = date_type.today()
    start = today - timedelta(days=150)

    sample = random.sample(DUMMY_EXPENSES, 100)
    for desc, cat, amt in sample:
        rand_date = start + timedelta(days=random.randint(0, 150))
        db.add_transaction(amt, desc, cat, rand_date.isoformat())

    st.success("Loaded 100 random transactions from the last 5 months.")
    st.rerun()
