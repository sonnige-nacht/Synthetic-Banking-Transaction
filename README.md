# Synthetic Banking Transaction Fraud Detection

An end-to-end portfolio project exploring synthetic banking transactions and building a fraud classifier. The work combines Python-based exploration, SQL Server data preparation, behavioral feature engineering, and a LightGBM model tuned with Optuna.

## Project workflow

1. Explore the CSV for data types, missing values, duplicates, and sample records.
2. Load the CSV into SQL Server in chunks and define `raw`, `stg`, and `dw` schemas.
3. Inspect staging columns, derive transaction-time features, and create a fraud-modeling view.
4. Explore fraud patterns and engineer customer, card, and device behavior features.
5. Train and tune a LightGBM classifier using a chronological 70/15/15 train, validation, and test split. Select a classification threshold on validation data, then evaluate it on the test set.

## Reported results

The modeling notebook reports the following test-set results for the tuned model at a threshold of 0.90. These are saved notebook results, not a fresh reproduction.

| Metric | Test result |
| --- | ---: |
| Average precision (reported as PR-AUC) | 0.6238 |
| Precision | 0.8462 |
| Recall | 0.5628 |
| F1-score | 0.6760 |
| False positive rate | 0.000147 |
| True positives / false positives | 121 / 22 |
| False negatives / true negatives | 94 / 149,763 |

The test set is highly imbalanced: 215 out of 150,000 transactions are labeled fraudulent. These results describe this synthetic dataset and should not be interpreted as evidence of real-world performance.

## Repository layout

```text
.
??? datasets/
?   ??? DATASET.txt
?   ??? raw/                  # Downloaded CSV goes here
??? python/                   # Exploration, SQL loader, and modeling
??? sql/                      # SQL Server preparation and modeling view
??? .gitignore
??? FILE_STRUCTURE.txt
??? README.md
??? requirements.txt
```

## Dataset

This project uses [Synthetic Banking Transaction Dataset with Multi-Pattern Fraud Labels for Machine Learning Research](https://data.mendeley.com/datasets/ktbthg777x/2), version 2, by Md Mehedi Hasan and Maria Rashid (DOI: 10.17632/ktbthg777x.2). The dataset is published on Mendeley Data under the CC BY 4.0 license.

The dataset is not included in this repository because of its size. To run the project:

1. Open the dataset page linked above and download the dataset.
2. Extract the downloaded archive.
3. Place `Fraud Detection Dataset.csv` in `datasets/raw/`.

The CSV and downloaded archive are excluded from Git. See `datasets/DATASET.txt` for the source and expected location. The dataset is synthetic; model results should not be assumed to generalize to real banking transactions.

## Setup

Prerequisites: Python, a running Microsoft SQL Server instance, ODBC Driver 17 for SQL Server, and permission to create schemas and tables. Create the source and warehouse databases before loading data. From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DB_HOST = "localhost"
$env:DB_USER = "your_sql_user"
$env:DB_PASSWORD = "your_password"
jupyter notebook
```

Set these environment variables in the same session before launching the loader or Jupyter. The loader targets `synthetic_banking_transaction_db` and the modeling notebook targets `synthetic_banking_transaction_datawarehouse`; adjust database names, port, and ODBC driver in those files if needed. Use a disposable database: the loader uses `if_exists="replace"` for the transactions table and will replace it on repeated runs.

Open `python/01_data_exploration.ipynb`, then run `python python/02_load_to_database_MicrosoftSQL.py`. Run the SQL scripts in numerical order in the appropriate database using a SQL Server client. Finally, open `python/07_ML_fraud_detection.ipynb` after preparing the warehouse described below. SQL statements that add columns or create a view are not all safe to rerun unchanged.

## Reproduction limitations

The files do not contain a complete pipeline from the loaded `dbo.transactions` table to the `stg.transactions`, `stg.fraud_status`, `dw.transactions`, and `dw.fraud_status` tables referenced by the SQL scripts. The dataset must be transformed and loaded into those tables, with the columns expected by the scripts, before the cleaning script and modeling view can run. The scripts also do not create the databases. Some notebook cells may require adjustment for library versions or execution order; dependencies are listed without pinned versions. No SQL Server execution or model retraining was performed while preparing this repository.

## Technologies

Python, pandas, NumPy, SQLAlchemy, pyodbc, Microsoft SQL Server, Jupyter, scikit-learn, LightGBM, and Optuna.
