#!/usr/bin/env python3
"""
Extract tag names and documentation from Ignition UDT JSON files.

This script parses Ignition UDT (User Defined Type) JSON exports and extracts
tag information including names, paths, and documentation strings.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def extract_tags(udt_data: Dict[str, Any], parent_path: str = "") -> List[Dict[str, str]]:
    """
    Recursively extract tag information from UDT JSON structure.
    
    Args:
        udt_data: Dictionary containing UDT structure
        parent_path: Parent path for nested tags
        
    Returns:
        List of dictionaries containing tag information
    """
    tags = []
    
    # Handle different UDT JSON structures
    if isinstance(udt_data, dict):
        # Check for 'tags' key (common in UDT definitions)
        if 'tags' in udt_data:
            tags_list = udt_data['tags']
            if isinstance(tags_list, list):
                for tag in tags_list:
                    tags.extend(process_tag(tag, parent_path))
            elif isinstance(tags_list, dict):
                for tag_name, tag_data in tags_list.items():
                    tags.extend(process_tag(tag_data, parent_path, tag_name))
        
        # Check for 'parameters' key (UDT parameters)
        if 'parameters' in udt_data:
            params = udt_data['parameters']
            if isinstance(params, list):
                for param in params:
                    tags.extend(process_parameter(param, parent_path))
        
        # Check for nested type definitions
        if 'typeId' in udt_data or 'tagType' in udt_data:
            tags.extend(process_tag(udt_data, parent_path))
    
    return tags


def process_tag(tag_data: Dict[str, Any], parent_path: str = "", tag_name: str = None) -> List[Dict[str, str]]:
    """
    Process a single tag and its children.
    
    Args:
        tag_data: Tag data dictionary
        parent_path: Parent path for the tag
        tag_name: Optional tag name if not in tag_data
        
    Returns:
        List of tag dictionaries
    """
    tags = []
    
    # Get tag name
    name = tag_name or tag_data.get('name', 'Unknown')
    
    # Build full path
    full_path = f"{parent_path}/{name}" if parent_path else name
    
    # Extract documentation
    documentation = tag_data.get('documentation', '')
    
    # Check for alarm configuration
    has_alarm = 'No'
    if 'alarms' in tag_data and tag_data['alarms']:
        has_alarm = 'Yes'
    elif 'alarmConfig' in tag_data and tag_data['alarmConfig']:
        has_alarm = 'Yes'
    
    # Check for history configuration
    has_history = 'No'
    if 'historyEnabled' in tag_data and tag_data['historyEnabled']:
        has_history = 'Yes'
    elif 'historicalDeadband' in tag_data or 'historyProvider' in tag_data:
        has_history = 'Yes'
    
    # Add current tag
    tag_info = {
        'tag': full_path,
        'documentation': documentation,
        'alarm': has_alarm,
        'history': has_history
    }
    tags.append(tag_info)
    
    # Process nested tags
    if 'tags' in tag_data:
        nested_tags = tag_data['tags']
        if isinstance(nested_tags, list):
            for nested_tag in nested_tags:
                tags.extend(process_tag(nested_tag, full_path))
        elif isinstance(nested_tags, dict):
            for nested_name, nested_data in nested_tags.items():
                tags.extend(process_tag(nested_data, full_path, nested_name))
    
    return tags


def process_parameter(param_data: Dict[str, Any], parent_path: str = "") -> List[Dict[str, str]]:
    """
    Process UDT parameter information.
    
    Args:
        param_data: Parameter data dictionary
        parent_path: Parent path for the parameter
        
    Returns:
        List containing parameter information
    """
    name = param_data.get('name', 'Unknown')
    full_path = f"{parent_path}/[PARAM]{name}" if parent_path else f"[PARAM]{name}"
    
    param_info = {
        'tag': full_path,
        'documentation': param_data.get('documentation', ''),
        'alarm': 'No',
        'history': 'No'
    }
    
    return [param_info]


def parse_udt_file(filepath: str) -> List[Dict[str, str]]:
    """
    Parse an Ignition UDT JSON file and extract tag information.
    
    Args:
        filepath: Path to the UDT JSON file
        
    Returns:
        List of tag dictionaries
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return extract_tags(data)


def export_to_csv(tags: List[Dict[str, str]], output_file: str):
    """
    Export tags to CSV format.
    
    Args:
        tags: List of tag dictionaries
        output_file: Output CSV filename
    """
    import csv
    
    if not tags:
        print("No tags to export")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['tag', 'documentation', 'alarm', 'history']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for tag in tags:
            writer.writerow(tag)
    
    print(f"Exported {len(tags)} tags to {output_file}")


def print_tags(tags: List[Dict[str, str]]):
    """
    Print tags in a formatted manner.
    
    Args:
        tags: List of tag dictionaries
    """
    for i, tag in enumerate(tags, 1):
        print(f"\n{i}. Tag: {tag['tag']}")
        if tag['documentation']:
            print(f"   Documentation: {tag['documentation']}")
        else:
            print(f"   Documentation: (none)")
        print(f"   Alarm Configured: {tag['alarm']}")
        print(f"   History Enabled: {tag['history']}")


def main():
    """Main function to run the script."""
    if len(sys.argv) < 2:
        print("Usage: python extract_udt_tags.py <udt_json_file> [--csv output.csv]")
        print("\nExample:")
        print("  python extract_udt_tags.py my_udt.json")
        print("  python extract_udt_tags.py my_udt.json --csv output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    # Parse the UDT file
    print(f"Parsing UDT file: {input_file}")
    tags = parse_udt_file(input_file)
    
    # Check for CSV export option
    if '--csv' in sys.argv and len(sys.argv) > sys.argv.index('--csv') + 1:
        csv_file = sys.argv[sys.argv.index('--csv') + 1]
        export_to_csv(tags, csv_file)
    else:
        print_tags(tags)
        print(f"\n\nTotal tags found: {len(tags)}")


if __name__ == "__main__":
    main()