import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple
from ..utils.logging_config import logger

def detect_anomalies(
    cleaned_df: pd.DataFrame,
    quarantined_df: pd.DataFrame,
    config: Dict[str, float]
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Transparent, explainable, rule-based anomaly detection.
    
    Rules supported:
    1. High-Value Transactions (amount > threshold)
    2. Unusual Customer Activity (Statistical Z-score via mean and variance)
    3. Repeated Rapid Transactions (Velocity window)
    4. Duplicate Records (Quarantined duplicates reported as review candidates)
    5. Invalid Entries (Quarantined entries reported as review candidates)

    Flagged transactions are rule-based review candidates, not definitive proof of fraud.
    """
    findings = []
    
    high_value_threshold = float(config.get('high_value_threshold', 50000.0))
    velocity_window_mins = float(config.get('velocity_window_minutes', 5.0))
    velocity_count_thresh = int(config.get('velocity_count_threshold', 3))
    zscore_threshold = float(config.get('customer_zscore_threshold', 2.5))
    min_history = int(config.get('min_customer_history_for_zscore', 3))

    now_iso = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if cleaned_df.empty:
        return cleaned_df, findings

    # Make a copy so we don't modify in-place unexpectedly
    df = cleaned_df.copy()
    
    # Track flags per transaction ID
    flagged_reasons = {}

    # -------------------------------------------------------------
    # Rule 1: High-Value Transactions
    # -------------------------------------------------------------
    high_val_mask = df['amount'] > high_value_threshold
    for _, row in df[high_val_mask].iterrows():
        tx_id = row['transaction_id']
        amt = float(row['amount'])
        reason = f"Transaction amount ₹{amt:,.2f} exceeds configured high-value threshold of ₹{high_value_threshold:,.2f}"
        findings.append({
            "transaction_id": tx_id,
            "customer_id": row['customer_id'],
            "merchant_id": row['merchant_id'],
            "rule_name": "High-Value Transaction",
            "reason": reason,
            "severity": "HIGH" if amt > (high_value_threshold * 1.5) else "MEDIUM",
            "metric_value": amt,
            "threshold_value": high_value_threshold,
            "detected_at": now_iso,
            "details": f"Category: {row['category']}, Merchant: {row['merchant_id']}"
        })
        flagged_reasons[tx_id] = reason

    # -------------------------------------------------------------
    # Rule 2: Repeated Rapid Transactions (Customer Velocity Window)
    # -------------------------------------------------------------
    # Sort by customer_id and timestamp
    df_sorted = df.sort_values(by=['customer_id', 'timestamp']).reset_index(drop=True)
    df_sorted['dt'] = pd.to_datetime(df_sorted['timestamp'])

    for cust_id, group in df_sorted.groupby('customer_id'):
        if len(group) < velocity_count_thresh:
            continue
        
        times = group['dt'].tolist()
        tx_ids = group['transaction_id'].tolist()
        amounts = group['amount'].tolist()
        
        # Sliding window check
        n = len(times)
        for i in range(n):
            window_txs = [tx_ids[i]]
            for j in range(i + 1, n):
                diff_minutes = (times[j] - times[i]).total_seconds() / 60.0
                if diff_minutes <= velocity_window_mins:
                    window_txs.append(tx_ids[j])
                else:
                    break
            
            if len(window_txs) >= velocity_count_thresh:
                # Flag the transactions in this velocity burst
                for vid in window_txs:
                    if vid not in flagged_reasons:
                        reason = f"Customer initiated {len(window_txs)} transactions within {velocity_window_mins:.0f} minutes (Velocity Spike)"
                        findings.append({
                            "transaction_id": vid,
                            "customer_id": cust_id,
                            "merchant_id": group.loc[group['transaction_id'] == vid, 'merchant_id'].values[0],
                            "rule_name": "Velocity Spike",
                            "reason": reason,
                            "severity": "HIGH",
                            "metric_value": float(len(window_txs)),
                            "threshold_value": float(velocity_count_thresh),
                            "detected_at": now_iso,
                            "details": f"Burst count: {len(window_txs)} txns within {velocity_window_mins} mins"
                        })
                        flagged_reasons[vid] = reason

    # -------------------------------------------------------------
    # Rule 3: Unusual Customer Activity (Statistical Z-Score: Mean & Variance)
    # -------------------------------------------------------------
    # Probability and expectation background:
    # Expectation E[X] = mean, Var(X) = E[(X - E[X])^2] = standard_deviation^2
    # Z-Score = (X - mu) / sigma
    for cust_id, group in df.groupby('customer_id'):
        if len(group) < min_history:
            continue
        
        amounts = group['amount'].values
        mean_amt = float(np.mean(amounts))
        std_amt = float(np.std(amounts, ddof=1)) # sample standard deviation

        # If customer transactions have variance:
        if std_amt > 1.0: # avoid division by near-zero variance
            for _, row in group.iterrows():
                amt = float(row['amount'])
                z_score = (amt - mean_amt) / std_amt
                tx_id = row['transaction_id']
                
                if z_score >= zscore_threshold:
                    reason = (
                        f"Unusual spend for customer: amount ₹{amt:,.2f} is {z_score:.2f} standard deviations "
                        f"above personal historical average of ₹{mean_amt:,.2f} (std: ₹{std_amt:,.2f}). "
                        f"Statistical limit: Assumes Gaussian spread; review for unusual personal pattern."
                    )
                    # Add finding if not already flagged as velocity or higher
                    findings.append({
                        "transaction_id": tx_id,
                        "customer_id": cust_id,
                        "merchant_id": row['merchant_id'],
                        "rule_name": "Unusual Customer Activity (Z-Score)",
                        "reason": reason,
                        "severity": "MEDIUM",
                        "metric_value": round(z_score, 2),
                        "threshold_value": zscore_threshold,
                        "detected_at": now_iso,
                        "details": f"Mean: ₹{mean_amt:,.2f}, StdDev: ₹{std_amt:,.2f}, Z: {z_score:.2f}"
                    })
                    if tx_id not in flagged_reasons:
                        flagged_reasons[tx_id] = reason

    # Update cleaned_df with anomaly flags
    df['anomaly_flag'] = df['transaction_id'].apply(lambda x: 1 if x in flagged_reasons else 0)
    df['anomaly_reason'] = df['transaction_id'].apply(lambda x: flagged_reasons.get(x, None))

    # -------------------------------------------------------------
    # Rule 4 & 5: Record findings from Quarantined Data (Duplicates & Invalids)
    # -------------------------------------------------------------
    if not quarantined_df.empty:
        for _, qrow in quarantined_df.iterrows():
            q_reason = qrow.get('quarantine_reason', 'Corrupt entry')
            is_dup = "Duplicate" in q_reason
            rule_name = "Duplicate Record" if is_dup else "Invalid Entry"
            severity = "HIGH" if is_dup else "LOW"
            
            findings.append({
                "transaction_id": qrow.get('transaction_id'),
                "customer_id": qrow.get('customer_id'),
                "merchant_id": qrow.get('merchant_id'),
                "rule_name": rule_name,
                "reason": f"Quarantined: {q_reason}",
                "severity": severity,
                "metric_value": None,
                "threshold_value": None,
                "detected_at": now_iso,
                "details": f"Raw row {qrow.get('raw_id')}, Status: {qrow.get('status')}"
            })

    logger.info(f"Anomaly detection finished. {len(flagged_reasons)} cleaned transactions flagged, {len(findings)} total findings.")
    return df, findings

