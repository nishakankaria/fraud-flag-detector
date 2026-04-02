"""
run.py
------
Entry point for the Fraud Flag Detector.

Generates a synthetic transaction dataset, runs all fraud detection rules,
prints a summary report, and saves flagged transactions to CSV.

Usage:
    python run.py
"""

from transaction_generator import generate_transactions
from fraud_detector import FraudDetector

OUTPUT_FILE = "flagged_transactions.csv"
N_TRANSACTIONS = 500


def print_report(summary: dict, output_path: str) -> None:
    width = 44
    print("\n" + "=" * width)
    print("  FRAUD FLAG DETECTOR — SUMMARY REPORT")
    print("=" * width)

    print(f"{'Total transactions analysed':<30}: {summary['total_transactions']}")
    print(
        f"{'Flagged as suspicious':<30}: "
        f"{summary['flagged_count']}  "
        f"({summary['flag_rate']:.1%})"
    )

    print(f"\n{'Flags by rule':}")
    for rule, count in sorted(summary["rule_counts"].items(), key=lambda x: -x[1]):
        print(f"  {rule:<22}: {count}")

    print(f"\n{'Top flagged merchants':}")
    for merchant, count in summary["top_merchants"].items():
        print(f"  {merchant:<28}: {count} flags")

    print(f"\nFlagged transactions saved to: {output_path}")
    print("=" * width + "\n")


def main():
    print(f"Generating {N_TRANSACTIONS} synthetic transactions…")
    transactions = generate_transactions(N_TRANSACTIONS)

    print("Running fraud detection rules…")
    detector = FraudDetector()
    flagged = detector.run(transactions)
    summary = detector.summary(transactions, flagged)

    print_report(summary, OUTPUT_FILE)

    if not flagged.empty:
        flagged.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
