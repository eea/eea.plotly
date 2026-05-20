"""Chart generation using agent system."""

import logging

from plone import api

from eea.genai.core.agent import AgentDeps
from eea.genai.core.utils import get_executor
from eea.plotly.controlpanel import IPlotlySettings

logger = logging.getLogger("eea.plotly")


def generate_chart(prompt, data_sources=None, context=None, request=None):
    """Generate a full visualization content from a natural language description."""
    deps = AgentDeps(
        context=context, request=request, data_sources=data_sources or None
    )
    result = get_executor().run_with_agent(
        "plotly_generator", user_prompt=prompt, deps=deps
    )
    _inject_theme(result)
    return result.model_dump()


def _inject_theme(result):
    """Replace __ACTIVE_THEME__ placeholder with the actual theme object."""
    layout = result.visualization.layout
    if layout.get("template") != "__ACTIVE_THEME__":
        return

    theme = _get_active_theme()
    if theme is None:
        logger.warning("No active theme found; removing template placeholder")
        layout.pop("template", None)
        return

    result.visualization.layout["template"] = theme


def _get_active_theme():
    """Return the first non-hidden theme from the Plotly control panel."""
    try:
        themes = api.portal.get_registry_record(
            "themes", interface=IPlotlySettings, default=[]
        )
    except Exception:
        return None

    for theme in themes:
        if not theme.get("hidden"):
            return theme
    return None
