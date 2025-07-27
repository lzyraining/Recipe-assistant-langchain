from dataclasses import dataclass
from typing import Dict


@dataclass
class ToolCall:
    name: str
    tool_call_id: str
    tool_response: str
    tool_args: Dict
