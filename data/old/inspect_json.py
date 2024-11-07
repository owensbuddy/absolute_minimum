import json
import os

# Define the path to the JSON file
file_path = "/Users/buddy/Desktop/School/effective-adventure/effective-adventure/data/posts.json"

def inspect_json_health(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return

    # Load the JSON data
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return

    # Check if the data is a list of dictionaries (expected structure for posts)
    if not isinstance(data, list):
        print("Expected a list of dictionaries, but found:", type(data))
        return

    # Initialize field tracking and counters
    field_counts = {}
    total_entries = len(data)
    empty_value_count = 0
    inconsistent_type_count = 0

    # Inspect structure
    for entry in data:
        if not isinstance(entry, dict):
            inconsistent_type_count += 1
            continue

        # Track field occurrences
        for key in entry.keys():
            field_counts[key] = field_counts.get(key, 0) + 1

        # Check for empty values
        for field, value in entry.items():
            if value in [None, "", [], {}]:
                empty_value_count += 1
                break

    # Summary of findings
    print("JSON Structure Health Summary:")
    print(f"- Total entries: {total_entries}")
    print(f"- Inconsistent entries (not dictionaries): {inconsistent_type_count}")
    print(f"- Entries with empty values: {empty_value_count}")
    print("\nField presence across entries:")
    for key, count in field_counts.items():
        print(f"  - {key}: present in {count}/{total_entries} entries")

    # Report missing fields
    missing_field_entries = total_entries - max(field_counts.values(), default=0)
    print(f"\nEntries missing some fields: {missing_field_entries}/{total_entries}")

    print("\nInspection complete.")

# Run the inspection
inspect_json_health(file_path)