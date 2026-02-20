#to run: python Ignition_UDT_Creation.py input.xlsx MyUDT output.json

import pandas as pd
import json
import sys


def excel_to_json(excel_file, udt_name, output_file='output.json'):
    """
    Convert Excel file to JSON format for UDT tags.

    Expected Excel columns (per row/tag):

    - name: Tag name (e.g., 'V_AB')  [required]
    - dataType: Data type (e.g., 'Float4', 'Int4', 'Boolean', etc.) [optional]
    - documentation: Tag description [optional]
    - engUnit: Engineering unit [optional]
    - valueSource: Value source (default: 'opc') [optional]
    - tagType: Tag type (default: 'AtomicTag') [optional]
    - alarmMode: Alarm mode (WhenTrue, AboveValue, BelowValue, ...) [optional]
    - alarmName: Alarm name (default: 'Alarm') [optional]
    - historyEnabled: any non-null value enables historization [optional]
    - historySampleRate: integer sample rate [optional]
    - historySampleRateUnits: e.g., 'Seconds' [optional]

    NEW for Metadata (Option B):
    - shortDescription: text for Metadata.shortDescription [optional]
    - stateLabels: pipe-separated labels, e.g. 'Closed|Open' [optional]
    - stateValues: pipe-separated values, e.g. 'false|true' [optional]
    """

    try:
        # Read Excel file
        df = pd.read_excel(excel_file)

        # Remove any completely empty rows
        df = df.dropna(how='all')

        tags = []

        for _, row in df.iterrows():
            if pd.notna(row.get('name')):  # Only process rows with a name
                tag = {}

                # ---------- Alarms ----------
                if pd.notna(row.get('alarmMode')):
                    alarm = {
                        "mode": str(row['alarmMode'])
                    }

                    if pd.notna(row.get('alarmName')):
                        alarm["name"] = str(row['alarmName'])
                    else:
                        alarm["name"] = "Alarm"  # Default alarm name

                    tag["alarms"] = [alarm]

                # ---------- Core tag fields ----------
                tag["valueSource"] = (
                    row.get('valueSource', 'opc')
                    if pd.notna(row.get('valueSource'))
                    else 'opc'
                )

                tag["dataType"] = (
                    row.get('dataType', 'Float4')
                    if pd.notna(row.get('dataType'))
                    else 'Float4'
                )

                if pd.notna(row.get('documentation')):
                    tag["documentation"] = str(row['documentation'])

                tag["name"] = str(row['name'])

                tag["tagType"] = (
                    row.get('tagType', 'AtomicTag')
                    if pd.notna(row.get('tagType'))
                    else 'AtomicTag'
                )

                if pd.notna(row.get('engUnit')):
                    tag["engUnit"] = str(row['engUnit'])

                # ---------- Metadata (Option B) ----------
                if pd.notna(row.get('shortDescription')):
                    md = {"shortDescription": str(row['shortDescription'])}

                    # States built from labels/values if present
                    if pd.notna(row.get('stateLabels')) and pd.notna(row.get('stateValues')):
                        labels = str(row['stateLabels']).split('|')
                        values_raw = str(row['stateValues']).split('|')

                        states = []
                        for lbl, val in zip(labels, values_raw):
                            v = str(val).strip().lower()
                            if v in ("true", "1", "yes", "y"):
                                v_bool = True
                            elif v in ("false", "0", "no", "n"):
                                v_bool = False
                            else:
                                # Fallback: leave as string if it doesn't look boolean
                                v_bool = v
                            states.append({
                                "label": lbl.strip(),
                                "value": v_bool
                            })

                        if states:
                            md["states"] = states

                    tag["Metadata"] = md

                # ---------- Historization ----------
                if pd.notna(row.get('historyEnabled')):
                    tag["historyEnabled"] = 'true'

                    if pd.notna(row.get('historySampleRateUnits')):
                        tag["historySampleRateUnits"] = str(row['historySampleRateUnits'])

                    if pd.notna(row.get('historySampleRate')):
                        # Guard against non-numeric sample rate
                        try:
                            tag["historySampleRate"] = int(row['historySampleRate'])
                        except Exception:
                            pass

                tags.append(tag)

        result = {
            "name": udt_name,
            "tagType": "UdtType",
            "tags": tags
        }

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


print(">>> Reached end of file, __name__ =", __name__)

if __name__ == "__main__":
    print(">>> Inside __main__ block")
    print(">>> sys.argv:", sys.argv)

    if len(sys.argv) < 3:
        print("Usage: python Ignition_UDT_Creation.py <excel_file> <udt_name> [output_file]")
        print('Example: python Ignition_UDT_Creation.py "tags.xlsx" "MV_SWBOARD" "output.json"')
        sys.exit(1)

    excel_file = sys.argv[1]
    udt_name = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'output.json'

    print(">>> Calling excel_to_json with:")
    print("    excel_file =", excel_file)
    print("    udt_name   =", udt_name)
    print("    output_file=", output_file)

    excel_to_json(excel_file, udt_name, output_file)
