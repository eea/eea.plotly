"""Plotly prompts - reference for agent configuration.

These prompts are kept for reference when configuring agents in the control panel.
Copy the relevant parts into your agent's system_prompt.
"""

PLOTLY_SYSTEM_PROMPT = """\
You are a data visualization expert. You will receive a JSON object
containing a Plotly.js chart and metadata. The JSON follows the Plotly.js
specification: `data` contains trace objects (type, x, y, name, etc.),
`layout` contains axis definitions and titles, and `dataSources` contains
the raw dataset columns.
Produce a 3-8 sentence plain prose description that combines accessibility
information (chart type, axes, data ranges) with analytical insights
(trends, outliers, key takeaways). Do not use bullet points or markdown.
Write in a clear, informative style suitable for screen readers and
general audiences."""

# Layout keys that are purely cosmetic and don't help the LLM understand the chart.
# Semantically meaningful keys (barmode, showlegend, shapes, etc.) are kept.
IRRELEVANT_LAYOUT_KEYS = {
    "paper_bgcolor",
    "plot_bgcolor",
    "font",
    "margin",
    "autosize",
    "hovermode",
    "hoverlabel",
    "dragmode",
    "separators",
    "hidesources",
    "legend",
    "colorway",
    "template",
    "modebar",
    "transition",
    "clickmode",
    "selectdirection",
    "newshape",
    "activeshape",
    "uniformtext",
    "waterfallgap",
    "waterfallgroupgap",
    "piecolorway",
    "extendpiecolors",
    "sunburstcolorway",
    "extendsunburstcolors",
    "treemapcolorway",
    "extendtreemapcolors",
    "iciclecolorway",
    "extendiciclecolors",
    "funnelgap",
    "funnelgroupgap",
    "bargap",
    "bargroupgap",
    "boxgap",
    "boxgroupgap",
    "violingap",
    "violingroupgap",
    "width",
    "height",
    "images",
    "updatemenus",
    "sliders",
}


# Per-axis keys that leak quantitative information (year ranges, tick
# values, numeric formats). Axis identity (title, type, categoryorder) is
# qualitative and stays.
AXIS_LEAKY_KEYS = {
    "range",
    "autorange",
    "tickvals",
    "ticktext",
    "tick0",
    "dtick",
    "tickformat",
    "tickformatstops",
    "rangeslider",
    "rangeselector",
    "rangebreaks",
    "tickmode",
    "nticks",
}


def clean_layout(layout):
    """Remove irrelevant cosmetic keys and leaky axis keys from layout.

    Drops cosmetic top-level keys (see ``IRRELEVANT_LAYOUT_KEYS``) and then,
    for any ``xaxis*`` / ``yaxis*`` sub-dict, strips quantitative axis keys
    (``range``, ``tickvals``, ``tick0``, etc. — see ``AXIS_LEAKY_KEYS``)
    so prompts cannot leak year ranges or numeric tick values to agents
    that must not produce quantitative claims.
    """
    cleaned = {k: v for k, v in layout.items() if k not in IRRELEVANT_LAYOUT_KEYS}
    for key, value in list(cleaned.items()):
        if isinstance(value, dict) and (
            key.startswith("xaxis") or key.startswith("yaxis")
        ):
            cleaned[key] = {k: v for k, v in value.items() if k not in AXIS_LEAKY_KEYS}
    return cleaned
