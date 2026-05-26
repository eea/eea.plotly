"""REST API endpoint for LLM chart generation."""

import json
import logging

from plone.restapi.services import Service

from eea.plotly.generate import generate_chart

logger = logging.getLogger("eea.plotly")


class LLMGenerateChartPost(Service):
    """POST @llm-generate-chart

    Generate a visualization content from a natural language description.

    Request:
        {
            "prompt": "Create a bar chart comparing CO2 emissions...",
            "data_sources": {"Country": [...], "Value": [...]}  // optional
        }

    Response:
        {
            "title": "CO2 Emissions by Country",
            "description": "Bar chart comparing...",
            "visualization": {
                "data": [{"type": "bar", ...}],
                "layout": {"title": {...}, ...}
            },
            "topics": ["Climate change mitigation"],
            "temporal_coverage": [2020, 2021, 2022],
            "geo_coverage": ["Europe"]
        }
    """

    def reply(self):
        body = json.loads(self.request.get("BODY", b"{}"))
        prompt = body.get("prompt", "")

        if not prompt:
            self.request.response.setStatus(400)
            return {"error": "Missing 'prompt' in request body"}

        data_sources = body.get("data_sources")

        try:
            return generate_chart(
                prompt,
                data_sources=data_sources,
                context=self.context,
                request=self.request,
            )
        except Exception as exc:
            logger.exception("Chart generation failed")
            self.request.response.setStatus(500)
            return {"error": str(exc)}
