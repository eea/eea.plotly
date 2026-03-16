"""Agent tools for eea.plotly."""

import json
import logging

from plone import api
from eea.genai.core.interfaces import AgentTool
from eea.plotly.controlpanel import IPlotlySettings

logger = logging.getLogger("eea.plotly")


class GetPlotlyTemplateTool(AgentTool):
    """Fetch a predefined chart template by label.

    Returns the full Plotly visualization JSON for the requested template,
    which can be used as a structural reference for chart generation.
    """

    name = "get_plotly_template"
    description = (
        "Fetch a predefined Plotly chart template by label. "
        "Returns the full visualization JSON (data + layout) "
        "for use as a structural reference when generating charts."
    )

    def system_prompt(self, deps):
        """List available templates so the LLM knows what to request."""
        labels = self._get_template_labels()
        if not labels:
            return ""
        labels_text = ", ".join(labels)
        return (
            f"#### Available Chart Templates\n\n"
            f"The following predefined chart templates are available: "
            f"{labels_text}.\n\n"
            f"Use the `get_plotly_template` tool to fetch the full JSON "
            f"for a template by its label. Use it as a structural reference "
            f"when generating charts. Always fetch a relevant template "
            f"before generating a chart."
        )

    def _get_template_labels(self):
        """Return visible template labels from the Plotly control panel."""
        try:
            templates = api.portal.get_registry_record(
                "templates", interface=IPlotlySettings, default=[]
            )
        except Exception:
            return []
        return [
            tmpl.get("label", "")
            for tmpl in templates
            if not tmpl.get("hidden") and tmpl.get("label")
        ]

    def execute(self, ctx, template_label: str) -> str:
        """Fetch a chart template by its label.

        Args:
            ctx: pydantic_ai RunContext.
            template_label: Label of the template to fetch
                (e.g. "Vertical Bar", "Line", "Pie").

        Returns:
            JSON string of the template's visualization, or an error message.
        """
        try:
            templates = api.portal.get_registry_record(
                "templates", interface=IPlotlySettings, default=[]
            )
        except Exception:
            return "Error: Could not read Plotly templates from control panel."

        # Find matching template (case-insensitive)
        label_lower = template_label.lower().strip()
        for tmpl in templates:
            if tmpl.get("hidden"):
                continue
            if tmpl.get("label", "").lower().strip() == label_lower:
                viz = tmpl.get("visualization", {})
                if "layout" in viz and "template" in viz["layout"]:
                    del viz["layout"]["template"]
                return json.dumps(viz, indent=2, default=str)

        # No exact match — list available templates
        available = [
            t.get("label", "")
            for t in templates
            if not t.get("hidden") and t.get("label")
        ]
        return (
            f"Template '{template_label}' not found. "
            f"Available templates: {', '.join(available)}"
        )
