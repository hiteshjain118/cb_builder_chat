#!/usr/bin/env python3
"""
Script to run the code from temp_code_file.jsonl using PythonFunctionRunner
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builder_package.core.python_function_runner import PythonFunctionRunner
import ast

def main():
    # Read the code from the JSONL file
    with open('temp_code_file.jsonl', 'r') as f:
        line = f.readline().strip()
        # Use ast.literal_eval to safely parse the Python literal
        data = ast.literal_eval(line)
        code = data['code']
    
    print("Code loaded from temp_code_file.jsonl:")
    print("=" * 50)
    print(code)
    print("=" * 50)
    print()
    
    try:
        # Create PythonFunctionRunner instance
        runner = PythonFunctionRunner(code)
        print("✓ PythonFunctionRunner created successfully")
        
        # Execute the tool
        print("\nExecuting analyze() function...")
        result = runner.call_tool()
        
        if result.status == "success":
            print(f"✓ Execution successful!")
            print(f"File created: {result.file_name}")
            print(f"Data type: {type(result.data)}")
            print(f"Data length: {len(result.data) if hasattr(result.data, '__len__') else 'N/A'}")
            
            # Print first few rows of data
            if hasattr(result.data, '__len__') and len(result.data) > 0:
                print("\nFirst few rows of data:")
                for i, row in enumerate(result.data[:3]):
                    print(f"Row {i+1}: {row}")
                if len(result.data) > 3:
                    print(f"... and {len(result.data) - 3} more rows")
        else:
            print(f"✗ Execution failed: {result.error_message}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 