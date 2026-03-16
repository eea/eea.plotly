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
        if context is None:
            return ""

        viz = getattr(context, "visualization", None)
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

    Returns a string like:
    "[200 values, min=1.5, max=99.3, mean=45.2, first: [1.5, 2.0, 3.1], last: [97.0, 98.5, 99.3]]"

    For non-numeric arrays (strings, dates):
    "[200 values, 45 unique, first: ['AT', 'BE', 'BG'], last: ['SE', 'SI', 'SK']]"
    """
    n = len(values)
    first = values[:3]
    last = values[-3:]

    # Try numeric summary
    numeric = [v for v in values if isinstance(v, (int, float))]
    if len(numeric) == n and n > 0:
        min_val = min(numeric)
        max_val = max(numeric)
        mean_val = sum(numeric) / n
        return (
            f"[{n} values, min={min_val}, max={max_val}, "
            f"mean={mean_val:.2f}, first: {first}, last: {last}]"
        )

    # Non-numeric: count unique values
    try:
        unique_count = len(set(str(v) for v in values))
    except Exception:
        unique_count = "?"

    return f"[{n} values, {unique_count} unique, first: {first}, last: {last}]"
