"""
generate_synthetic_data.py
==========================
Creates 50 synthetic bridges with random predicted + observed damage states
for testing src/validation.py before Sirisha's real CSV is available.

DATA-SWAP NOTE:
    When Sirisha delivers data/northridge_observed.csv (Sprint 2):
    1. Replace OBSERVED_CSV in run_validation() with the real file path.
    2. Replace PREDICTED_CSV with your pipeline output CSV.
    3. No other changes needed — validation.py schema is compatible.

Output files:
    data/synthetic_observed.csv
    data/synthetic_predicted.csv
"""

import numpy as np
import pandas as pd
import os

# ── Config ──────────────────────────────────────────────────────────────
SEED = 42
N_BRIDGES = 50

# Northridge-region bounding box (approximate)
LAT_RANGE  = (34.00, 34.40)
LON_RANGE  = (-118.70, -118.20)

# Realistic damage distribution for Northridge (Basoz 1998)
OBSERVED_PROBS = {
    "none":      0.827,
    "slight":    0.062,
    "moderate":  0.054,
    "extensive": 0.032,
    "complete":  0.025,
}

DAMAGE_STATES = ["none", "slight", "moderate", "extensive", "complete"]


def generate_synthetic_data(seed: int = SEED, n: int = N_BRIDGES) -> tuple:
    """
    Generate (observed_df, predicted_df) with realistic structure.

    The predicted states have intentional noise added so that the
    confusion matrix shows meaningful off-diagonal entries.
    """
    rng = np.random.default_rng(seed)

    # Bridge locations within Northridge bounding box
    lats = rng.uniform(*LAT_RANGE, n)
    lons = rng.uniform(*LON_RANGE, n)
    bridge_ids = [f"SYNTH-{i+1:04d}" for i in range(n)]

    # Observed damage — sample from Basoz 1998 distribution
    obs_probs = list(OBSERVED_PROBS.values())
    observed  = rng.choice(DAMAGE_STATES, size=n, p=obs_probs)

    # Predicted damage — introduce systematic bias:
    # 70% chance: correct; 20% chance: one state off; 10% chance: two states off
    ds_idx   = {ds: i for i, ds in enumerate(DAMAGE_STATES)}
    predicted = []
    for obs in observed:
        roll = rng.random()
        idx  = ds_idx[obs]
        if roll < 0.70:
            pred_idx = idx                                     # correct
        elif roll < 0.90:
            shift = rng.choice([-1, 1])
            pred_idx = np.clip(idx + shift, 0, 4)             # 1 off
        else:
            shift = rng.choice([-2, 2])
            pred_idx = np.clip(idx + shift, 0, 4)             # 2 off
        predicted.append(DAMAGE_STATES[pred_idx])

    # Synthetic Sa(1.0s) values (placeholder; real values from GMPE pipeline)
    sa_values = rng.lognormal(mean=np.log(0.3), sigma=0.6, size=n)

    observed_df = pd.DataFrame({
        "bridge_id":       bridge_ids,
        "latitude":        lats,
        "longitude":       lons,
        "observed_damage": observed,
    })

    predicted_df = pd.DataFrame({
        "bridge_id":        bridge_ids,
        "predicted_damage": predicted,
        "sa_predicted":     np.round(sa_values, 6),
    })

    return observed_df, predicted_df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    obs_df, pred_df = generate_synthetic_data()

    obs_path  = "data/synthetic_observed.csv"
    pred_path = "data/synthetic_predicted.csv"

    obs_df.to_csv(obs_path,  index=False)
    pred_df.to_csv(pred_path, index=False)

    print(f"Generated {len(obs_df)} synthetic bridges.")
    print(f"Observed  → {obs_path}")
    print(f"Predicted → {pred_path}")
    print("\nObserved distribution:")
    print(obs_df["observed_damage"].value_counts().to_string())
    print("\nPredicted distribution:")
    print(pred_df["predicted_damage"].value_counts().to_string())
