from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ToolCall:
    name: str
    tool_call_id: str
    tool_args: Dict
    tool_response: Optional[str] = None  # None before execution, populated after
