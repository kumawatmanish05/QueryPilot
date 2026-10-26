import re 

def validate_read_only_sql(sql : str) -> tuple[bool ,str]:
    """Perform basic checks on a read -only SQL Query."""

    if not sql or not sql.strip():
        return False,"SQL query cannot be empty."

    normalized_sql = sql.strip()

    #Allow at most one trailing semicolon.
    normalized_sql = normalized_sql.rstrip(";").strip()

    #Reject multiple SQL Statements
    if ";" in normalized_sql:
        return False , "Multiple SQL Statements are not allowed."

    # Only Allow SELECT queries at this Stage.
    if not re.match(r"^SELECT\b",normalized_sql,re.IGNORECASE):
        return False ,"ONLy SELECT queries are allowed."

    return True , "Query Passed basic Validation"
