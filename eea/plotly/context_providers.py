"""Agent context providers for eea.plotly."""

import json
import logging

from eea.genai.core.interfaces import Enricher
from eea.genai.core.utils import Source
from eea.plotly.prompts import clean_layout
from eea.plotly.utils import sanitizeVisualization

logger = logging.getLogger("eea.plotly")

# Arrays with more values than this threshold get replaced with
# statistical summaries to keep the prompt within token budget.
_ARRAY_TRUNCATION_THRESHOLD = 200


class PlotlyVisualizationProvider(Enricher):
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

        source = Source(context, properties)

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


def _is_numeric_list(values):
    """True if every element is a real number (ints/floats, not bool)."""
    if not values:
        return False
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)


def _looks_like_year_strings(values):
    """True if strings parse as 4-digit calendar years.

    String year arrays (e.g. ["2012","2013",...]) are otherwise treated as
    categorical and would leak first/last samples through ``_summarize_array``.
    """
    if not values:
        return False
    for v in values:
        if not isinstance(v, str) or len(v) != 4 or not v.isdigit():
            return False
        n = int(v)
        if not (1800 <= n <= 2200):
            return False
    return True


def _truncate_trace(trace):
    """Return a copy of a trace with sensitive/large arrays summarized.

    Numeric arrays are always summarized (regardless of length) so raw
    values cannot reach the LLM. Year-like string arrays are also always
    summarized. Other lists pass through unless they exceed the truncation
    threshold.
    """
    result = {}
    for key, value in trace.items():
        if isinstance(value, list) and (
            _is_numeric_list(value)
            or _looks_like_year_strings(value)
            or len(value) > _ARRAY_TRUNCATION_THRESHOLD
        ):
            result[key] = _summarize_array(value)
        else:
            result[key] = value
    return result


def _truncate_data_sources(data_sources):
    """Return a copy of dataSources with sensitive/large columns summarized."""
    result = {}
    for col_name, values in data_sources.items():
        if isinstance(values, list) and (
            _is_numeric_list(values)
            or _looks_like_year_strings(values)
            or len(values) > _ARRAY_TRUNCATION_THRESHOLD
        ):
            result[col_name] = _summarize_array(values)
        else:
            result[col_name] = values
    return result


def _summarize_array(values):
    """Summarize an array into a compact description string.

    Numeric arrays → ``"[N numeric values]"``. Year-like string arrays →
    ``"[N year-like values]"``. Other arrays keep first/last samples and
    unique count because labels like country codes are useful qualitative
    keywords for retrieval.

    Quantitative details (min/max/mean) are deliberately omitted: agents
    that consume this output are instructed to avoid numeric claims, and
    summary text cannot leak what is not present.
    """
    n = len(values)

    if _is_numeric_list(values):
        return f"[{n} numeric values]"
    if _looks_like_year_strings(values):
        return f"[{n} year-like values]"

    first = values[:3]
    last = values[-3:]
    try:
        unique_count = len(set(str(v) for v in values))
    except Exception:
        unique_count = "?"

    return f"[{n} values, {unique_count} unique, first: {first}, last: {last}]"
