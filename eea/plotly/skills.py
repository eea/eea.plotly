"""Agent skills for eea.plotly."""

import logging

from eea.genai.core.interfaces import AgentSkill

logger = logging.getLogger("eea.plotly")

PLOTLY_KNOWLEDGE_PROMPT = """\
#### EEA Visualization JSON Structure

A visualization is stored as a JSON object with these top-level keys:

```json
{
  "data": [ <trace>, ... ],
  "layout": { ... },
  "dataSources": { "column_name": [values...], ... },
  "columns": [ {"key": "column_name"}, ... ]
}
```

##### dataSources and *src References

Data is stored separately in `dataSources` (a dict of column name → array of values). \
Traces reference columns via `*src` fields instead of embedding data inline:

- `xsrc` / `ysrc` — column name for x/y data (bar, scatter, line, histogram, box, violin)
- `labelssrc` / `valuessrc` — column name for labels/values (pie, sunburst, treemap)
- `parentssrc` — column name for parent hierarchy (sunburst, treemap)
- `latsrc` / `lonsrc` — column name for latitude/longitude (scattergeo, scattermapbox)
- `textsrc` — column name for text/hover labels
- `marker.colorsrc` / `marker.sizesrc` — column name for marker color/size encoding
- `header.valuessrc` / `cells.valuessrc` — column names for table header/cells
- `locationssrc` — column name for geographic locations (choropleth)

When `xsrc` is set, the `x` array is also populated with the same data (dereferenced). \
Both must be present. The `*src` field is the authoritative reference; inline arrays are \
the dereferenced copy.

Each trace includes a `meta.columnNames` object mapping trace properties to their \
source column names for traceability:

```json
{
  "type": "bar",
  "xsrc": "Country",
  "ysrc": "Emissions",
  "x": ["Germany", "France", "Poland"],
  "y": [750, 420, 380],
  "meta": {
    "columnNames": {
      "x": "Country",
      "y": "Emissions"
    }
  }
}
```

The `columns` array lists all available data columns:
```json
"columns": [{"key": "Country"}, {"key": "Emissions"}]
```

##### Trace Types and Key Properties

**Basic charts:**
- `scatter` — xsrc, ysrc, mode ("lines", "markers", "lines+markers", "lines+text"), \
name, marker, line, fill, stackgroup, hovertemplate
- `bar` — xsrc, ysrc, name, orientation ("v" or "h"), marker, hovertemplate. \
Use layout.barmode for grouping ("group", "stack", "relative")
- `pie` — labelssrc, valuessrc, hole (0-1 for donut), textinfo, textposition, direction
- `histogram` — xsrc (or ysrc), nbinsx, histfunc, cumulative

**Statistical:**
- `box` — ysrc (or xsrc), name, boxmean, quartilemethod
- `violin` — ysrc (or xsrc), name, box.visible, meanline.visible

**Maps:**
- `choropleth` — locationssrc, zsrc, locationmode, colorscale, textsrc
- `scattergeo` — latsrc, lonsrc, textsrc, marker, mode
- `scattermapbox` — latsrc, lonsrc, textsrc, marker (color, size, colorsrc, sizesrc). \
Requires layout.mapbox.style (e.g. "open-street-map")

**Hierarchical:**
- `sunburst` — labelssrc, parentssrc, valuessrc, branchvalues ("total"), textinfo
- `treemap` — labelssrc, parentssrc, valuessrc, branchvalues, textinfo

**Flow:**
- `sankey` — node.labelsrc, node.colorsrc, link.sourcesrc, link.targetsrc, link.valuesrc

**Specialized:**
- `indicator` — value, mode ("number+delta+gauge"), delta, gauge
- `waterfall` — xsrc, ysrc, measuresrc
- `funnel` — xsrc, ysrc, textinfo
- `table` — header.valuessrc, cells.valuessrc
- `heatmap` — zsrc (array of column references for 2D data), xsrc, ysrc, colorscale

##### Transforms

Traces can include `transforms` for sorting or filtering data:
```json
"transforms": [{
  "type": "sort",
  "order": "descending",
  "targetsrc": "Value",
  "meta": { "columnNames": { "target": "Value" } }
}]
```

##### Layout Key Properties

- `title` — {text, font, x, y, subtitle: {text, font}}
- `xaxis` / `yaxis` — {title: {text, font, standoff}, type ("linear"|"log"|"date"|"category"), \
range, tickformat, autorange, showgrid, showline, zeroline, exponentformat, domain, anchor}
- Multiple axes: `xaxis2`, `yaxis2`, etc. with `anchor` and `overlaying` properties
- `barmode` — "group", "stack", "relative", "overlay"
- `showlegend` — boolean
- `legend` — {orientation, x, y, font, traceorder}
- `annotations` — array of {text, x, y, xref, yref, showarrow, font, align}
- `shapes` — array of {type ("rect"|"line"|"circle"), x0, y0, x1, y1, fillcolor, opacity}
- `mapbox` — {style: "open-street-map", center: {lat, lon}, zoom}
- `margin` — {t, b, l, r, pad}
- `template` — the site theme object

##### Hover Templates

`hovertemplate` supports these variables:
- `%{x}`, `%{y}`, `%{z}` — data values
- `%{text}` — text array values
- `%{data.name}` — trace name
- `%{label}`, `%{value}`, `%{percent}` — for pie/sunburst
- `%{marker.color}`, `%{marker.size}` — marker values
- `<extra></extra>` — hides the trace name box

Examples: `"%{x} $%{y}M"`, `"%{y}% - %{data.name}"`, `"%{label} - %{value}<extra></extra>"`

##### Common Trace Properties

All traces support:
- `name` — legend label for this trace
- `hoverinfo` — "x+y", "text", "none", etc.
- `hoverlabel` — {namelength: 0} to hide trace name in hover
- `hovertemplate` — formatted hover text (overrides hoverinfo)
- `visible` — true, false, or "legendonly"
- `showlegend` — boolean (per-trace)

##### Structural Requirements

1. Every trace has both `*src` references and dereferenced inline data arrays.
2. Every trace has `meta.columnNames` mapping properties to column names.
3. `dataSources` contains all columns referenced by traces.
4. `columns` lists all column keys.
"""


class PlotlyKnowledgeSkill(AgentSkill):
    """Adds Plotly JSON structure knowledge to the system prompt.

    Pure structural reference for the EEA visualization JSON format.
    Used by both interpretation (summarizer) and generation agents.
    """

    name = "plotly_knowledge"
    description = "Adds Plotly.js chart structure knowledge to the system prompt"

    def system_prompt(self, deps):
        return PLOTLY_KNOWLEDGE_PROMPT
