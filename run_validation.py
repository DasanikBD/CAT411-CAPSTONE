"""
run_validation.py
=================
Entry point for CAT411 Vulnerability Validation (Anik Das — T1a / T1b)

Sprint 1 (current): Runs with SYNTHETIC data to verify the framework.
Sprint 2 (swap):    Change OBSERVED_CSV and PREDICTED_CSV to real files.

Usage:
    python run_validation.py                     # synthetic data (Sprint 1)
    python run_validation.py --real              # real data (Sprint 2)
    python run_validation.py --observed path.csv --predicted path2.csv
"""

import sys
import os
import argparse

# Make sure src/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from generate_synthetic_data import generate_synthetic_data
from validation import run_validation

# ── Default file paths ─────────────────────────────────────────────────
SYNTHETIC_OBS   = "data/synthetic_observed.csv"
SYNTHETIC_PRED  = "data/synthetic_predicted.csv"

# ── Sprint 2: swap these paths when Sirisha's data is ready ────────────
REAL_OBS        = "data/northridge_observed.csv"          # Sirisha's output
REAL_PRED       = "output/analysis/bridge_damage_results.csv"  # pipeline output

OUTPUT_DIR      = "output/validation"


def main():
    parser = argparse.ArgumentParser(description="CAT411 Validation Framework")
    parser.add_argument("--real",      action="store_true",
                        help="Use real Northridge data instead of synthetic")
    parser.add_argument("--observed",  default=None,
                        help="Path to observed damage CSV")
    parser.add_argument("--predicted", default=None,
                        help="Path to predicted damage CSV")
    args = parser.parse_args()

    # ── Resolve paths ──────────────────────────────────────────────────
    if args.observed and args.predicted:
        obs_csv  = args.observed
        pred_csv = args.predicted
        print("[mode] Custom CSV paths")
    elif args.real:
        obs_csv  = REAL_OBS
        pred_csv = REAL_PRED
        print("[mode] REAL Northridge data (Sprint 2)")
    else:
        # Sprint 1: generate fresh synthetic data each run
        print("[mode] SYNTHETIC data (Sprint 1 — framework test)")
        obs_df, pred_df = generate_synthetic_data()
        os.makedirs("data", exist_ok=True)
        obs_df.to_csv(SYNTHETIC_OBS,  index=False)
        pred_df.to_csv(SYNTHETIC_PRED, index=False)
        obs_csv  = SYNTHETIC_OBS
        pred_csv = SYNTHETIC_PRED

    # ── Run validation ─────────────────────────────────────────────────
    results = run_validation(
        observed_csv  = obs_csv,
        predicted_csv = pred_csv,
        output_dir    = OUTPUT_DIR,
    )

    # ── Quick sanity check ─────────────────────────────────────────────
    acceptance = results["acceptance"]
    passes = acceptance["Pass"].sum()
    total  = len(acceptance)
    print(f"\n[result] {passes}/{total} acceptance criteria passed.")

    # Return non-zero exit code if critical checks fail
    critical = acceptance[acceptance["Metric"].isin(
        ["Overall Accuracy", "Mean Residual (|bias|)", "RMSE (ordinal)"]
    )]
    if not critical["Pass"].all():
        print("[warn] Some critical acceptance criteria FAILED.")
        sys.exit(1)
    else:
        print("[ok]  All critical acceptance criteria PASSED.")


if __name__ == "__main__":
    main()
