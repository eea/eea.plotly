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

        return {
            "themes": api.portal.get_registry_record(
                "themes",
                interface=IPlotlySettings,
                default=[]
            ),
            "templates": api.portal.get_registry_record(
                "templates",
                interface=IPlotlySettings,
                default=[]
            )
        }
