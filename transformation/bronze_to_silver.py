from pathlib import Path
import pyarrow.parquet as pq
import duckdb
import pyarrow as pa

directory_root = str(Path(__file__).parent.parent)

def fred_bronze_to_silver_transformation():
    path = directory_root + '/storage/bronze/fred_data.parquet'
    duckdb.sql(F"CREATE TABLE bronze_fred_table AS SELECT * FROM '{path}'")
    duckdb.sql("COPY (WITH CTE AS (SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_fred_table)"
                "SELECT * EXCLUDE(observations), unnest(observations, recursive := true) FROM CTE)"
               f" TO '{directory_root}/storage/silver/fred_data.parquet'" )

def historical_market_bronze_to_silver_transformation():
    path = directory_root + '/storage/bronze/historical_stock_data.parquet'
    duckdb.sql(F"CREATE TABLE bronze_historical_market_table AS SELECT * FROM '{path}'")
    duckdb.sql("COPY (SELECT * EXCLUDE(api_data), unnest(api_data, recursive := true) FROM bronze_historical_market_table)"
                     f" TO '{directory_root}/storage/silver/historical_stock_data.parquet'")
def sec_bronze_to_silver_transformation():
    path = directory_root + '/storage/bronze/sec_data.parquet'
    table = pq.read_table(path)
    data_list = table.to_pylist()

    duckdb.sql(
        "CREATE TABLE bronze_historical_sec_table ("
        "load_date DATE, "
        "cik BIGINT, "
        "concept VARCHAR, "
        "start_date DATE, "
        "end_date DATE, "
        "value DOUBLE, "
        "accn VARCHAR, "
        "fy INTEGER, "
        "fp VARCHAR, "
        "form VARCHAR, "
        "filed DATE, "
        "frame VARCHAR"
        ")"
    )
    rows = []
    row_count_checksum = []
    for element in data_list:
        row_count = 0
        for ConceptFact,Data in element['api_data'].items():
            units = Data.get('units') if isinstance(Data, dict) else None
            if not units:
                continue
            for unit, items in units.items():
                if not items:
                    continue
                for item in items:
                    rows.append({
                        "load_date": element['load_date'],
                        "cik": element['cik'],
                        "taxonomy": 'us-gaap',
                        "conceptfact": ConceptFact,
                        "unit": unit,
                        "start_date": item.get('start'),
                        "end_date": item.get('end'),
                        "value": item.get('val'),
                        "accountnum": item.get('accn'),
                        "fy": item.get('fy'),
                        "fp": item.get('fp'),
                        "form": item.get('form'),
                        "filed": item.get('filed'),
                        "frame": item.get('frame'),
                    })
                    row_count += 1
        row_count_checksum.append((element['cik'], row_count))

    for i in range(len(data_list)):
        raw_checksum = data_list[i]['cik'], data_list[i]['row_count']
        silver_checksum = row_count_checksum[i][0], row_count_checksum[i][1]
        if not row_count_check(raw_checksum, silver_checksum):
            return False

    table = pa.Table.from_pylist(rows)
    pq.write_table(table, f'{directory_root}/storage/silver/historical_sec_data.parquet')
    return None
def row_count_check(raw_checksum, silver_checksum):
    "Compares row count from raw api data (pre-transformation) and row count post transformation"
    if raw_checksum[1] != silver_checksum[1]:
        print(f"CIK{raw_checksum[0]} does not match, raw row count shows {raw_checksum[1]} and"
              f"silver row count shows {silver_checksum[1]}")
        return False
    return True

def delete_db_tables():
    """
    Function to delete duckdb tables that are used for bronze to silver transformations
    """
    duckdb.sql("DROP TABLE IF EXISTS bronze_fred_table;")
    duckdb.sql("DROP TABLE IF EXISTS bronze_historical_market_table;")
    duckdb.sql("DROP TABLE IF EXISTS bronze_historical_sec_table;")

if __name__ == '__main__':
    #fred_bronze_to_silver_transformation()
    #historical_market_bronze_to_silver_transformation()
    sec_bronze_to_silver_transformation()
    delete_db_tables()
