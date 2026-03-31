import pandas as pd

# Load data
tx = pd.read_csv("data/transactions.csv")
st = pd.read_csv("data/settlements.csv")

tx['date'] = pd.to_datetime(tx['date'])
st['settlement_date'] = pd.to_datetime(st['settlement_date'])

# Merge
merged = tx.merge(st, on="transaction_id", how="left")

report = []

# Missing settlement
missing = merged[merged['settlement_id'].isnull()]
for _, row in missing.iterrows():
    report.append([row['transaction_id'], "Missing Settlement"])

# Duplicate
duplicates = st[st.duplicated('transaction_id', keep=False)]
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

# Save report
df = pd.DataFrame(report, columns=["transaction_id", "issue"])
df = df.drop_duplicates()
df.to_csv("report.csv", index=False)

print("\n✅ REPORT GENERATED:\n")
print(df)