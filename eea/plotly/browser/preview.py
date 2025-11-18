"""RestAPI enpoint @plotly GET"""

import copy
import json
import plotly.io as pio
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
from eea.plotly.controlpanel import IPlotlySettings
from eea.plotly.utils import sanitizeVisualization
from eea.plotly.io_json import JSONEncoder

from .preview_adapter.adapter import get_preview_adapter


def deepUpdate(original, update):
    """Recursively update a dictionary with another dictionary."""
    for key, value in update.items():
        if (
            isinstance(value, dict)
            and key in original
            and isinstance(original[key], dict)
        ):
            deepUpdate(original[key], value)
        elif key in original:
            original[key] = value


@implementer(IPublishTraverse)
class PlotlyPreview(BrowserView):
    """Plotly Preview"""

    visualization = None
    name = None
    width = 1200
    height = 900

    def render(self):
        """Render"""

        self.visualization = copy.deepcopy(
            sanitizeVisualization(self.context.visualization)
        )

        if not self.visualization:
            self.request.response.setStatus(404)
            return {"message": "Visualization is not defined", "type": "NotFound"}

        if self.name:
            theme = None
            themes = api.portal.get_registry_record(
                "themes", interface=IPlotlySettings, default=[]
            )
            for t in themes:
                if t.get("id") == self.name:
                    theme = copy.deepcopy(t)
                    break
            if theme and "layout" in self.visualization:
                data = theme.get("data", {})
                layout = theme.get("layout", {})
                for trIndex, tr in enumerate(self.visualization.get("data", [])):
                    trType = tr.get("type", "")
                    if trType in data:
                        newTrIndex = min(trIndex, len(data[trType]) - 1)
                        newTr = data[trType][newTrIndex]
                        deepUpdate(tr, newTr)
                deepUpdate(self.visualization["layout"], layout)
                self.visualization["layout"]["template"] = theme

        get_preview_adapter(self, self.name)

        fig = pio.from_json(
            json.dumps(self.visualization, cls=JSONEncoder), skip_invalid=True
        )

        if "template" not in self.visualization["layout"]:
            fig.update_layout(template=None)

        image = fig.to_image(format="svg", width=self.width, height=self.height)

        sh = self.request.response.setHeader

        sh("Content-Type", "image/svg+xml")
        sh("Content-Disposition", "inline; filename=%s.svg" % "x")

        return image

    def publishTraverse(self, request, name):
        """used for traversal via publisher, i.e. when using as a url"""
        self.name = name
        self.width = int(request.form.get("width", self.width))
        self.height = int(request.form.get("height", self.height))
        return self

    def __call__(self):
        """Call"""
        return self.render()
