#!/usr/bin/env python3
"""
Test script to see what columns are available after json_normalize
"""

import pandas as pd
import json

# Load a small sample of the data
with open('model_http_retriever_query_Invoice_72bbf4.jsonl', 'r') as f:
    line = f.readline().strip()
    data = json.loads(line)
    invoices = data['QueryResponse']['Invoice'][:2]  # Just first 2 invoices

print("Sample invoice structure:")
print(json.dumps(invoices[0], indent=2))

# Test json_normalize
invoices_df = pd.json_normalize(invoices, 'Line', ['Id'], 
                               record_prefix='Line_', meta_prefix='Invoice_')

print(f"\nDataFrame shape: {invoices_df.shape}")
print(f"Available columns: {list(invoices_df.columns)}")

# Show first few rows
print(f"\nFirst few rows:")
print(invoices_df.head()) 