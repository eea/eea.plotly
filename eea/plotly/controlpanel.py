"""Plotly Controlpanel API"""

import json
from zope.interface import Interface
from zope.component import adapter
from plone.schema import JSONField
from plone.restapi.controlpanels import RegistryConfigletPanel
from eea.plotly.interfaces import IPlotlyLayer
from eea.plotly import EEAMessageFactory as _

TEMPLATES_SCHEMA = json.dumps(
    {"type": "array", "items": {"type": "object", "properties": {}}}
)

THEMES_SCHEMA = json.dumps(
    {"type": "array", "items": {"type": "object", "properties": {}}}
)


class IPlotlySettings(Interface):
    """Client settings for EEA Plotly."""

    themes = JSONField(
        title=_("Themes"),
        description=_("The JSON representation of plotly themes."),
        schema=THEMES_SCHEMA,
        default=[],
        widget="plotly_themes",
        required=False,
    )

    templates = JSONField(
        title=_("Templates"),
        description=_("The JSON representation of plotly templates."),
        schema=TEMPLATES_SCHEMA,
        default=[],
        widget="plotly_templates",
        required=False,
    )


@adapter(Interface, IPlotlyLayer)
class PlotlyControlpanel(RegistryConfigletPanel):
    """Plotly Control Panel"""

    schema = IPlotlySettings
    schema_prefix = None
    configlet_id = "plotly"
    configlet_category_id = "Products"
    title = "Plotly Settings"
    group = "Products"
    data = {"themes": [], "templates": []}
