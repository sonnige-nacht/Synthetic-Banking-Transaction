import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from tqdm import tqdm

try:
    from IPython.display import display
except ImportError:
    display = print

print("Libraries loaded")


# -------------------------------------------- Database connection settings ------------------------------------------- #

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = "1433"
DB_NAME = "synthetic_banking_transaction_db"

DB_DRIVER = "ODBC Driver 17 for SQL Server"

connection_params = (
    f"DRIVER={{{DB_DRIVER}}};"
    f"SERVER={DB_HOST},{DB_PORT};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=yes;"
)

DATABASE_URL = (
    f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_params)}"
)

engine = create_engine(
    DATABASE_URL,
    fast_executemany=True
)

print(f"Engine created for SQL Server database: {DB_NAME}")


# -------------------------------------------- Test database connection ------------------------------------------- #

try:
    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT @@VERSION;")
        )

        version = result.fetchone()[0]

        print(
            f"Connection successful!\n"
            f"SQL Server Version:\n{version}"
        )

except Exception as e:
    print(f"Connection error: {e}")


# ------------------------------------------------- CSV folder path -------------------------------------------------- #

CSV_FOLDER = Path(__file__).resolve().parents[1] / "datasets" / "raw"

if CSV_FOLDER.exists():

    csv_files = list(CSV_FOLDER.glob("*.csv"))

    print("Folder found")
    print(f"Number of CSV files: {len(csv_files)}")

    for f in csv_files:
        print(f"  - {f.name}")

else:

    print(f"Folder not found: {CSV_FOLDER}")


# -------------------------------------------- Define file to table mapping ------------------------------------------- #

FILE_TABLE_MAPPING = {

    "Fraud Detection Dataset.csv": "transactions"

}

print("Mapping defined")


# -------------------------------------------- Load CSV to SQL Server ------------------------------------------- #

def load_csv_to_sqlserver(
    csv_path,
    table_name,
    engine,
    if_exists="replace",
    chunksize=10000
):
    """
    Load CSV file into SQL Server using chunks
    and display a graphical progress bar.
    """

    try:

        # -------------------------------------------------
        # Calculate total number of rows
        # -------------------------------------------------

        with open(
            csv_path,
            "r",
            encoding="utf-8"
        ) as f:

            total_rows = sum(
                1 for _ in f
            ) - 1


        # -------------------------------------------------
        # Read CSV in chunks
        # -------------------------------------------------

        chunks = pd.read_csv(
            csv_path,
            chunksize=chunksize
        )


        first_chunk = True
        loaded_rows = 0


        # -------------------------------------------------
        # Progress bar
        # -------------------------------------------------

        with tqdm(
            total=total_rows,
            desc=f"Loading {table_name}",
            unit="rows",
            leave=True
        ) as progress_bar:


            for chunk in chunks:


                # -----------------------------------------
                # First chunk -> replace table
                # Other chunks -> append
                # -----------------------------------------

                if first_chunk:

                    current_if_exists = if_exists

                    first_chunk = False

                else:

                    current_if_exists = "append"


                # -----------------------------------------
                # Send chunk to SQL Server
                # -----------------------------------------

                chunk.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists=current_if_exists,
                    index=False
                )


                # -----------------------------------------
                # Update progress
                # -----------------------------------------

                loaded_rows += len(chunk)

                progress_bar.update(
                    len(chunk)
                )


        return loaded_rows, None


    except Exception as e:

        return 0, str(e)


print("Loading function ready")


# -------------------------------------------- Start data loading ------------------------------------------- #

print("\nStarting data load...\n")

results = []


for csv_file, table_name in FILE_TABLE_MAPPING.items():

    csv_path = CSV_FOLDER / csv_file


    # -------------------------------------------------
    # Check file existence
    # -------------------------------------------------

    if not csv_path.exists():

        print(
            f"File not found: {csv_file}"
        )

        results.append({

            "file": csv_file,

            "table": table_name,

            "rows": 0,

            "status": "NOT_FOUND"
        })

        continue


    print(
        f"\nLoading: {csv_file} -> {table_name}"
    )


    # -------------------------------------------------
    # Load file
    # -------------------------------------------------

    row_count, error = load_csv_to_sqlserver(

        csv_path=csv_path,

        table_name=table_name,

        engine=engine,

        if_exists="replace",

        chunksize=10000
    )


    # -------------------------------------------------
    # Check result
    # -------------------------------------------------

    if error:

        print(
            f"   Error: {error}\n"
        )

        results.append({

            "file": csv_file,

            "table": table_name,

            "rows": 0,

            "status": f"ERROR: {error}"
        })


    else:

        print(
            f"   Success! "
            f"{row_count:,} rows loaded\n"
        )

        results.append({

            "file": csv_file,

            "table": table_name,

            "rows": row_count,

            "status": "SUCCESS"
        })


# -------------------------------------------- Loading summary ------------------------------------------- #

df_results = pd.DataFrame(
    results
)

print("\nLoading Summary:")

display(
    df_results
)


total_rows = df_results[
    "rows"
].sum()


success_count = (
    df_results["status"] == "SUCCESS"
).sum()


print(
    f"\n{success_count}/"
    f"{len(FILE_TABLE_MAPPING)} "
    f"tables loaded successfully"
)


print(
    f"Total rows loaded: "
    f"{total_rows:,}"
)


# -------------------------------------------- List database tables ------------------------------------------- #

with engine.connect() as conn:

    result = conn.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'dbo'
            ORDER BY table_name;
            """
        )
    )

    tables = [
        row[0]
        for row in result
    ]


print(
    f"\nTables in database "
    f"({len(tables)} tables):"
)


for table in tables:

    print(
        f"  - {table}"
    )


# -------------------------------------------- Verify row counts ------------------------------------------- #

print("\nDatabase row counts:")


for table in sorted(tables):

    with engine.connect() as conn:

        result = conn.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM dbo.[{table}];
                """
            )
        )

        count = result.fetchone()[0]

        print(
            f"{table:.<40} "
            f"{count:>10,}"
        )


print(
    "\nAll set! "
    "Data loaded into SQL Server."
)