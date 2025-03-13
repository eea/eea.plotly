"""RestAPI enpoint @plotly GET"""
import json
import copy

from eea.plotly.interfaces import IPlotlySettings
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
import plotly.io as pio


def deepUpdate(original, update):
    """Deep update a dictionary original with another dictionary update.

    Args:
        original (dict): Dictionary to update
        update (dict): Dictionary with updates

    Returns:
        dict: Updated dictionary
    """
    for key, value in update.items():
        if isinstance(
                value, dict) and key in original and isinstance(
                original[key],
                dict):
            # If both are dictionaries, update them recursively
            deepUpdate(original[key], value)
        elif key in original:
            # If the key exists in both, update the value
            original[key] = value


@implementer(IPublishTraverse)
class PlotlyPreview(BrowserView):
    """Plotly Preview"""

    name = None

    def render(self):
        """Render"""

        chartData = copy.deepcopy(
            self.context.visualization.get("chartData", {})
        )

        if not chartData:
            self.request.response.setStatus(404)
            return {
                "message": "Visualization is not defined",
                "type": "NotFound"
            }

        if self.name:
            theme = None
            themes = api.portal.get_registry_record(
                "themes",
                interface=IPlotlySettings,
                default=[]
            )
            for t in themes:
                if t.get("id") == self.name:
                    theme = copy.deepcopy(t)
                    break
            if theme and "layout" in chartData:
                data = theme.get("data", {})
                layout = theme.get("layout", {})
                for trIndex, tr in enumerate(chartData.get("data", [])):
                    trType = tr.get("type", "")
                    if trType in data:
                        newTrIndex = min(trIndex, len(data[trType])-1)
                        newTr = data[trType][newTrIndex]
                        deepUpdate(tr, newTr)
                deepUpdate(chartData["layout"], layout)
                chartData["layout"]["template"] = theme

        fig = pio.from_json(json.dumps(chartData), skip_invalid=True)

        image_bytes = fig.to_image(format="svg")

        sh = self.request.response.setHeader

        sh(
            "Content-Type",
            "image/svg+xml"
        )
        sh("Content-Disposition", "inline; filename=%s.svg" % "x")

        return image_bytes

    def publishTraverse(self, request, name):
        """used for traversal via publisher, i.e. when using as a url"""
        self.name = name
        return self

    def __call__(self):
        """Call"""
        return self.render()
