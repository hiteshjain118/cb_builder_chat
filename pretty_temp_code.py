#!/usr/bin/env python3
"""
QuickBooks Markup Analysis Script
Analyzes markup percentages between Invoice and Bill data for items
"""

import pandas as pd
import json

def analyze():
    import pandas as pd
    import json
    
    # Load invoice and bill data
    with open('model_http_retriever_query_Invoice_{\'query\': "SELECT * FROM Invoice WHERE TxnDate = \'2025-08-08\'"}.jsonl', 'r') as file:
        invoice_data = [json.loads(line) for line in file]

    with open('model_http_retriever_query_Bill_{\'query\': "SELECT * FROM Bill WHERE TxnDate = \'2025-08-08\'"}.jsonl', 'r') as file:
        bill_data = [json.loads(line) for line in file]

    # Extract relevant data from invoices
    invoices = invoice_data[0]['QueryResponse']['Invoice']
    invoice_lines = []
    for invoice in invoices:
        for line in invoice['Line']:
            if line['DetailType'] == 'SalesItemLineDetail':
                invoice_lines.append({
                    'ItemName': line['SalesItemLineDetail']['ItemRef']['name'],
                    'InvoiceAmount': line['Amount'],
                    'InvoiceUnitPrice': line['SalesItemLineDetail']['UnitPrice'],
                    'InvoiceQty': line['SalesItemLineDetail']['Qty'],
                })

    invoice_df = pd.DataFrame(invoice_lines)

    # Extract relevant data from bills
    bills = bill_data[0]['QueryResponse']['Bill']
    bill_lines = []
    for bill in bills:
        for line in bill['Line']:
            if line['DetailType'] == 'ItemBasedExpenseLineDetail':
                bill_lines.append({
                    'ItemName': line['ItemBasedExpenseLineDetail']['ItemRef']['name'],
                    'BillAmount': line['Amount'],
                    'BillUnitPrice': line['ItemBasedExpenseLineDetail']['UnitPrice'],
                    'BillQty': line['ItemBasedExpenseLineDetail']['Qty'],
                })

    bill_df = pd.DataFrame(bill_lines)

    # Merge both dataframes on ItemName
    merged_df = pd.merge(invoice_df, bill_df, on='ItemName', how='inner')

    # Calculate markup percentage
    merged_df['Markup'] = ((merged_df['InvoiceUnitPrice'] - merged_df['BillUnitPrice']) / merged_df['BillUnitPrice']) * 100

    return merged_df[['ItemName', 'InvoiceUnitPrice', 'BillUnitPrice', 'Markup']]

if __name__ == "__main__":
    analyze()