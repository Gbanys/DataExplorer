from pandas import DataFrame
from typing_extensions import Annotated
from langchain_core.tools import tool, InjectedToolArg
from pandasai import SmartDataframe
from agent.llm import pandas_llm
import pandas as pd

import uuid
from pathlib import Path

def create_pandas_ai_tool(dataframe: pd.DataFrame):

    @tool
    def retrieve_pandas_ai_response(prompt: str) -> str:
        """A tool used for analyzing datasets.
        prompt is a command or a question for a data analyzer.
        The dataframe parameter is referencing a global variable so ignore it and do not overwrite it.
        """
        smart_dataframe = SmartDataframe(dataframe, config={"llm": pandas_llm})
        result = str(smart_dataframe.chat(prompt))
        
        # If PandasAI returned a file path, rename it to something unique
        path = Path(result)
        if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif") and path.exists():
            # Generate a new filename in the same directory
            new_path = path.with_name(f"{path.stem}_{uuid.uuid4().hex}{path.suffix}")
            path.rename(new_path)
            return str(new_path)

        # Otherwise just return the original text
        return result

    return retrieve_pandas_ai_response