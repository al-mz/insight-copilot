import re
from typing import List

from IPython.display import Image, display
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


def parse_inf_file(inf_path: str) -> List[str]:
    """
    Parse a PSCAD .inf file and extract column descriptions.

    Args:
        inf_path (str): Path to the .inf file

    Returns:
        List[str]: List of column descriptions in order
    """
    column_names = []
    pgb_pattern = re.compile(r'PGB\(\d+\)\s+Output\s+Desc="([^"]+)"')

    try:
        with open(inf_path, "r") as f:
            for line in f:
                match = pgb_pattern.search(line)
                if match:
                    column_names.append(match.group(1))
    except Exception as e:
        print(f"Error parsing .inf file {inf_path}: {e}")

    return column_names


def save_graph_diagram(graph, filename="graph.png"):
    """
    Generate and save a graph of the given graph.

    Args:
        graph: The graph to be depicted.
        filename: The name of the file to save the graph as.
    """
    try:
        graph = graph.get_graph(xray=True).draw_mermaid_png()
        with open(filename, "wb") as f:
            f.write(graph)
        display(Image(filename))
    except Exception as e:
        print(f"An error occurred while generating the graph: {e}")


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)
