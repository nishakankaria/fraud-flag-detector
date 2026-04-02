"""
transaction_generator.py
------------------------
Generates a synthetic dataset of payment transactions for testing the fraud detector.

All data is entirely fictional. No real customer or financial data is used.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

MERCHANTS = [
    ("Supermarket", "domestic", 15, 120),
    ("Coffee Shop", "domestic", 2, 15),
    ("Electronics Store", "domestic", 50, 1500),
    ("Clothing Retailer", "domestic", 20, 200),
    ("ATM Withdrawal", "domestic", 50, 500),
    ("Restaurant", "domestic", 10, 80),
    ("Petrol Station", "domestic", 30, 90),
    ("Pharmacy", "domestic", 5, 60),
    ("International Hotel", "foreign", 80, 600),
    ("Airport Duty Free", "foreign", 20, 300),
    ("Online Marketplace", "domestic", 5, 800),
    ("Subscription Service", "domestic", 5, 30),
]


def _random_timestamp(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_transactions(n: int = 500) -> pd.DataFrame:
    """
    Generate n synthetic payment transactions.

    Includes deliberate anomalies to give the detector something to find:
    - A cluster of rapid-fire transactions (velocity fraud simulation)
    - Some late-night high-value transactions
    - Round-number amounts
    """
    start = datetime(2024, 1, 1)
    end = datetime(2024, 6, 30)

    account_ids = [f"ACC_{i:04d}" for i in range(1, 51)]  # 50 accounts
    transactions = []

    for i in range(n):
        account = random.choice(account_ids)
        merchant_name, location, min_amt, max_amt = random.choice(MERCHANTS)
        amount = round(random.uniform(min_amt, max_amt), 2)
        timestamp = _random_timestamp(start, end)

        transactions.append({
            "transaction_id": f"TXN_{i+1:05d}",
            "account_id": account,
            "timestamp": timestamp,
            "amount": amount,
            "merchant": merchant_name,
            "location": location,
            "currency": "GBP",
        })

    # Inject velocity cluster — 5 rapid transactions from one account
    burst_account = "ACC_0001"
    burst_time = datetime(2024, 3, 15, 14, 0, 0)
    for j in range(5):
        transactions.append({
            "transaction_id": f"TXN_BURST_{j+1:02d}",
            "account_id": burst_account,
            "timestamp": burst_time + timedelta(minutes=j * 2),
            "amount": round(random.uniform(50, 300), 2),
            "merchant": "Online Marketplace",
            "location": "domestic",
            "currency": "GBP",
        })

    # Inject round-amount transactions
    for k in range(8):
        transactions.append({
            "transaction_id": f"TXN_ROUND_{k+1:02d}",
            "account_id": random.choice(account_ids),
            "timestamp": _random_timestamp(start, end),
            "amount": random.choice([100.0, 200.0, 500.0, 1000.0]),
            "merchant": "ATM Withdrawal",
            "location": "domestic",
            "currency": "GBP",
        })

    df = pd.DataFrame(transactions)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate_transactions(500)
    print(f"Generated {len(df)} transactions")
    print(df.head())
