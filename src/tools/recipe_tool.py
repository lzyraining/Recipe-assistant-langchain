import json
import logging
from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.apis import get_api_client

logger = logging.getLogger(__name__)


class Recipe(BaseModel):
    """Recipe model for storing recipe information.

    This class represents a recipe with its name, ingredients,
    instructions, cooking time, and number of servings.

    Attributes:
        name: The name of the recipe
        ingredients: List of ingredients required for the recipe
        instructions: Step-by-step cooking instructions
        cooking_time: The time required to cook the recipe
        servings: The number of servings the recipe makes
    """

    title: str = Field(description="Name of the recipe")
    ingredients: List[str] = Field(description="List of ingredients")
    instructions: List[str] = Field(description="Step-by-Step cooking instruction")
    servings: str = Field(description="Number of servings")

class RecipeRequest(BaseModel):
    name: str = Field(description="Name of the recipe")


@tool("get_recipe", args_schema=RecipeRequest)
def get_recipe(name: str) -> str:
    """Get recipe from a meal name

    Args:
        name: meal name which needs recipe

    Returns:
        Recipe: JSON string of the recipe
    """
    api_client = get_api_client()
    response = api_client.get_recipe(name)
    data = json.loads(response)[0]
    logger.info(data)

    ingredients = [
        ingredient.strip()
        for ingredient in data["ingredients"].replace("INGREDIENTS:", "").split("|")
        if ingredient.strip()
    ]

    instructions = [
        instruction.strip()
        for instruction in data["instructions"].replace("'DIRECTIONS:", "").split("|")
        if instruction.strip()
    ]

    recipe = Recipe(
        title=data["title"],
        ingredients=ingredients,
        instructions=instructions,
        servings=data["servings"],
    ).model_dump_json(indent=2)

    logger.info(f"Recipe found: {recipe}")
    return recipe
