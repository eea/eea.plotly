"""Module where all interfaces, events and exceptions live."""
import json
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.schema import JSONField
from eea.plotly import EEAMessageFactory as _


TEMPLATES_SCHEMA = json.dumps({
    "type": "array",
    "items": {
        "type": "object",
        "properties": {}
    }
})

THEMES_SCHEMA = json.dumps({
    "type": "array",
    "items": {
        "type": "object",
        "properties": {}
    }
})


class IPlotlyLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IPlotlySettings(Interface):
    """Client settings for EEA Plotly."""
    themes = JSONField(
        title=_(u"Themes"),
        description=_(
            u"The JSON representation of plotly themes."
        ),
        schema=THEMES_SCHEMA,
        default=[],
        widget="plotly_themes",
        required=False
    )

    templates = JSONField(
        title=_(u"Templates"),
        description=_(
            u"The JSON representation of plotly templates."
        ),
        schema=TEMPLATES_SCHEMA,
        default=[],
        widget="plotly_templates",
        required=False
    )
