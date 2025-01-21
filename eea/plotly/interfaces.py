"""Module where all interfaces, events and exceptions live."""
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.schema import JSONField
from eea.plotly import EEAMessageFactory as _

import json

VISUALIZATION_SCHEMA = json.dumps({
    "type": "object",
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
    }
})


class IPlotlyLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ITemplateSchema(Interface):
    """Schema for individual template item."""
    label = schema.TextLine(
        title=_(u"Label"),
        description=_(u"A descriptive label for the template."),
        required=True,
    )
    type = schema.TextLine(
        title=_(u"Type"),
        description=_(u"The type of template."),
        required=True,
    )
    visualization = JSONField(
        title="Visualization",
        description="The JSON representation of the visualization information. Must be a JSON object.",  # noqa
        schema=VISUALIZATION_SCHEMA,
        default={
            "chartData": {
                "data": [],
                "layout": {},
                "frames": []
            },
            "use_data_sources": True
        },
        required=False,
    )


class IPlotlySettings(Interface):
    """Client settings for EEA Plotly."""
    templates = schema.List(
        title=_(u"Templates"),
        description=_(
            u"Templates to be used for constructing plotly charts."
        ),
        value_type=schema.Object(
            title=_(u"Template"),
            schema=ITemplateSchema,
        ),
        required=True,
    )
