"""Chart generation using agent system."""

import logging

from plone import api
from zope.component import queryUtility

from eea.genai.core.interfaces import IAgentExecutor
from eea.genai.core.agent import AgentDeps
from eea.plotly.controlpanel import IPlotlySettings

logger = logging.getLogger("eea.plotly")


def generate_chart(prompt, data_sources=None, context=None, request=None):
    """Generate a full visualization content from a natural language description.

    Uses the ZCML-registered 'plotly_generator' agent (overridable via
    control panel).

    Args:
        prompt: Natural language description of the chart to create.
        data_sources: Optional dict of column_name -> values.
        context: Optional content object for context.
        request: Optional HTTP request.

    Returns:
        dict with title, description, visualization (data + layout),
        topics, temporal_coverage, and geo_coverage.
    """
    executor = _get_agent_executor()
    deps = AgentDeps(context=context, request=request)

    if data_sources:
        deps.data_sources = data_sources

    result = executor.run_with_agent(
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


def _get_agent_executor():
    """Get the agent executor utility."""
    executor = queryUtility(IAgentExecutor)
    if executor is None:
        raise RuntimeError("No IAgentExecutor utility registered")
    return executor
