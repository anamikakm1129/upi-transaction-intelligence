import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..utils.logging_config import logger

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SAMPLE_CSV_PATH = os.path.join(DATA_DIR, "sample_transactions.csv")

CUSTOMERS = [
    f"cust_{name.lower()}@{handle}"
    for name in [
        "Aarav", "Priya", "Rohit", "Ananya", "Vikram", "Sneha", "Karan", "Deepa",
        "Arjun", "Meera", "Aditya", "Neha", "Rohan", "Pooja", "Varun", "Isha",
        "Siddharth", "Kavya", "Manish", "Divya", "Gautam", "Tanvi", "Nikhil", "Shreya",
        "Harsh", "Ritu", "Akash", "Swati", "Abhishek", "Preeti", "Rahul", "Anjali"
    ]
    for handle in ["oksbi", "okhdfcbank", "icici", "okaxis", "ybl", "paytm", "kotak"]
][:60]

MERCHANTS_BY_CATEGORY = {
    "Grocery & Supermarket": [
        ("blinkit@axis", "Blinkit Instant Commerce"),
        ("zepto@icici", "Zepto Quick Delivery"),
        ("dmart.retail@hdfc", "DMart Supermarket"),
        ("instamart@swiggy", "Swiggy Instamart"),
        ("bigbasket@tata", "BigBasket Tata")
    ],
    "Food & Dining": [
        ("swiggy@icici", "Swiggy Foods"),
        ("zomato@hdfc", "Zomato Delivery"),
        ("mcdonalds@hdfc", "McDonalds India"),
        ("starbucks@tata", "Starbucks Coffee"),
        ("dominos@icici", "Dominos Pizza")
    ],
    "Shopping & E-Commerce": [
        ("amazon.pay@apl", "Amazon India"),
        ("flipkart.upi@axis", "Flipkart Internet"),
        ("myntra@icici", "Myntra Fashion"),
        ("nykaa@hdfc", "Nykaa Cosmetics"),
        ("croma@tata", "Croma Electronics")
    ],
    "Utilities & Bill Pay": [
        ("bescom.power@sbi", "BESCOM Electricity"),
        ("airtel.payments@airtel", "Airtel Broadband & Mobile"),
        ("jio.fiber@jio", "Jio Fiber Services"),
        ("mahanagar.gas@sbi", "Mahanagar Gas"),
        ("tata.play@hdfc", "Tata Play DTH")
    ],
    "Travel & Transport": [
        ("uber.india@icici", "Uber India"),
        ("ola.cabs@axis", "Ola Mobility"),
        ("irctc.upi@sbi", "IRCTC Indian Railways"),
        ("makemytrip@hdfc", "MakeMyTrip"),
        ("fastag.toll@nhai", "NHAI NETC FASTag")
    ],
    "Health & Wellness": [
        ("apollo.pharmacy@hdfc", "Apollo Pharmacy"),
        ("1mg.healthcare@icici", "Tata 1mg"),
        ("pharmeasy@axis", "PharmEasy"),
        ("cultfit@hdfc", "Cult.fit Healthcare")
    ],
    "Entertainment & Subscriptions": [
        ("bookmyshow@kotak", "BookMyShow Movies"),
        ("netflix.india@hdfc", "Netflix Entertainment"),
        ("spotify.india@icici", "Spotify Music"),
        ("hotstar@axis", "Disney+ Hotstar")
    ],
    "Peer-to-Peer (P2P)": [
        ("rahul.sharma@okaxis", "Rahul Sharma P2P"),
        ("anita.deshmukh@oksbi", "Anita Deshmukh P2P"),
        ("rajesh.kumar@icici", "Rajesh Kumar P2P"),
        ("sunita.verma@ybl", "Sunita Verma P2P")
    ]
}

CATEGORY_AMOUNT_RANGES = {
    "Grocery & Supermarket": (120, 2800, 650),
    "Food & Dining": (80, 1500, 380),
    "Shopping & E-Commerce": (399, 9500, 1850),
    "Utilities & Bill Pay": (250, 4200, 1100),
    "Travel & Transport": (50, 1800, 240),
    "Health & Wellness": (150, 4800, 750),
    "Entertainment & Subscriptions": (149, 1499, 499),
    "Peer-to-Peer (P2P)": (100, 18000, 2200)
}

# Diurnal hourly probability weights (reflecting real Indian UPI traffic: peak 7-10 PM)
HOURLY_WEIGHTS = [
    0.008, 0.005, 0.003, 0.002, 0.004, 0.010, # 00-05 AM (lull)
    0.025, 0.045, 0.060, 0.065, 0.055, 0.050, # 06-11 AM (morning ramp)
    0.075, 0.080, 0.060, 0.045, 0.045, 0.055, # 12-17 PM (lunch & afternoon)
    0.075, 0.095, 0.100, 0.085, 0.045, 0.016  # 18-23 PM (evening peak 7-10 PM)
]

