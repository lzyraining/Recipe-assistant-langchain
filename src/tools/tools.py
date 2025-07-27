from typing import List

from langchain_core.tools import Tool

from .recipe_tool import get_recipe


class Tools:

    @staticmethod
    def available_tools() -> List[Tool]:
        return [get_recipe]

    @staticmethod
    def tool_registry():
        return {"get_recipe": get_recipe}
