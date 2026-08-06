import logging
from typing import Dict, Any, Callable, List, Optional

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for AI function tools (both server-executed and client-dispatched)."""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._executors: Dict[str, Callable] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        is_client_side: bool = False,
        executor: Optional[Callable] = None
    ):
        schema = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self._tools[name] = {
            "schema": schema,
            "is_client_side": is_client_side
        }
        if executor:
            self._executors[name] = executor

    def get_openai_tools_schema(self) -> List[Dict[str, Any]]:
        return [t["schema"] for t in self._tools.values()]

    def is_client_tool(self, name: str) -> bool:
        return self._tools.get(name, {}).get("is_client_side", False)

    async def execute(self, name: str, args: Dict[str, Any]) -> Any:
        if name in self._executors:
            try:
                executor = self._executors[name]
                if callable(executor):
                    import inspect
                    if inspect.iscoroutinefunction(executor):
                        return await executor(**args)
                    return executor(**args)
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return {"error": str(e)}
        return {"status": "dispatched_to_client", "action": name, "args": args}

# Singleton Global Tool Registry
tool_registry = ToolRegistry()

# Register standard voice AI client-side actions
tool_registry.register(
    name="navigate_pages",
    description="Navigates user to a page inside the web application.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Target page path (e.g. /profile, /dashboard, /search, /places)"}
        },
        "required": ["path"]
    },
    is_client_side=True
)

tool_registry.register(
    name="open_profile",
    description="Opens the user profile drawer or page.",
    parameters={"type": "object", "properties": {}},
    is_client_side=True
)

tool_registry.register(
    name="search_hotels",
    description="Searches hotels in a target destination with optional dates and budget.",
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City or landmark name"},
            "check_in": {"type": "string"},
            "check_out": {"type": "string"},
            "max_price": {"type": "number"}
        },
        "required": ["location"]
    },
    is_client_side=False,
    executor=lambda location, check_in=None, check_out=None, max_price=None: {
        "status": "success",
        "results": [
            {"id": "h1", "name": f"Royal Hotel {location}", "rating": 4.8, "price_per_night": 2500},
            {"id": "h2", "name": f"Heritage Stay {location}", "rating": 4.5, "price_per_night": 1800}
        ]
    }
)

tool_registry.register(
    name="create_itinerary",
    description="Creates a customized travel itinerary for a destination.",
    parameters={
        "type": "object",
        "properties": {
            "destination": {"type": "string"},
            "days": {"type": "integer"},
            "interests": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["destination", "days"]
    },
    is_client_side=False,
    executor=lambda destination, days, interests=None: {
        "status": "success",
        "itinerary_id": "itin_991823",
        "summary": f"Created {days}-day itinerary for {destination} focusing on {interests or 'top attractions'}."
    }
)

tool_registry.register(
    name="search_nearby",
    description="Searches for nearby emergency services, medical stores, ATMs, or restaurants.",
    parameters={
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": ["medical_store", "atm", "police_station", "restaurant", "hospital"]},
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["category"]
    },
    is_client_side=True
)

tool_registry.register(
    name="fill_form",
    description="Fills input fields on active web form.",
    parameters={
        "type": "object",
        "properties": {
            "form_id": {"type": "string"},
            "field_values": {"type": "object", "description": "Key-value pair of form field names and values"}
        },
        "required": ["field_values"]
    },
    is_client_side=True
)

tool_registry.register(
    name="generate_pdf",
    description="Generates downloadable PDF trip itinerary summary.",
    parameters={
        "type": "object",
        "properties": {
            "trip_id": {"type": "string"}
        },
        "required": ["trip_id"]
    },
    is_client_side=True
)
