# QuickBooks Data Analysis Script

This standalone script runs the markup analysis function that was previously executed within the chat application.

## Files

- `run_analysis.py` - Main analysis script
- `requirements_analysis.txt` - Python dependencies
- `README_analysis.md` - This documentation

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Required data files** in the same directory:
   - `qb_user_data_retriever_query_Bill_0715cd.jsonl`
   - `qb_user_data_retriever_query_Item_6aa95c.jsonl`

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements_analysis.txt
   ```

2. **Ensure data files are present:**
   - Copy your JSONL data files to the same directory as the script
   - Or modify the file paths in the script if they're located elsewhere

## Usage

### Basic Usage
```bash
python run_analysis.py
```

### What the Script Does

1. **Loads data** from the two JSONL files (Bill and Item data)
2. **Validates data structure** and content
3. **Processes Bill data** to extract line items with cost prices
4. **Processes Item data** to extract sales prices and purchase costs
5. **Merges the datasets** based on Item IDs
6. **Calculates markup percentages** using the formula: `(SalesPrice - CostPrice) / CostPrice * 100`
7. **Performs business logic validation** (checks for negative prices, zero prices, etc.)
8. **Outputs results** to console and saves to CSV file

### Output

- **Console output**: Detailed analysis process, warnings, and final results
- **CSV file**: `markup_analysis_results.csv` with columns:
  - `Name`: Item name
  - `CostPrice`: Cost price from Bill data
  - `SalesPrice`: Sales price from Item data
  - `Markup`: Calculated markup percentage

### Data Validation Features

The script includes comprehensive data validation:
- **Structure validation**: Ensures required JSON keys exist
- **Data quality checks**: Identifies missing, null, or invalid values
- **Business logic validation**: Checks for negative prices, zero prices, infinite markup
- **Warning system**: Reports issues without failing the entire analysis

## Customization

### Changing File Paths
Modify these lines in the script:
```python
bill_file = 'qb_user_data_retriever_query_Bill_0715cd.jsonl'
item_file = 'qb_user_data_retriever_query_Item_6aa95c.jsonl'
```

### Adding More Validation
The script has a modular structure - you can add more validation checks in the `analyze()` function.

### Modifying Output Format
Change the CSV output filename or add additional export formats in the `main()` function.

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure JSONL files are in the same directory
2. **Import errors**: Install required packages with `pip install -r requirements_analysis.txt`
3. **Data structure errors**: Check that your JSONL files match the expected QuickBooks API format
4. **Empty results**: Verify data quality and check warning messages for skipped items

### Debug Mode

The script provides detailed logging throughout the process. If you encounter issues:
1. Check the console output for specific error messages
2. Verify the data structure of your JSONL files
3. Ensure all required fields are present in your data

## Example Output

```
Starting QuickBooks data analysis...
==================================================
Loading data from qb_user_data_retriever_query_Bill_0715cd.jsonl...
Loading data from qb_user_data_retriever_query_Item_6aa95c.jsonl...
Performing data validation...
Processing Bill data...
Found 15 valid bill items
Processing Item data...
Found 23 valid items
Merging Bill and Item data...
Merged DataFrame shape: (15, 5)
Running business logic invariant checks...
Calculating markup percentages...
Final data validation...
Final result DataFrame shape: (15, 4)

=== BUSINESS LOGIC SUMMARY ===
Total items analyzed: 15
Average markup: 45.67%
Minimum markup: 12.34%
Maximum markup: 89.12%
Total cost: $1,234.56
Total sales value: $1,798.90
Total markup value: $564.34

==================================================
ANALYSIS COMPLETE!
==================================================

Final Results:
Name                    CostPrice  SalesPrice  Markup
Item A                    10.00       15.00    50.00
Item B                    25.00       45.00    80.00
...

Results saved to: markup_analysis_results.csv
```

## Support

If you encounter issues:
1. Check the console output for specific error messages
2. Verify your data files match the expected format
3. Ensure all dependencies are properly installed 