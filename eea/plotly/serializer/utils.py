"""block-related utils"""

import re
from plone.restapi.serializer.utils import RESOLVEUID_RE
from plone.restapi.deserializer.utils import path2uid
from eea.plotly.utils import getLink, sanitizeVisualization


def getUid(context, link, retry=True):
    """Get the UID corresponding to a given link."""

    if not link:
        return link
    match = RESOLVEUID_RE.match(link)
    if match is None:
        if not retry:
            return link
        # Alin Voinea a zis sa las asa
        return getUid(context, path2uid(context=context, link=getLink(link)), False)

    uid, _ = match.groups()
    return uid


def getProperties(context):
    """Extract properties information from context."""

    return {
        "@id": context.get("@id"),
        "title": context.get("title"),
        "description": context.get("description"),
        "publisher": context.get("publisher"),
        "geo_coverage": context.get("geo_coverage"),
        "temporal_coverage": context.get("temporal_coverage"),
        "other_organisations": context.get("other_organisations"),
        "data_provenance": context.get("data_provenance"),
        "figure_note": context.get("figure_note"),
    }


def getVisualizationLayout(viz):
    """Get visualization layout with no data"""

    if not viz.get("data"):
        return {}

    newData = viz.get("data")

    for traceIndex, trace in enumerate(newData):
        for tk in trace:
            originalColumn = re.sub("src$", "", tk)
            if tk.endswith("src") and originalColumn in trace:
                newData[traceIndex][originalColumn] = []
        if not trace.get("transforms"):
            continue
        for transformIndex, _ in enumerate(trace.get("transforms")):
            newData[traceIndex]["transforms"][transformIndex]["target"] = []

    viz["data"] = newData

    return viz


def getVisualization(context, layout=True):
    """Extract visualization information from context."""

    viz = sanitizeVisualization(context.get("visualization", None))

    if not viz:
        return {}

    return {**viz, **(getVisualizationLayout(viz) if layout else {})}
