"""RestAPI enpoint @plotly GET"""
from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from eea.plotly.interfaces import (
    IPlotlySettings,
    IPlotlyLayer
)


@implementer(IPublishTraverse)
class PlotlySettingsGet(Service):
    """Plotly Settings GET"""

    def reply(self):
        """Reply"""
        if not IPlotlyLayer.providedBy(self.request):
            return {
                "themes": [],
                "templates": []
            }

        themes = api.portal.get_registry_record(
            "themes",
            interface=IPlotlySettings,
            default=[]
        )

        templates = api.portal.get_registry_record(
            "templates",
            interface=IPlotlySettings,
            default=[]
        )

        for template in templates:
            layout = template.get(
                "visualization", {}).get(
                "chartData", {}).get(
                "layout", None)
            if layout:
                themeId = layout.get("template", {}).get("id", None)
                if not themeId and themes:
                    layout["template"] = themes[0]
                elif themeId:
                    for theme in themes:
                        if theme.get("id") == themeId:
                            layout["template"] = theme

        return {
            "themes": themes,
            "templates": templates
        }
