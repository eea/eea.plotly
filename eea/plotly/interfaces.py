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
        "properties": {
            "label": {
                "type": "string",
                "title": _("Label"),
                "description": _("A descriptive label for the template."),
                "default": ""
            },
            "type": {
                "type": "string",
                "title": _("Type"),
                "description": _("The type of template."),
                "default": ""
            },
            "visualization": {
                "type": "object",
                "title": _("Visualization"),
                "description": _("The visualization data."),
                "properties": {
                    "chartData": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            "layout": {
                                "type": "object",
                                "properties": {}
                            },
                            "frames": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                        }
                    },
                    "use_data_sources": {
                        "type": "boolean",
                        "default": True
                    },
                    "data_source": {
                        "type": "object",
                        "properties": {}
                    },
                    "provider_url": {
                        "type": "string",
                        "default": ""
                    }
                },
                "default": {
                    "chartData": {
                        "data": [],
                        "layout": {},
                        "frames": []
                    },
                    "use_data_sources": True
                }
            }
        }
    }
})


class IPlotlyLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IPlotlySettings(Interface):
    """Client settings for EEA Plotly."""
    templates = JSONField(
        title=_(u"Templates"),
        description=_(
            u"The JSON representation of plotly templates."
        ),
        schema=TEMPLATES_SCHEMA,
        default=[],
        widget="plotly_templates",
        required=True
    )
