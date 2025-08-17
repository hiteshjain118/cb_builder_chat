#!/usr/bin/env python3
"""
Standalone script to run the analyze function for QuickBooks data analysis.
This script loads data from JSONL files and performs markup analysis.
"""

def analyze():
    import pandas as pd
    import json
    import traceback
    bill_data = []
    item_data = []
    # Load the retrieved data from JSONL files
    with open('qb_user_data_retriever_query_Bill_0715cd.jsonl', 'r') as file:
        for line in file:
            bill_data.append(json.loads(line))
    
    with open('qb_user_data_retriever_query_Item_6aa95c.jsonl', 'r') as file:
        for line in file:
            item_data.append(json.loads(line))
    
    # Extract relevant fields from the Bill data
    bill_lines = bill_data[0]['QueryResponse']['Bill'][0]['Line']
    bill_items = []
    for line in bill_lines:
        item_ref = line['ItemBasedExpenseLineDetail']['ItemRef']
        cost_price = line['ItemBasedExpenseLineDetail']['UnitPrice']
        bill_items.append({'ItemId': item_ref['value'], 'CostPrice': cost_price, 'name': item_ref['name']})
    
    # Convert Bill lines to DataFrame
    bill_df = pd.DataFrame(bill_items)

    # Extract relevant fields from the Item data
    item_df = pd.DataFrame()
    for response in item_data:
        items = response['QueryResponse']['Item']
        for item in items:
            tmp_df = pd.DataFrame([{
                'ItemId': item['Id'],
                'Name': item['Name'],
                'SalesPrice': item.get('UnitPrice', 0.0),
                'PurchaseCost': item.get('PurchaseCost', 0.0),
                'name': item['FullyQualifiedName']
            }])
            print(item)
            item_df = pd.concat([item_df, tmp_df])
    
    # Merge the data from Bill and Item DataFrame
    merged_df = pd.merge(bill_df, item_df, on='name')

    # Calculate markup
    merged_df['Markup'] = (merged_df['SalesPrice'] - merged_df['CostPrice']) / merged_df['CostPrice'] * 100

    # Relevant Columns
    result_df = merged_df[['Name', 'CostPrice', 'SalesPrice', 'Markup']]
    
    # Ensure no missing/invalid values
    result_df.dropna(inplace=True)

    return result_df

def main():
    """Main function to run the analysis and display results."""
    try:
        print("Starting QuickBooks data analysis...")
        print("=" * 50)
        
        # Run the analysis
        result_df = analyze()
        
        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE!")
        print("=" * 50)
        
        # Display the results
        print("\nFinal Results:")
        print(result_df.to_string(index=False))
        
        # Display summary statistics
        print("\nSummary Statistics:")
        print(f"Number of items: {len(result_df)}")
        print(f"Average markup: {result_df['Markup'].mean():.2f}%")
        print(f"Markup range: {result_df['Markup'].min():.2f}% to {result_df['Markup'].max():.2f}%")
        
        return result_df
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        traceback.print_exc()
        print("\nRecommendations to fix issues:")
        print("1. Check that JSONL files exist and are readable")
        print("2. Verify data structure matches expected format")
        print("3. Ensure all required fields are present")
        print("4. Check for data quality issues (null values, invalid prices)")
        return None

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"Current working directory: {current_dir}")
    
    # List available JSONL files
    jsonl_files = list(current_dir.glob("*.jsonl"))
    if jsonl_files:
        print(f"Found JSONL files: {[f.name for f in jsonl_files]}")
    else:
        print("No JSONL files found in current directory")
        print("Please ensure you're in the directory containing the data files")
    
    # Run the analysis
    result = main()
    
    if result is not None:
        print("\n✅ Analysis completed successfully!")
    else:
        print("\n❌ Analysis failed. Please check the error messages above.")
        sys.exit(1) 