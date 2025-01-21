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

        import pdb
        pdb.set_trace()

        if not IPlotlyLayer.providedBy(self.request):
            return {
                "templates": []
            }

        return {
            "templates": api.portal.get_registry_record(
                "templates",
                interface=IPlotlySettings,
                default=[],
            )
        }
