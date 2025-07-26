from typing import List

from pydantic import BaseModel, Field


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

    name: str = Field(description="Name of the recipe")
    ingredients: List[str] = Field(description="List of ingredients")
    instructions: List[str] = Field(description="Step-by-Step cooking instruction")
    cooking_time: str = Field(description="Cooking time")
    servings: int = Field(description="Number of servings")

    def format_str(self) -> str:
        """Format a Recipe object into a readable string.

        This method formats the recipe as a Markdown string with
        sections for the name, ingredients, instructions, cooking time,
        and servings.

        Returns:
            A formatted Markdown string representation of the recipe
        """
        result = f"# {self.name}\n\n"
        result += "## Ingredients\n"
        for ingredient in self.ingredients:
            result += f"- {ingredient}\n"

        result += "\n## Instructions\n"
        for i, instruction in enumerate(self.instructions, 1):
            result += f"{i}. {instruction}\n"

        result += f"\n**Cooking Time:** {self.cooking_time}\n"
        result += f"**Servings:** {self.servings}\n"

        return result
