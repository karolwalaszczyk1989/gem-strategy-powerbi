import requests
import pandas as pd
from io import StringIO
import os
from dotenv import load_dotenv
from datetime import date


load_dotenv()


# --- CONFIGURATION ---

TICKERS = [
    {"stooq": "cndx.uk", "db": "CNDX.UK"},
    {"stooq": "cspx.uk", "db": "CSPX.UK"},
    {"stooq": "iwda.uk", "db": "IWDA.UK"},
    {"stooq": "eimi.uk", "db": "EIMI.UK"},
    {"stooq": "vfem.uk", "db": "VFEM.UK"},
    {"stooq": "cbu0.uk", "db": "CBU0.UK"},
    {"stooq": "idtl.uk", "db": "IDTL.UK"},
    {"stooq": "ib01.uk", "db": "IB01.UK"},
]

SOURCE = "stooq"
TARGET_TABLE = "gem_prices_daily"

PARQUET_PATH = r"C:\Users\Wally\OneDrive\GEM\gem_prices_daily.parquet"



def build_stooq_url(ticker: str) -> str:
    """
    Build CSV download URL for stooq.pl (direct download).
    Example:
    input:  cndx.uk
    output: https://stooq.pl/q/d/l/?s=cndx.uk&i=d
    """
    base_url = "https://stooq.pl/q/d/l/"
    return f"{base_url}?s={ticker}&i=d"

#------------------------------------------------------------------#

def download_stooq_csv(url: str) -> str:
    """
    Download CSV content from stooq.pl.
    Returns raw CSV text.
    Raises exception if download fails.
    """
    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(f"HTTP error {response.status_code} for URL: {url}")

    if not response.text or "Brak danych" in response.text:
        raise RuntimeError(f"Empty or invalid CSV for URL: {url}")

    return response.text

#-------------------------------------------------------------------#

def parse_stooq_csv(csv_text: str) -> pd.DataFrame:
    """
    Parse raw CSV text from stooq.pl into a normalized DataFrame.
    """
    df = pd.read_csv(
        StringIO(csv_text),
        sep=","
    )

    return df

# ------------------------------------------------------------------#

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename stooq CSV columns to database-compatible names.
    """
    column_mapping = {
        "Data": "price_date",
        "Otwarcie": "open_price",
        "Najwyzszy": "high_price",
        "Najnizszy": "low_price",
        "Zamkniecie": "close_price",
        "Wolumen": "volume",
    }

    df = df.rename(columns=column_mapping)

    return df
#Pandas ogarnia kolumny
#-------------------------------------------------------------------#

def add_metadata_columns(df: pd.DataFrame, ticker: str, source: str) -> pd.DataFrame:
    """
    Add ticker and source columns required by the database schema.
    """
    df["ticker"] = ticker
    df["source"] = source

    return df
#dodajemy kolumny których nie ma w CSV za pomocą Pandas
#------------------------------------------------------------------#

def convert_price_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert price_date column to datetime.date.
    """
    df["price_date"] = pd.to_datetime(df["price_date"], errors="coerce").dt.date
    return df

#-------------------------------------------------------------------#

def drop_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with missing critical values.
    """
    df = df.dropna(subset=[
        "price_date",
        "close_price"
    ])
    return df

#-------------------------------------------------------------------#

def sort_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort DataFrame by price_date ascending.
    """
    return df.sort_values("price_date")


import mysql.connector


def test_mysql_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    print("Połączenie z MySQL OK")

    connection.close()
#Czy łączymy się z baza danych ?
#---------------------------------------------------#

def test_mysql_select_1():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor()
    cursor.execute("SELECT 1")

    result = cursor.fetchone()
    print("SELECT 1 result:", result)

    cursor.close()
    connection.close()
#czy cokolwiek zrobimy z bazą? select 1 jako najprostsza interkacja
#--------------------------------------------------#

def test_mysql_count_rows():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM gem_prices_daily")

    result = cursor.fetchone()
    print("Row count in gem_prices_daily:", result[0])

    cursor.close()
    connection.close()
#prosty test z count - działa
#------------------------------------------------#

def test_mysql_select_sample():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM gem_prices_daily
        ORDER BY price_date DESC
        LIMIT 5
    """
    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    connection.close()
#Testujemy czy zczytamy dane z SQL 5 wierszy
#-------------------------------------------------------------#


def insert_single_row(row):
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor()

    sql = """
        INSERT IGNORE INTO gem_prices_daily (
            price_date,
            ticker,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            source
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        row["price_date"],
        row["ticker"],
        row["open_price"],
        row["high_price"],
        row["low_price"],
        row["close_price"],
        int(row["volume"]),
        row["source"]
    )

    print("INSERT VALUES:", values)

    cursor.execute(sql, values)
    connection.commit()

    cursor.close()
    connection.close()

    print("INSERT OK")
#test pojedynczego wiersza - udany
#--------------------------------------------------#

def insert_batch(df: pd.DataFrame):
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor()

    sql = """
        INSERT IGNORE INTO gem_prices_daily (
            price_date,
            ticker,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            source
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
#Zapytanie do SQL, dodałem IGNORE aby nie nadpisywało się jeśli primary key już był.
    #ma to przyspieszyć pracę przez brak nadpisywania
    values = [
        (
            row.price_date,
            row.ticker,
            float(row.open_price),
            float(row.high_price),
            float(row.low_price),
            float(row.close_price),
            int(row.volume),
            row.source
        )
        for row in df.itertuples(index=False)
    ]

    print(f"Prepared {len(values)} rows for batch insert")

    cursor.executemany(sql, values)
    connection.commit()

    cursor.close()
    connection.close()

    print("BATCH INSERT OK")

#Batch po jednym pełnym tickerze

#-----------------------------------------------------------------------#

def drop_today_rows(df: pd.DataFrame) -> pd.DataFrame:
    today = date.today()
    return df[df["price_date"] < today]

#ignoruję dzień dzisiejszy, bo ma dynamiczną cenę zamknięcia
#----------------------------------------------------------------------#


def run_etl_for_all_tickers():
    all_data = []  # <- zbieramy dane pod Parquet

    for cfg in TICKERS:
        print(f"--- Processing {cfg['db']} ---")

        url = build_stooq_url(cfg["stooq"])
        csv_text = download_stooq_csv(url)

        df = parse_stooq_csv(csv_text)
        df = normalize_columns(df)
        df = add_metadata_columns(df, cfg["db"], SOURCE)
        df = convert_price_date(df)
        df = drop_today_rows(df)
        df = drop_invalid_rows(df)
        df = sort_by_date(df)

        insert_batch(df)

        all_data.append(df)  # <- dokładamy snapshot

        print(f"--- Finished {cfg['db']} ---\n")

    # ===== SNAPSHOT DO PARQUET (Power BI) =====
    final_df = pd.concat(all_data, ignore_index=True)

    final_df.to_parquet(
        PARQUET_PATH,
        index=False
    )

    print(f"Parquet snapshot zapisany: {PARQUET_PATH}")


#batch po wszystkich tickerach. plus zapis do pliku na OneDrive


if __name__ == "__main__":
    run_etl_for_all_tickers()


