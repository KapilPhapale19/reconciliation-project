import streamlit as st
import pandas as pd

st.title("💰 Payment Reconciliation System")

# Load data
tx = pd.read_csv("data/transactions.csv")
st_data = pd.read_csv("data/settlements.csv")

tx['date'] = pd.to_datetime(tx['date'])
st_data['settlement_date'] = pd.to_datetime(st_data['settlement_date'])

if st.button("Run Reconciliation"):

    merged = tx.merge(st_data, on="transaction_id", how="left")
    report = []

    # Missing settlement
    missing = merged[merged['settlement_id'].isnull()]
    for _, row in missing.iterrows():
        report.append([row['transaction_id'], "Missing Settlement"])

    # Duplicate
    duplicates = st_data[st_data.duplicated('transaction_id', keep=False)]
    for _, row in duplicates.iterrows():
        report.append([row['transaction_id'], "Duplicate Settlement"])

    # Rounding
    rounding = merged[
        (abs(merged['amount_x'] - merged['amount_y']) > 0) &
        (abs(merged['amount_x'] - merged['amount_y']) < 1)
    ]
    for _, row in rounding.iterrows():
        report.append([row['transaction_id'], "Rounding Issue"])

    # Late settlement
    late = merged[
        merged['date'].dt.month != merged['settlement_date'].dt.month
    ]
    for _, row in late.iterrows():
        report.append([row['transaction_id'], "Late Settlement"])

    # Orphan refund
    payments = tx[tx['type'] == 'payment']['transaction_id'].tolist()
    refunds = tx[tx['type'] == 'refund']
    orphan = refunds[~refunds['transaction_id'].isin(payments)]

    for _, row in orphan.iterrows():
        report.append([row['transaction_id'], "Orphan Refund"])

    df = pd.DataFrame(report, columns=["transaction_id", "issue"]).drop_duplicates()

    st.success("✅ Reconciliation Complete")
    st.dataframe(df)