def generate_sample_dataset(num_records: int = 1200, seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic, synthetic UPI transaction dataset.
    Clearly labeled as synthetic in output metadata.
    Includes controlled duplicates, high-value outliers, velocity spikes,
    and invalid test records for transparent data quality evaluation.
    """
    random.seed(seed)
    np.random.seed(seed)

    base_date = datetime.now() - timedelta(days=14)
    records = []

    categories = list(MERCHANTS_BY_CATEGORY.keys())
    cat_weights = [0.25, 0.22, 0.14, 0.10, 0.12, 0.06, 0.04, 0.07]

    payment_methods = ["UPI-QR", "UPI-P2P", "UPI-Collect", "UPI-Autopay"]
    pm_weights = [0.60, 0.20, 0.15, 0.05]

    device_types = ["Android", "iOS", "Web"]
    dev_weights = [0.78, 0.20, 0.02]

    # Status probabilities: 94% Success, 5% Failed, 1% Pending
    statuses = ["SUCCESS", "FAILED", "PENDING"]
    status_weights = [0.94, 0.05, 0.01]

    tx_counter = 10001

    hourly_p = np.array(HOURLY_WEIGHTS, dtype=float)
    hourly_p /= hourly_p.sum()

    for _ in range(num_records):
        day_offset = random.randint(0, 13)
        hour = np.random.choice(range(24), p=hourly_p)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        tx_time = base_date + timedelta(days=day_offset, hours=int(hour), minutes=minute, seconds=second)

        cust = random.choice(CUSTOMERS)
        cat = np.random.choice(categories, p=cat_weights)
        merchants = MERCHANTS_BY_CATEGORY[cat]
        merchant_id, _ = random.choice(merchants)

        min_a, max_a, mode_a = CATEGORY_AMOUNT_RANGES[cat]
        # Triangular distribution gives realistic pricing distribution
        amount = round(float(np.random.triangular(min_a, mode_a, max_a)), 2)

        pm = np.random.choice(payment_methods, p=pm_weights)
        dev = np.random.choice(device_types, p=dev_weights)
        st = np.random.choice(statuses, p=status_weights)
        rrn = f"42{random.randint(1000000000, 9999999999)}"

        tx_id = f"UPI{tx_time.strftime('%Y%m%d')}{tx_counter}"
        tx_counter += 1

        records.append({
            "transaction_id": tx_id,
            "timestamp": tx_time.strftime('%Y-%m-%d %H:%M:%S'),
            "customer_id": cust,
            "merchant_id": merchant_id,
            "amount": amount,
            "category": cat,
            "status": st,
            "payment_method": pm,
            "bank_reference_number": rrn,
            "device_type": dev
        })

    # =========================================================
    # Controlled Anomalies for Demonstration & Data Quality Testing
    # =========================================================

    # 1. High-Value Transactions (> ₹50,000 threshold)
    high_value_targets = [
        ("UPI2026101290001", 68500.00, "Shopping & E-Commerce", "croma@tata"),
        ("UPI2026101390002", 94250.00, "Shopping & E-Commerce", "amazon.pay@apl"),
        ("UPI2026101490003", 125000.00, "Peer-to-Peer (P2P)", "rahul.sharma@okaxis")
    ]
    for h_id, h_amt, h_cat, h_merch in high_value_targets:
        h_time = (base_date + timedelta(days=random.randint(2, 10), hours=15, minutes=20)).strftime('%Y-%m-%d %H:%M:%S')
        records.append({
            "transaction_id": h_id,
            "timestamp": h_time,
            "customer_id": "cust_vikram@paytm",
            "merchant_id": h_merch,
            "amount": h_amt,
            "category": h_cat,
            "status": "SUCCESS",
            "payment_method": "UPI-Collect",
            "bank_reference_number": f"42{random.randint(1000000000, 9999999999)}",
            "device_type": "Android"
        })

    # 2. Velocity Spike: Rapid burst of transactions within 3 minutes by same customer
    burst_cust = "cust_aarav@oksbi"
    burst_base = base_date + timedelta(days=5, hours=19, minutes=10)
    for b_idx in range(4):
        b_time = (burst_base + timedelta(seconds=b_idx * 35)).strftime('%Y-%m-%d %H:%M:%S')
        records.append({
            "transaction_id": f"UPIBURST{b_idx+1:04d}",
            "timestamp": b_time,
            "customer_id": burst_cust,
            "merchant_id": "blinkit@axis",
            "amount": round(780.0 + (b_idx * 150), 2),
            "category": "Grocery & Supermarket",
            "status": "SUCCESS",
            "payment_method": "UPI-QR",
            "bank_reference_number": f"42{random.randint(1000000000, 9999999999)}",
            "device_type": "iOS"
        })

    # 3. Controlled Statistical Z-Score Outlier
    # Customer 'cust_sneha@ybl' usually spends ~₹200-₹400, suddenly spends ₹32,000
    for s_idx in range(6):
        records.append({
            "transaction_id": f"UPISNEHA{s_idx+1:04d}",
            "timestamp": (base_date + timedelta(days=s_idx + 1, hours=11)).strftime('%Y-%m-%d %H:%M:%S'),
            "customer_id": "cust_sneha@ybl",
            "merchant_id": "swiggy@icici",
            "amount": round(random.uniform(220, 390), 2),
            "category": "Food & Dining",
            "status": "SUCCESS",
            "payment_method": "UPI-QR",
            "bank_reference_number": f"42{random.randint(1000000000, 9999999999)}",
            "device_type": "Android"
        })
    # The anomaly spike transaction:
    records.append({
        "transaction_id": "UPISNEHA_SPIKE",
        "timestamp": (base_date + timedelta(days=8, hours=14, minutes=45)).strftime('%Y-%m-%d %H:%M:%S'),
        "customer_id": "cust_sneha@ybl",
        "merchant_id": "myntra@icici",
        "amount": 34500.00,
        "category": "Shopping & E-Commerce",
        "status": "SUCCESS",
        "payment_method": "UPI-Collect",
        "bank_reference_number": f"42{random.randint(1000000000, 9999999999)}",
        "device_type": "Android"
    })

    # 4. Controlled Duplicates (same transaction_id repeated)
    if len(records) > 5:
        records.append(dict(records[2])) # Duplicate 1
        records.append(dict(records[5])) # Duplicate 2
        records.append(dict(records[10])) # Duplicate 3

    # 5. Controlled Invalid Entries for Data Quality Report
    records.append({
        "transaction_id": "UPI_INVALID_AMT_NEG",
        "timestamp": (base_date + timedelta(days=3, hours=10)).strftime('%Y-%m-%d %H:%M:%S'),
        "customer_id": "cust_karan@ibl",
        "merchant_id": "swiggy@icici",
        "amount": -450.00, # NEGATIVE AMOUNT
        "category": "Food & Dining",
        "status": "SUCCESS",
        "payment_method": "UPI-QR",
        "bank_reference_number": "429999999991",
        "device_type": "Android"
    })
    records.append({
        "transaction_id": "UPI_INVALID_AMT_ZERO",
        "timestamp": (base_date + timedelta(days=4, hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
        "customer_id": "cust_priya@okhdfcbank",
        "merchant_id": "uber.india@icici",
        "amount": 0.00, # ZERO AMOUNT
        "category": "Travel & Transport",
        "status": "FAILED",
        "payment_method": "UPI-QR",
        "bank_reference_number": "429999999992",
        "device_type": "iOS"
    })
    records.append({
        "transaction_id": "UPI_INVALID_DATE_FORMAT",
        "timestamp": "2026-99-99 25:99:99", # UNPARSEABLE TIMESTAMP
        "customer_id": "cust_rohit@icici",
        "merchant_id": "blinkit@axis",
        "amount": 540.00,
        "category": "Grocery & Supermarket",
        "status": "SUCCESS",
        "payment_method": "UPI-QR",
        "bank_reference_number": "429999999993",
        "device_type": "Android"
    })
    records.append({
        "transaction_id": "UPI_MISSING_CUST_ID",
        "timestamp": (base_date + timedelta(days=6, hours=18)).strftime('%Y-%m-%d %H:%M:%S'),
        "customer_id": None, # MISSING MANDATORY CUSTOMER_ID
        "merchant_id": "zomato@hdfc",
        "amount": 620.00,
        "category": "Food & Dining",
        "status": "SUCCESS",
        "payment_method": "UPI-QR",
        "bank_reference_number": "429999999994",
        "device_type": "Android"
    })

    df = pd.DataFrame(records)
    logger.info(f"Generated synthetic dataset with {len(df)} total rows.")
    return df

def ensure_sample_csv_exists() -> str:
    """Ensure that the default sample CSV file is generated and persisted."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SAMPLE_CSV_PATH) or os.path.getsize(SAMPLE_CSV_PATH) == 0:
        logger.info(f"Creating sample synthetic dataset at: {SAMPLE_CSV_PATH}")
        df = generate_sample_dataset(num_records=1200)
        df.to_csv(SAMPLE_CSV_PATH, index=False)
    return SAMPLE_CSV_PATH
