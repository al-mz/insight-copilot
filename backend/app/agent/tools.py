import base64
import json
import sqlite3
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, List, Optional

import httpx
import pandas as pd
import plotly.graph_objects as plt
from copilotkit.langgraph import copilotkit_emit_state
from langchain_core.messages import ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from typing_extensions import Annotated

# Database path
DB_PATH = Path(__file__).parent.parent / "database" / "powersim.db"
API_BASE_URL = "http://localhost:8000/api"  # Updated to include /api prefix


@tool(description="Extracts signal types and their descriptions from the SQLite database.", return_direct=False)
async def get_signal_types(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Any, InjectedState],
) -> str:
    """
    Extract distinct signal types and their descriptions from the SQLite database.

    Returns:
        dict: Dictionary containing signal types and their descriptions
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query for distinct signal types and their descriptions
        cursor.execute(
            """
            SELECT DISTINCT
                s.name as signal_name,
                s.description as signal_description,
                s.unit as signal_unit,
                sc.name as case_name
            FROM signals s
            JOIN simulation_cases sc ON s.case_id = sc.id
            ORDER BY s.name, sc.name
        """
        )

        # Fetch all results
        results = cursor.fetchall()

        # Close the connection
        conn.close()

        # Organize results by signal type
        signal_types = {}
        for row in results:
            signal_name = row[0]
            if signal_name not in signal_types:
                signal_types[signal_name] = {"description": row[1], "unit": row[2], "cases": []}
            signal_types[signal_name]["cases"].append(row[3])

        # Convert signal_types to a string
        signal_types_str = json.dumps(signal_types, indent=4)

        return Command(
            update={
                "messages": [ToolMessage(signal_types_str, tool_call_id=tool_call_id)],
            }
        )

    except Exception as e:
        return Command(
            update={
                "messages": [ToolMessage(f"Error extracting signal types: {str(e)}", tool_call_id=tool_call_id)],
            }
        )


@tool
async def plot_signal_timeseries(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[Any, InjectedState],
    config: RunnableConfig,
    signal_name: str = None,
    case_name: str = None,
    signal_id: int = None,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    format: str = "interactive",
) -> str:
    """
    Plot time-series data for a specific signal within a given timeframe.

    If signal_id is provided, it will be used directly.
    If signal_name and case_name are provided, it will look up the signal_id.

    Args:
        tool_call_id: The ID for this tool call
        signal_name: Name of the signal to plot
        case_name: Name of the simulation case
        signal_id: ID of the signal (alternative to signal_name+case_name)
        start_time: Start time in seconds (optional)
        end_time: End time in seconds (optional)
        format: Output format - "interactive" for frontend plotting, "html" for interactive plot or "png" for static image

    Returns:
        str: JSON containing the plot data or error information
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Step 1: If signal_id is not provided, look it up by signal_name and case_name
        if signal_id is None:
            if signal_name is None or case_name is None:
                available_signals = get_available_signals(cursor)
                return json.dumps(
                    {
                        "success": False,
                        "error": "Either signal_id or both signal_name and case_name must be provided",
                        "available_signals": available_signals,
                    },
                    indent=4,
                )

            # Look up signal_id by name and case
            cursor.execute(
                """
                SELECT s.id
                FROM signals s
                JOIN simulation_cases sc ON s.case_id = sc.id
                WHERE s.name = ? AND sc.name = ?
            """,
                (signal_name, case_name),
            )

            result = cursor.fetchone()
            if not result:
                available_signals = get_available_signals(cursor)
                conn.close()
                return json.dumps(
                    {
                        "success": False,
                        "error": f"Signal '{signal_name}' in case '{case_name}' not found",
                        "available_signals": available_signals,
                    },
                    indent=4,
                )

            signal_id = result["id"]
            conn.close()

        # Step 2: Get signal metadata
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT s.name, s.description, s.unit, sc.name as case_name
            FROM signals s
            JOIN simulation_cases sc ON s.case_id = sc.id
            WHERE s.id = ?
        """,
            (signal_id,),
        )

        signal_info = cursor.fetchone()
        if not signal_info:
            available_signals = get_available_signals(cursor)
            conn.close()
            return json.dumps(
                {
                    "success": False,
                    "error": f"Signal with ID {signal_id} not found",
                    "available_signals": available_signals,
                },
                indent=4,
            )
        conn.close()

        # Step 3: Get timeseries data from API endpoint
        async with httpx.AsyncClient() as client:
            params = {}
            if start_time is not None:
                params["start_time"] = start_time
            if end_time is not None:
                params["end_time"] = end_time

            response = await client.get(f"{API_BASE_URL}/signals/timeseries/{signal_id}", params=params)
            if response.status_code != 200:
                return Command(
                    update={
                        "messages": [
                            ToolMessage(f"Error fetching timeseries data: {response.text}", tool_call_id=tool_call_id)
                        ],
                    }
                )

            data = response.json()
            timeseries = data["timeseries"]
            metadata = data["metadata"]

        # Convert to dataframe for easier plotting
        df = pd.DataFrame(timeseries)

        # Step 4: Create the plot
        fig = plt.Figure()
        fig.add_trace(plt.Scatter(x=df["timestamp"], y=df["value"], mode="lines"))

        # Add title and axis labels
        signal_name = signal_info["name"]
        case_name = signal_info["case_name"]
        unit = signal_info["unit"] or "N/A"

        fig.update_layout(
            title=f"{signal_name} from {case_name}",
            xaxis_title="Time (seconds)",
            yaxis_title=f"{signal_name} ({unit})",
            template="plotly_white",
        )

        # Initialize result_dict with common data - IMPORTANT: Define before any conditionals
        result_dict = {
            "success": True,
            "signal": {
                "id": signal_id,
                "name": signal_info["name"],
                "description": signal_info["description"],
                "unit": signal_info["unit"],
                "case": signal_info["case_name"],
            },
            "timerange": {
                "start": start_time or metadata["time_range"][0],
                "end": end_time or metadata["time_range"][1],
                "min_available": metadata["time_range"][0],
                "max_available": metadata["time_range"][1],
            },
            "data_points_count": metadata["returned_points"],
        }

        # Handle different output formats
        if format.lower() == "interactive":
            # Add frontend-specific data for interactive plotting
            result_dict["plot_data"] = {
                "x": df["timestamp"].tolist(),
                "y": df["value"].tolist(),
                "type": "scatter",
                "mode": "lines",
            }
            result_dict["layout"] = {
                "title": f"{signal_name} from {case_name}",
                "xaxis": {"title": "Time (seconds)"},
                "yaxis": {"title": f"{signal_name} ({unit or 'N/A'})"},
                "template": "plotly_white",
            }

            # search for last human message ID from the state with role "human"
            last_human_message_id = None
            for message in reversed(state.messages):
                if message.type == "human":  # Instead of message.type == "human"
                    # Found the last human message
                    last_human_message_id = message.id
                    break

            # Update state to include the plot data
            plot_data_dict = {
                "plot_data": result_dict["plot_data"],
                "layout": result_dict["layout"],
                "last_human_message_id": last_human_message_id,  # Add message ID to associate the plot to the user's message
            }

            # Append the dictionary to the data list instead of trying to assign directly
            if hasattr(state, "data"):
                state.data.append(plot_data_dict)
            else:
                # This should never happen, but just in case
                state.data = [plot_data_dict]

            # Emmit state to the frontend
            await copilotkit_emit_state(config, state)

            # For interactive format, return a success message and the data will be accessible
            # in the message history for the frontend to use
            # return json.dumps(result_dict, indent=4)
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            "Successfully fetched and plotted signal timeseries data",
                            tool_call_id=tool_call_id,
                        )
                    ],
                    "data": state.data,
                }
            )

        elif format.lower() == "html":
            # Create a temporary HTML file
            html_path = Path(__file__).parent.parent / "temp" / f"plot_{signal_id}_{int(time.time())}.html"

            # Make sure the directory exists
            html_path.parent.mkdir(exist_ok=True)

            # Write the HTML file
            fig.write_html(str(html_path))

            # Add the file path to the result
            result_dict["plot_html_path"] = str(html_path)

            # Optionally include the HTML content directly
            with open(html_path, "r") as f:
                html_content = f.read()

            result_dict["plot_html"] = html_content[:10000] + "..." if len(html_content) > 10000 else html_content

            # Return success message with the path to the HTML file
            return Command(
                update={
                    "messages": [ToolMessage(json.dumps(result_dict, indent=4), tool_call_id=tool_call_id)],
                }
            )

        else:  # Default to PNG format
            # Generate PNG image
            buffer = BytesIO()
            fig.write_image(buffer, format="png")
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode()
            result_dict["plot_image"] = img_str

            # Return success message with the base64-encoded image
            return Command(
                update={
                    "messages": [ToolMessage(json.dumps(result_dict, indent=4), tool_call_id=tool_call_id)],
                }
            )

    except Exception as e:
        return Command(
            update={
                "messages": [ToolMessage(f"Error plotting signal timeseries: {str(e)}", tool_call_id=tool_call_id)],
            }
        )


def get_available_signals(cursor):
    """Helper function to get a list of available signals and cases."""
    cursor.execute(
        """
        SELECT
            s.id, s.name, sc.name as case_name
        FROM signals s
        JOIN simulation_cases sc ON s.case_id = sc.id
        ORDER BY sc.name, s.name
    """
    )

    return [{"id": row["id"], "name": row["name"], "case": row["case_name"]} for row in cursor.fetchall()]


TOOLS: List[Callable[..., Any]] = [get_signal_types, plot_signal_timeseries]
