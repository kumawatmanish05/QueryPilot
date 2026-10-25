
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.core.database import engine


DATA_PATH = Path("data/sample_sales.csv")


def load_sample_data() -> int:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    if df.empty:
        raise ValueError("Dataset is empty.")

    with engine.begin() as connection:
        df.to_sql(
            name="sales",
            con=connection,
            if_exists="replace",
            index=False,
        )

        count = connection.execute(
            text("SELECT COUNT(*) FROM sales")
        ).scalar_one()

    return count


if __name__ == "__main__":
    rows_loaded = load_sample_data()
    print(f"Successfully loaded {rows_loaded} rows into the sales table.")
