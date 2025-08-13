#!/usr/bin/env python3
"""
Markup Analysis Script
Calculates markup percentages between Invoice and Bill data for items
"""

import pandas as pd
import json

# Load data from jsonl files
with open('model_http_retriever_query_Invoice_{\'query\': "SELECT * FROM Invoice WHERE TxnDate = \'2025-08-08\'"}.jsonl', 'r') as f:
    invoice_data = json.loads(f.readline().strip())

with open('model_http_retriever_query_Bill_{\'query\': "SELECT * FROM Bill WHERE TxnDate = \'2025-08-08\'"}.jsonl', 'r') as f:
    bill_data = json.loads(f.readline().strip())

# Extract relevant columns from Invoice data
invoice_lines = []
for invoice in invoice_data['QueryResponse']['Invoice']:
    for line in invoice['Line']:
        if 'SalesItemLineDetail' in line['DetailType']:
            invoice_lines.append({
                'Item': line['SalesItemLineDetail']['ItemRef']['name'],
                'Qty': line['SalesItemLineDetail']['Qty'],
                'UnitPrice': line['SalesItemLineDetail']['UnitPrice'],
                'Amount': line['Amount']
            })

# Extract relevant columns from Bill data
bill_lines = []
for bill in bill_data['QueryResponse']['Bill']:
    for line in bill['Line']:
        if 'ItemBasedExpenseLineDetail' in line['DetailType']:
            bill_lines.append({
                'Item': line['ItemBasedExpenseLineDetail']['ItemRef']['name'],
                'Qty': line['ItemBasedExpenseLineDetail']['Qty'],
                'UnitPrice': line['ItemBasedExpenseLineDetail']['UnitPrice'],
                'Amount': line['Amount']
            })

# Create dataframes
invoice_df = pd.DataFrame(invoice_lines)
bill_df = pd.DataFrame(bill_lines)

# Merge dataframes on item names
merged_df = pd.merge(
    invoice_df, 
    bill_df, 
    on='Item', 
    suffixes=('_invoice', '_bill')
)

# Calculate markup percentage
merged_df['Markup'] = (
    (merged_df['UnitPrice_invoice'] - merged_df['UnitPrice_bill']) / 
    merged_df['UnitPrice_bill']
) * 100

# Select relevant columns for final output
markup_df = merged_df[['Item', 'UnitPrice_invoice', 'UnitPrice_bill', 'Markup']]

# Sort by markup percentage (highest first)
markup_df = markup_df.sort_values(by='Markup', ascending=False)

# Display top 10 items by markup
print("Top 10 Items by Markup Percentage:")
print("=" * 50)
print(markup_df.head(10))

# Summary statistics
print("\n" + "=" * 50)
print("Summary Statistics:")
print(f"Total items analyzed: {len(markup_df)}")
print(f"Average markup: {markup_df['Markup'].mean():.2f}%")
print(f"Highest markup: {markup_df['Markup'].max():.2f}%")
print(f"Lowest markup: {markup_df['Markup'].min():.2f}%") 