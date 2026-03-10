"""Tool-Registrierung und Discovery für den Agent Core."""

from typing import Callable

import structlog

log = structlog.get_logger()


class BaseTool:
    """Basisklasse für alle Agent-Tools."""

    name: str = ""
    description: str = ""
    input_schema: dict = {}

    async def execute(self, **kwargs) -> dict:
        """Führt das Tool aus. Muss von Subklassen implementiert werden."""
        raise NotImplementedError


class ToolRegistry:
    """
    Registriert und verwaltet alle verfügbaren Tools.

    Jeder Agent registriert seine eigenen Tools beim Start.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Registriert ein Tool."""
        self._tools[tool.name] = tool
        log.debug("tool_registry.registered", tool=tool.name)

    def get(self, name: str) -> BaseTool | None:
        """Gibt ein Tool anhand des Namens zurück."""
        return self._tools.get(name)

    def get_definitions(self) -> list[dict]:
        """Gibt alle Tool-Definitionen im Claude-Format zurück."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    @property
    def names(self) -> list[str]:
        """Gibt alle registrierten Tool-Namen zurück."""
        return list(self._tools.keys())
