"""Agent context providers for eea.plotly."""

import json
import logging

from eea.genai.core.interfaces import AgentContextProvider
from eea.plotly.prompts import clean_layout
from eea.plotly.utils import sanitizeVisualization

logger = logging.getLogger("eea.plotly")

# Arrays with more values than this threshold get replaced with
# statistical summaries to keep the prompt within token budget.
_ARRAY_TRUNCATION_THRESHOLD = 200


class _Source:
    """Unified accessor: properties dict overrides context attributes."""

    def __init__(self, context, properties):
        self._context = context
        self._properties = properties

    def __getattr__(self, name):
        if name in self._properties:
            return self._properties[name]
        return getattr(self._context, name, None)


class PlotlyVisualizationProvider(AgentContextProvider):
    """Extracts Plotly chart data and adds it to the user prompt.

    Reads deps.context.visualization, cleans cosmetic layout keys,
    and truncates large data arrays to statistical summaries while
    preserving the full Plotly JSON structure.
    """

    name = "plotly_visualization"
    description = "Adds Plotly chart structure and data to the user prompt"

    def user_prompt(self, deps):
        context = getattr(deps, "context", None)
        properties = getattr(deps, "properties", None) or {}

        if context is None:
            return ""

        source = _Source(context, properties)

        viz = getattr(source, "visualization", None)
        if not viz or not isinstance(viz, dict):
            return ""

        prepared = prepare_visualization(viz)
        if not prepared:
            return ""

        viz_json = json.dumps(prepared, indent=2, default=str)
        return f"### Plotly visualization\n\n```json\n{viz_json}\n```"


def prepare_visualization(viz):
    """Return a cleaned copy of the visualization JSON.

    1. Normalizes via sanitizeVisualization() for backward compat.
    2. Cleans cosmetic layout keys via clean_layout().
    3. Truncates large data arrays (>200 values) to statistical summaries.
    """
    normalized = sanitizeVisualization(viz)
    data = normalized.get("data", [])
    layout = normalized.get("layout", {})
    data_sources = normalized.get("dataSources", {})

    if not data and not data_sources:
        return None

    result = {}

    # Clean layout
    if layout:
        result["layout"] = clean_layout(layout)

    # Process traces
    if data:
        result["data"] = [_truncate_trace(trace) for trace in data]

    # Process dataSources
    if data_sources:
        result["dataSources"] = _truncate_data_sources(data_sources)

    return result


def _truncate_trace(trace):
    """Return a copy of a trace with large arrays summarized."""
    result = {}
    for key, value in trace.items():
        if isinstance(value, list) and len(value) > _ARRAY_TRUNCATION_THRESHOLD:
            result[key] = _summarize_array(value)
        else:
            result[key] = value
    return result


def _truncate_data_sources(data_sources):
    """Return a copy of dataSources with large columns summarized."""
    result = {}
    for col_name, values in data_sources.items():
        if isinstance(values, list) and len(values) > _ARRAY_TRUNCATION_THRESHOLD:
            result[col_name] = _summarize_array(values)
        else:
            result[col_name] = values
    return result


def _summarize_array(values):
    """Summarize a large array into a compact description string.

    Numeric arrays are reduced to "[N numeric values]" only. We deliberately
    omit min/max/mean and sample values so the summarizer agent cannot leak
    or hallucinate quantitative claims (its prompt forbids numbers).

    Non-numeric (categorical/date) arrays keep first/last samples and unique
    count because labels like country codes and year strings are useful
    qualitative keywords for retrieval.
    """
    n = len(values)

    numeric = [v for v in values if isinstance(v, (int, float))]
    if len(numeric) == n and n > 0:
        return f"[{n} numeric values]"

    first = values[:3]
    last = values[-3:]
    try:
        unique_count = len(set(str(v) for v in values))
    except Exception:
        unique_count = "?"

    return f"[{n} values, {unique_count} unique, first: {first}, last: {last}]"
