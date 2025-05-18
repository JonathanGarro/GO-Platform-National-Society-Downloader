import requests
import pandas as pd
import time
import json
from datetime import datetime
import os


def flatten_dict(d, parent_key='', sep='.'):
    """
    Recursively flatten a nested dictionary.

    Args:
        d (dict): The dictionary to flatten
        parent_key (str): The parent key for nested keys
        sep (str): Separator between the keys

    Returns:
        dict: Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # stringify lists
            if len(v) > 0 and isinstance(v[0], dict):
                # store a placeholder
                items.append((new_key, f"[List of {len(v)} items]"))
            else:
                # join them as a string with a delimiter
                items.append((new_key, "|".join(str(item) for item in v)))
        else:
            items.append((new_key, v))

    return dict(items)


def fetch_all_countries():
    """
    Function to fetch all country data from the IFRC GO API
    and export it to a CSV file with all fields including nested ones.
    """
    base_url = "https://goadmin.ifrc.org/api/v2/country/"
    all_data = []
    next_url = base_url
    page_count = 0
    max_retries = 3

    # create output dir
    output_dir = "ifrc_data"
    os.makedirs(output_dir, exist_ok=True)

    print("Starting data extraction from IFRC GO API...")

    while next_url:
        page_count += 1
        print(f"Fetching page {page_count}: {next_url}")

        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(next_url, timeout=30)
                response.raise_for_status()

                data = response.json()

                if 'results' in data and isinstance(data['results'], list):
                    all_data.extend(data['results'])
                    print(f"  Found {len(data['results'])} records on this page")
                else:
                    print("  Warning: No results found on this page or unexpected format")

                next_url = data.get('next')

                # small delay between requests bc the GO server doesn't like me sometimes
                if next_url:
                    time.sleep(1)

                break

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Error fetching data: {e}")
                # try again after if it might be rate limiting
                if hasattr(e, 'response') and e.response and e.response.status_code in (429, 503):
                    retry_after = int(e.response.headers.get('Retry-After', 60))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                elif retries < max_retries:
                    wait_time = 5 * retries
                    print(f"Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Moving to next page.")
                    next_url = None
                    break
            except json.JSONDecodeError:
                print("Error parsing JSON response. Skipping to next page.")
                next_url = None
                break

    print(f"Number of records fetched: {len(all_data)}")

    if all_data:
        try:
            timestamp = datetime.now().strftime("%Y%m%d")

            # save raw data
            raw_file = os.path.join(output_dir, f"raw_country_data_{timestamp}.json")
            with open(raw_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            print(f"Raw data saved to {raw_file}")

            nested_list_fields = {}

            for record in all_data:
                for key, value in record.items():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        if key not in nested_list_fields:
                            nested_list_fields[key] = []
                        nested_list_fields[key].extend(
                            [{**item, 'parent_id': record.get('id', 'unknown')} for item in value])

            for field, items in nested_list_fields.items():
                print(f"Processing nested list field '{field}' ({len(items)} items)")

                if items:
                    flattened_items = [flatten_dict(item) for item in items]

                    nested_df = pd.DataFrame(flattened_items)

                    field_name = field.replace('.', '_').replace('/', '_')
                    nested_file = os.path.join(output_dir, f"ifrc_countries_{field_name}_{timestamp}.csv")

                    # Export to CSV
                    nested_df.to_csv(nested_file, index=False, encoding='utf-8')
                    print(f"  Nested data exported to {nested_file}")

            flattened_data = [flatten_dict(record) for record in all_data]

            df = pd.DataFrame(flattened_data)

            # csv export
            output_file = os.path.join(output_dir, f"ifrc_countries_{timestamp}.csv")
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Main data exported to {output_file}")
            print(f"Total columns in main file: {len(df.columns)}")

            # sense check the column names
            print("\nSample columns from main file:")
            sample_cols = sorted(list(df.columns))[:10]
            for col in sample_cols:
                print(f"  - {col}")

        except Exception as e:
            print(f"Error processing data: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No data to export")


if __name__ == "__main__":
    fetch_all_countries()
    print("Process completed.")