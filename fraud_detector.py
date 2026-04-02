"""
fraud_detector.py
-----------------
Rule-based fraud detection engine.

Each rule is a standalone function that takes the transactions DataFrame
and returns the set of transaction IDs that triggered that rule.
The FraudDetector class runs all rules and assembles a results report.

Design principle: every flag must be explainable. Each flagged transaction
records exactly which rules triggered, so a human can review and act on it.
"""

import pandas as pd
from datetime import timedelta
from collections import Counter


# ------------------------------------------------------------------
# Individual rules
# ------------------------------------------------------------------

def rule_high_value(
    transactions: pd.DataFrame, threshold: float = 1000.0
) -> set:
    """
    Flag transactions where the amount exceeds the threshold.
    High-value transactions warrant additional scrutiny.
    """
    flagged = transactions[transactions["amount"] > threshold]
    return set(flagged["transaction_id"])


def rule_velocity(
    transactions: pd.DataFrame, window_minutes: int = 10, min_count: int = 3
) -> set:
    """
    Flag accounts that have min_count or more transactions within window_minutes.

    Rapid successive transactions from a single account are a common
    indicator of card testing or account takeover.
    """
    flagged_ids = set()
    df = transactions.sort_values(["account_id", "timestamp"])

    for account, group in df.groupby("account_id"):
        times = group["timestamp"].tolist()
        ids = group["transaction_id"].tolist()

        for i in range(len(times)):
            window_end = times[i] + timedelta(minutes=window_minutes)
            # Count how many transactions fall within the window starting at i
            count = sum(1 for t in times[i:] if t <= window_end)
            if count >= min_count:
                # Flag all transactions in this window
                for j in range(i, len(times)):
                    if times[j] <= window_end:
                        flagged_ids.add(ids[j])

    return flagged_ids


def rule_late_night(
    transactions: pd.DataFrame, start_hour: int = 1, end_hour: int = 4
) -> set:
    """
    Flag transactions that occur between start_hour and end_hour (24h clock).

    The 01:00–04:00 window has historically higher fraud rates in card-present
    and card-not-present environments.
    """
    hour = transactions["timestamp"].dt.hour
    flagged = transactions[(hour >= start_hour) & (hour < end_hour)]
    return set(flagged["transaction_id"])


def rule_round_amount(transactions: pd.DataFrame) -> set:
    """
    Flag transactions with suspiciously round amounts (multiples of £50).

    Fraudsters often test stolen card details with round numbers before
    making larger purchases. Round amounts can also indicate ATM-style
    cash extraction patterns.
    """
    flagged = transactions[transactions["amount"] % 50 == 0]
    return set(flagged["transaction_id"])


def rule_foreign_high_value(
    transactions: pd.DataFrame, threshold: float = 300.0
) -> set:
    """
    Flag foreign transactions above the threshold.

    International transactions combined with high value are a common
    fraud pattern, particularly following account compromise.
    """
    flagged = transactions[
        (transactions["location"] == "foreign") & (transactions["amount"] > threshold)
    ]
    return set(flagged["transaction_id"])


# ------------------------------------------------------------------
# Detector class
# ------------------------------------------------------------------

class FraudDetector:
    """
    Runs all fraud rules against a transactions DataFrame and
    produces a flagged results DataFrame with explanations.
    """

    RULES = {
        "high_value": rule_high_value,
        "velocity": rule_velocity,
        "late_night": rule_late_night,
        "round_amount": rule_round_amount,
        "foreign_high_value": rule_foreign_high_value,
    }

    def run(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all rules. Returns a DataFrame of flagged transactions
        with a 'triggered_rules' column listing which rules fired.
        """
        # Collect results per rule
        rule_results: dict[str, set] = {}
        for rule_name, rule_fn in self.RULES.items():
            rule_results[rule_name] = rule_fn(transactions)

        # Build per-transaction flag list
        all_flagged_ids = set().union(*rule_results.values())

        rows = []
        for txn_id in all_flagged_ids:
            triggered = [
                rule for rule, ids in rule_results.items() if txn_id in ids
            ]
            rows.append({
                "transaction_id": txn_id,
                "triggered_rules": ", ".join(triggered),
                "rule_count": len(triggered),
            })

        flags_df = pd.DataFrame(rows)

        if flags_df.empty:
            return pd.DataFrame()

        result = transactions.merge(flags_df, on="transaction_id", how="inner")
        return result.sort_values("rule_count", ascending=False).reset_index(drop=True)

    def summary(self, transactions: pd.DataFrame, flagged: pd.DataFrame) -> dict:
        """
        Compute summary statistics for the report.
        """
        total = len(transactions)
        n_flagged = len(flagged)

        # Count per rule
        rule_counts: Counter = Counter()
        if not flagged.empty:
            for rules_str in flagged["triggered_rules"]:
                for r in rules_str.split(", "):
                    rule_counts[r] += 1

        # Top flagged merchants
        top_merchants: dict = {}
        if not flagged.empty:
            top_merchants = (
                flagged["merchant"]
                .value_counts()
                .head(5)
                .to_dict()
            )

        return {
            "total_transactions": total,
            "flagged_count": n_flagged,
            "flag_rate": n_flagged / total if total > 0 else 0,
            "rule_counts": dict(rule_counts),
            "top_merchants": top_merchants,
        }
