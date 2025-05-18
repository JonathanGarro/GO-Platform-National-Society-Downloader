# IFRC National Society Downloader

A Python tool for downloading and processing data about National Societies from the IFRC GO Platform API.

## Description

This tool fetches comprehensive data about Red Cross and Red Crescent National Societies from the IFRC GO Platform API. It processes the data, flattens nested structures, and exports the results to CSV and JSON files for easy analysis and use.

The data includes:
- Basic information about National Societies
- Contact details
- Geographical information
- Links and relationships
- Other metadata

## Features

- Fetches data from the IFRC GO API with pagination support
- Handles API rate limiting and retries
- Flattens nested JSON structures for easier data processing
- Exports data in both raw JSON and processed CSV formats
- Timestamps output files for versioning
- Handles nested list fields by creating separate CSV files

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/national-society-downloader.git
   cd national-society-downloader
   ```

2. Install the required dependencies:
   ```
   pip install requests pandas
   ```

## Usage

Simply run the script:

```
python go_ns_explorer.py
```

The script will:
1. Create an `ifrc_data` directory if it doesn't exist
2. Fetch all country data from the IFRC GO API
3. Save the raw data as a JSON file
4. Process and flatten the data
5. Export the main dataset as a CSV file
6. Process any nested list fields into separate CSV files

## Output Files

The script generates the following files in the `ifrc_data` directory:

- `raw_country_data_YYYYMMDD.json`: Raw JSON data from the API
- `ifrc_countries_YYYYMMDD.csv`: Main flattened dataset with all country information
- `ifrc_countries_FIELD_YYYYMMDD.csv`: Additional CSV files for nested list fields (if any)

Where `YYYYMMDD` is the date when the data was fetched.

## Data Source

The data is sourced from the IFRC GO Platform API:
- Base URL: https://goadmin.ifrc.org/api/v2/country/

## License

MIT License

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

## Acknowledgments

- International Federation of Red Cross and Red Crescent Societies (IFRC) for providing the API
