from typing import Any, Dict, List

import pandas as pd


def process_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert list of dictionaries to pandas DataFrame."""
    return pd.DataFrame(data)


def generate_sql_query(natural_language_query: str) -> str:
    """Convert natural language query to SQL query."""
    # TODO: Implement query generation logic
    return "SELECT * FROM data LIMIT 10"


def format_response(data: pd.DataFrame) -> Dict[str, Any]:
    """Format DataFrame response for API."""
    return {
        "columns": data.columns.tolist(),
        "data": data.to_dict(orient="records"),
        "summary": {"row_count": len(data), "column_count": len(data.columns)},
    }
