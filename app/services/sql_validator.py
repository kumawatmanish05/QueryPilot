import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

def validate_read_only_sql(sql : str) -> tuple[bool,str]:
    """Perform basic structral checks on a read -only SQL query."""

    if not sql or not sql.strip():
        return False,"SQL query cannot be empty."

    try:
        statements = sqlglot.parse(sql , read = "sqlite")
    except ParseError:
        return False ,"Invalid SQL Syntax."

    #Ingnore empty statements , such as extra trailing semicolons.
    statements = [statement for statement in statements if statement is not None]

    if len(statements) !=1:
        return False , "Exactly one SQL statement is required"

    statement = statements[0]

    if not isinstance(statement , exp.Select):
        return False ,"Only SELECT queries are allowed"

    return True ,"Query passed Structural Validation."