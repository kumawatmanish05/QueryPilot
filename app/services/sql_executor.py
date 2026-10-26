from sqlalchemy import text

from app.core.database import engine 

def execute_read_only_query(sql:str) -> list[dict]:
    """Execute a read-only SQL Query and return rows as dictionaries"""

    with engine.connect() as connection:
        result = connection.execute(text(sql))
        rows = result.mappings().all()

    return [dict(row) for row in rows]

if __name__ == "__main__":
    query = """
    SELECT product , SUM(quantity * unit_price) AS revenue
    FROM sales
    GROUP BY product
    ORDER BY revenue DESC
    """

    results = execute_read_only_query(query)

    for row in results :
        print(row)