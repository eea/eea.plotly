# pylint: disable=old-style-class
""" block-related utils """

from AccessControl import Unauthorized
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import (
    ISerializeToJson,
    IBlockFieldSerializationTransformer
)
from plone.restapi.serializer.utils import uid_to_url
from zExceptions import Forbidden
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from eea.plotly.serializer.utils import getUid, getProperties, getVisualization
from eea.plotly.utils import isExpanded, getLinkHTML


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class EmbedVisualizationSerializationTransformer:
    """Embed visualization serialization transformer"""

    order = 9999
    block_type = "embed_visualization"
    title = "Chart (Interactive)"
    state = {}
    error = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        self.init(value)

        url = uid_to_url(self.state.get("url"))
        doc_json = self.state.get("doc_json")

        value["vis_url"] = url

        if self.error:
            return {
                **value,
                "visualization": {
                    "error": self.error
                }
            }

        if 'visualization' in value:
            del value['visualization']

        if not doc_json:
            return value

        response = {
            **value,
            "properties": self.state["properties"]
        }

        if isExpanded(self.request):
            response["visualization"] = getVisualization(context=doc_json)

        return response

    def init(self, value):
        """ Init """
        self.state = {}
        self.state["url"] = value.get("vis_url")

        if not self.state["url"]:
            return

        self.state["uid"] = getUid(self.context, self.state["url"])
        self.state["doc"] = self.get_doc()
        self.state["doc_json"] = self.get_doc_json()

        if not self.state["doc_json"]:
            return

        self.state["properties"] = {
            **getProperties(self.state["doc_json"]),
            "@type": self.state["doc_json"].get("@type"),
            "UID": self.state["doc_json"].get("UID")
        }

    def get_doc(self):
        """Get doc"""
        url = self.state["url"]
        uid = self.state["uid"]
        try:
            return api.content.get(UID=uid)
        except Unauthorized:
            self.error = "Apologies, it seems this " + getLinkHTML(
                url, self.title) + " has not been published yet."
            return None

        except Forbidden:
            self.error = "Apologies, it seems you do not have " + \
                "permissions to see this " + getLinkHTML(url, self.title) + \
                "."
            return None

    def get_doc_json(self):
        """Get document json"""
        doc = self.state["doc"]
        if not doc:
            return None
        serializer = queryMultiAdapter(
            (doc, self.request), ISerializeToJson)
        if not serializer:
            return None
        return serializer(
            version=self.request.get("version"))


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class PlotlyChartSerializationTransformer:
    """Plotly chart serializer"""

    order = 9999
    block_type = "plotly_chart"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return value
