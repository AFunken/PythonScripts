import pandas as pd
import json
import sys

def excel_to_json(excel_file, udt_name, output_file='output.json'):
    """
    Convert Excel file to JSON format for UDT tags.
    
    Expected Excel columns:
    - name: Tag name (e.g., 'V_AB')
    - dataType: Data type (e.g., 'Float4', 'Int4', 'Boolean', etc.)
    - documentation: Tag description (e.g., 'Voltage A to B') - optional
    - engUnit: Engineering unit (e.g., 'V', 'A', 'Hz') - optional
    - valueSource: Value source (default: 'opc') - optional
    - tagType: Tag type (default: 'AtomicTag') - optional
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Remove any completely empty rows
        df = df.dropna(how='all')
        
        # Build tags array
        tags = []
        for _, row in df.iterrows():
            if pd.notna(row.get('name')):  # Only process rows with a name
                # Build tag in Ignition's preferred order
                tag = {}
                tag["valueSource"] = row.get('valueSource', 'opc') if pd.notna(row.get('valueSource')) else 'opc'
                tag["dataType"] = row.get('dataType', 'Float4') if pd.notna(row.get('dataType')) else 'Float4'
                
                # Add documentation if provided (before name)
                if pd.notna(row.get('documentation')):
                    tag["documentation"] = str(row['documentation'])
                
                tag["name"] = str(row['name'])
                tag["tagType"] = row.get('tagType', 'AtomicTag') if pd.notna(row.get('tagType')) else 'AtomicTag'
                
                # Add engUnit if provided
                if pd.notna(row.get('engUnit')):
                    tag["engUnit"] = str(row['engUnit'])
                
                tags.append(tag)
        
        # Build final JSON structure
        result = {
            "name": udt_name,
            "tagType": "UdtType",
            "tags": tags
        }
        
        # Write to JSON file with UTF-8 encoding
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully converted {excel_file} to {output_file}")
        print(f"✓ UDT Name: {udt_name}")
        print(f"✓ Created {len(tags)} tags")
        
        return result
        
    except FileNotFoundError:
        print(f"Error: File '{excel_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <excel_file> <udt_name> [output_file]")
        print("\nExample:")
        print('  python script.py "tags.xlsx" "MV_SWBOARD" "output.json"')
        print("\nExpected Excel columns:")
        print("  - name (required): Tag name")
        print("  - dataType (optional): Data type (default: Float4)")
        print("  - documentation (optional): Tag description")
        print("  - engUnit (optional): Engineering unit")
        print("  - valueSource (optional): Value source (default: opc)")
        print("  - tagType (optional): Tag type (default: AtomicTag)")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    udt_name = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'output.json'
    
    excel_to_json(excel_file, udt_name, output_file)