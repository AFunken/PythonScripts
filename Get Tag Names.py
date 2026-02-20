import json

# Load the JSON file
with open("C:\\Users\\austin.funken\\OneDrive - Hoffman and Hoffman\\Documents\\Projects\\Standard Project - EPMS\\STD_AO_UDT.json", 'r') as f:
    data = json.load(f)

# Extract name and documentation from each tag
results = []

for tag in data.get('tags', []):
    name = tag.get('name', '')
    documentation = tag.get('documentation', '')
    
    results.append({
        'name': name,
        'documentation': documentation
    })

# Print results
for item in results:
    print(f"Name: {item['name']}")
    print(f"Documentation: {item['documentation']}")
    print('-' * 50)