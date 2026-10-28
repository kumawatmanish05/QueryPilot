
from pathlib import Path
import re 

import pandas as pd
from sqlalchemy import text

from app.core.database import engine


DATA_PATH = Path("data/sample_sales.csv")


def load_csv_to_table(csv_path: str, 
                      table_name: str , 
                      database_engine=None) -> int:
    csv_file = Path(csv_path)

    if not csv_file.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_file}")

    df = pd.read_csv(csv_file)

    if df.empty:
        raise ValueError("Dataset is empty.")

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("Invalid Table name.")

    if database_engine is None:
        database_engine = engine

    with database_engine.begin() as connection:
        df.to_sql(
            name=table_name,
            con=connection,
            if_exists="replace",
            index=False,
        )

        count = connection.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar_one()

    return count

if __name__ == "__main__":
    rows_loaded = load_csv_to_table(
        csv_path="data/sample_sales.csv",
        table_name="sales",
    )
    print(f"Successfully loaded {rows_loaded} rows.")