import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict, List

import pandas as pd
from copilotkit.langgraph import copilotkit_emit_state
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from tenacity import retry, stop_after_attempt, wait_exponential
from typing_extensions import Annotated

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "sqlite-sakila.db"


class SQLiteDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query with retry logic."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn)
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def get_schema(self) -> Dict[str, List[str]]:
        """Get the database schema."""
        schema = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                schema[table_name] = [col[1] for col in columns]
        return schema


# Initialize database
db = SQLiteDatabase(DB_PATH)


@tool(description="Get the database schema", return_direct=False)
async def get_schema(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Any, InjectedState],
) -> str:
    """Get the database schema."""
    schema = db.get_schema()
    return json.dumps(schema, indent=2)


@tool(description="Run a query on the database", return_direct=True)
async def run_query(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Any, InjectedState],
    config: RunnableConfig,
    query: str,
) -> str:
    """Run a SQL query on the database with retry logic."""
    await copilotkit_emit_state(config, {"progress": "Running query..."})
    try:
        result = db.execute_query(query)
        return result.to_json(orient="records")
    except Exception as e:
        return f"Error executing query: {str(e)}"


TOOLS: List[Callable[..., Any]] = [get_schema, run_query]
