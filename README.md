# Project Title

## Description

This project is designed to filter and process records from various data sources, including JSON files, MongoDB, and MySQL databases.

## Features

- Fully automated dummy record generation
- Allows options to store data on local Mongo or SQL
- Filter records from JSON files
- Filter records from MongoDB
- Filter records from MySQL
- Process and transform records
- Logging and error handling
- Codebase is fully secured and well writen and readable
- Codebase uses well known pre-commit hooks to achieve security in code

## Setup

### Prerequisites

- Python
- MongoDB (Optional)
- MySQL (Optional)

### Installation

1. Clone the repository:
2. Create a virtual environment and activate it:
3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    pip install -r dev-requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file referring `.env.sample` file

### Commands

1. Generate dummy records to work with the project. Here flags for Mongo and SQL are optional.
    
    ```sh
    python app/utils/record_generator.py --number_of_records 100 --store_to_mongodb True --store_to_sql True
    ```

2. Once records are generated successfully, start the API server.

    ```sh
    python debug.py
    ```