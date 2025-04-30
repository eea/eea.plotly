"""RestAPI enpoint @plotly GET"""
from eea.plotly.controlpanel import IPlotlySettings
from eea.plotly.utils import sanitizeVisualization
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
import plotly.io as pio
import json
import copy


def deepUpdate(original, update):
    for key, value in update.items():
        if isinstance(
                value, dict) and key in original and isinstance(
                original[key],
                dict):
            deepUpdate(original[key], value)
        elif key in original:
            original[key] = value


@implementer(IPublishTraverse)
class PlotlyPreview(BrowserView):
    """Plotly Preview"""

    name = None

    def render(self):
        """Render"""

        visualization = copy.deepcopy(
            sanitizeVisualization(self.context.visualization)
        )

        if not visualization:
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
            if theme and "layout" in visualization:
                data = theme.get("data", {})
                layout = theme.get("layout", {})
                for trIndex, tr in enumerate(visualization.get("data", [])):
                    trType = tr.get("type", "")
                    if trType in data:
                        newTrIndex = min(trIndex, len(data[trType])-1)
                        newTr = data[trType][newTrIndex]
                        deepUpdate(tr, newTr)
                deepUpdate(visualization["layout"], layout)
                visualization["layout"]["template"] = theme

        fig = pio.from_json(json.dumps(visualization), skip_invalid=True)

        if "template" not in visualization["layout"]:
            fig.update_layout(template=None)

        image = fig.to_image(format="svg", width=1200, height=900)

        sh = self.request.response.setHeader

        sh(
            "Content-Type",
            "image/svg+xml"
        )
        sh("Content-Disposition", "inline; filename=%s.svg" % "x")

        return image

    def publishTraverse(self, request, name):
        """used for traversal via publisher, i.e. when using as a url"""
        self.name = name
        return self

    def __call__(self):
        """Call"""
        return self.render()
