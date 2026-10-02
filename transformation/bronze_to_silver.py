from pathlib import Path
import pyarrow.parquet as pq
import duckdb

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
    for element in data_list:
        for ConceptFact,Data in element['api_data'].items():
            try:
                for DataKey,DataValue in Data['units'].items():
                    for item in DataValue:
                        row = []
                        row = [element['load_date'], element['cik'], ConceptFact, item.get('start'), item.get('end'),
                               item.get('val'), item.get('accn'), item.get('fy'), item.get('fp'), item.get('form'),
                               item.get('filed'), item.get('frame')]
                        rows.append(row)
            except TypeError:
                print(list(data_list[0]['api_data'].keys()))
                break

def delete_db_tables():
    """
    Function to delete duckdb tables that are used for bronze to silver transformations
    """
    duckdb.sql("DROP TABLE IF EXISTS bronze_fred_table;")
    duckdb.sql("DROP TABLE IF EXISTS bronze_historical_market_table;")

if __name__ == '__main__':
    #fred_bronze_to_silver_transformation()
    #historical_market_bronze_to_silver_transformation()
    sec_bronze_to_silver_transformation()
    #delete_db_tables()
