# 🔍 Fraud Flag Detector

A lightweight Python tool that applies rule-based heuristics to flag potentially fraudulent transactions in a dataset.

> Built to explore how simple, interpretable rules can surface suspicious payment patterns — before reaching for ML.

---

## 💡 Why Rule-Based?

Machine learning fraud models are powerful, but they're often black boxes. In regulated financial services, you need to be able to *explain* why a transaction was flagged — to compliance teams, regulators, and customers.

Rule-based systems aren't the final answer, but they're:
- Auditable — every flag has a clear reason
- Fast to deploy — no training data needed
- A strong baseline before layering in ML

This project implements five common fraud heuristics and produces a clear, human-readable report.

---

## 🚩 Detection Rules

| Rule | Description |
|------|-------------|
| **High Value** | Transaction amount exceeds £1,000 |
| **Velocity** | 3+ transactions from same account within 10 minutes |
| **Late Night** | Transaction between 01:00–04:00 (higher fraud risk window) |
| **Round Amount** | Suspiciously round number (e.g. £500.00, £1000.00) — common in testing stolen cards |
| **Foreign + High Value** | Transaction abroad AND over £300 |

Each flagged transaction is tagged with *which rules triggered*, so every flag is explainable.

---

## 🚀 Getting Started

```bash
# Clone
git clone https://github.com/nishakankaria/fraud-flag-detector.git
cd fraud-flag-detector

# Install dependencies
pip install -r requirements.txt

# Generate sample data and run the detector
python run.py
```

You'll see a summary in the terminal and a `flagged_transactions.csv` saved to the project folder.

---

## 📂 Project Structure

```
fraud-flag-detector/
├── run.py                  # Entry point — generates data, runs detector, prints report
├── fraud_detector.py       # Core rule engine
├── transaction_generator.py # Synthetic transaction data generator
├── requirements.txt
├── tests/
│   └── test_fraud_detector.py
└── README.md
```

---

## 📊 Sample Output

```
========================================
  FRAUD FLAG DETECTOR — SUMMARY REPORT
========================================
Total transactions analysed : 500
Flagged as suspicious       : 87  (17.4%)

Flags by rule:
  high_value          : 42
  velocity            : 31
  late_night          : 28
  round_amount        : 38
  foreign_high_value  : 19

Top flagged merchants:
  Electronics Store   : 18 flags
  International Hotel : 14 flags
  ATM Withdrawal      : 12 flags

Flagged transactions saved to: flagged_transactions.csv
========================================
```

---

## 🔮 Potential Extensions

- [ ] Add ML scoring layer (logistic regression or XGBoost) on top of rule flags
- [ ] Build a simple Streamlit UI to upload a CSV and view flags interactively
- [ ] Add a confidence score — weight rules by historical precision
- [ ] Integrate with an API to flag transactions in real time

---

## 📜 Licence

MIT — use freely.
